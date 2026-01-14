# client.py - EOG-HPO Client SDK
"""
EOG-HPO Client SDK
Provides intelligent hyperparameter recommendations
"""

import requests
import webbrowser
import time 
import re
import os
import json
import getpass
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

# Optional dependencies for visualization
try:
    import pandas as pd
    import numpy as np
    from IPython.display import display, HTML, clear_output
    import matplotlib.pyplot as plt
    _VISUALIZATION_AVAILABLE = True
except ImportError:
    _VISUALIZATION_AVAILABLE = False

# Configure logger
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Hyperparameter configuration"""
    params: Dict[str, float]
    config_id: str
    iteration: int

 
class EOGHPOClient:
    """
    Client for EOG-HPO recommendation service.
    Trains locally, gets recommendations from cloud.
    """
    
    # Production API endpoint - all users connect here
    DEFAULT_BASE_URL = "https://api.eaheog.com"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize EOG-HPO client
        
        Args:
            api_key: Optional API key (will prompt for login if not provided)
            base_url: Optional custom API endpoint (for testing only, defaults to production)
        """
        # Use provided URL, environment variable, or production default
        # Environment variable is mainly for internal testing
        self.base_url = (
            base_url or 
            os.environ.get("EOGHPO_BASE_URL") or 
            self.DEFAULT_BASE_URL
        )
        
        self.base_url = self.base_url.rstrip('/')
        self.session_id = None
        self.history = []
        self.current_iteration = 0
        
        # Setup persistent session with retries
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        # Set timeout for all requests
        self.timeout = 30
        
        # 1. Try provided key
        self.api_key = api_key
        
        # 2. Try Environment Variable
        if not self.api_key:
            self.api_key = os.environ.get("EOGHPO_API_KEY")
            
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})
        logger.debug(f"Initialized EOGHPOClient with base_url={self.base_url}")

    def _get_config_path(self) -> Path:
        """Returns path to local credentials file."""
        config_dir = Path.home() / ".eaheog"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "credentials.json"

    def _load_stored_api_key(self) -> Optional[str]:
        try:
            path = self._get_config_path()
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f).get('api_key')
        except Exception:
            pass
        return None

    def _save_api_key(self, api_key: str):
        try:
            path = self._get_config_path()
            with open(path, 'w') as f:
                json.dump({'api_key': api_key}, f)
            # Secure file permissions (Unix-like systems)
            try:
                os.chmod(path, 0o600)
            except:
                pass  # Windows doesn't support chmod
        except Exception as e:
            logger.warning(f"Failed to save credentials: {e}")
            print(f"⚠️ Could not save credentials locally: {e}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Unified request handler with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
            
        logger.debug(f"Request: {method} {url}")
         
        response = None
        try:
            response = self.session.request(method, url, **kwargs)
            logger.debug(f"Response: {response.status_code} {response.reason} - {response.elapsed.total_seconds():.3f}s")
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error connecting to {self.base_url}: {e}")
            raise ConnectionError(
                f"Cannot connect to EOG-HPO service at {self.base_url}. "
                f"Please check your internet connection."
            ) from e
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out: {e}")
            raise TimeoutError(
                f"Request timed out after {self.timeout}s. "
                f"The service may be experiencing high load. Please try again."
            ) from e
        except requests.exceptions.HTTPError as e:
            # Parse error message from response if available
            try:
                if response is not None:
                    error_data = response.json()
                    logger.error(f"HTTP Error details: {error_data}")
                    error_msg = (
                        error_data.get('message') or 
                        error_data.get('detail') or 
                        error_data.get('error') or 
                        str(e)
                    )
                else:
                    error_msg = str(e)
            except:
                # Fallback to text if JSON fails
                error_msg = response.text if response is not None else str(e)
            logger.error(f"API Error: {error_msg}")
            raise Exception(f"API Error: {error_msg}") from e
        
    def logout(self):
        """Logs out by clearing local credentials."""
        try:
            path = self._get_config_path()
            if path.exists():
                os.remove(path)
            self.api_key = None
            if "x-api-key" in self.session.headers:
                del self.session.headers["x-api-key"]
            logger.info("User logged out")
            print("✅ Logged out successfully.")
        except Exception as e:
            logger.error(f"Error logging out: {e}")
            print(f"❌ Error logging out: {e}")

    def signup(self):
        """Interactive sign-up helper."""
        print("=== EOG-HPO Sign Up ===")
        while True:
            email = input("Email: ").strip()
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                break
            print("❌ Invalid email format. Please try again.")
            
        password = getpass.getpass("Password: ")
        try:
            response = self._make_request(
                "POST",
                "/auth/signup",
                json={"email": email, "password": password}
            )
            logger.info(f"Signup successful for {email}")
            print("✅ Sign up successful!")
            print("⚠️  A verification link has been sent to your email. You MUST verify it before logging in.")
        except Exception as e:
            logger.error(f"Signup failed: {e}")
            print(f"❌ Sign up failed: {e}")

    def login(self):
        """Interactive authentication manager."""
        print("\n=== EOG-HPO Authentication ===")
        
        # Check for stored credentials first
        stored_key = self._load_stored_api_key()
        
        if stored_key and not self.api_key:
            print(f"🔑 Found saved credentials (Key ends in ...{stored_key[-4:]})")
            print("1. Use saved credentials")
            print("2. Log out and sign in as different user")
            print("3. Create new account")
            
            choice = input("Select option (1-3) [1]: ").strip() or '1'
            
            if choice == '1':
                self.api_key = stored_key
                logger.info("Logged in with saved credentials")
                print("✅ Logged in using saved credentials.")
                return
            elif choice == '2':
                self.logout()
            elif choice == '3':
                self.logout()
                self.signup()
        
        if not self.api_key:
            print("\n1. Log In")
            print("2. Sign Up")
            print("3. Enter API Key manually")
            choice = input("Select option (1-3) [1]: ").strip() or '1'
            
            if choice == '3':
                self.api_key = getpass.getpass("API Key: ").strip()
                if self.api_key:
                    self._save_api_key(self.api_key)
                    self.session.headers.update({"x-api-key": self.api_key})
                    print("✅ API Key saved.")
                return
            elif choice == '2':
                self.signup()
                print("\nPlease log in with your new account.")

        print("\n--- Log In ---")
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        try:
            response = self._make_request(
                "POST",
                "/auth/login",
                json={"email": email, "password": password}
            )
            data = response.json()
            self.api_key = data.get("api_key") or data.get("token")
            if not self.api_key:
                raise ValueError("No API key returned from login")
            self._save_api_key(self.api_key)
            self.session.headers.update({"x-api-key": self.api_key})
            logger.info("Login successful")
            print("✅ Login successful!")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            print(f"❌ Login failed: {e}")

    def estimate_cost(self, n_iterations: int, search_space: Dict[str, tuple], n_runs: int = 1) -> Dict:
        """
        Estimate cost before starting optimization
        
        Args:
            n_iterations: Number of configurations to try
            search_space: The search space dictionary (needed for dimension pricing)
            n_runs: Number of independent runs
            
        Returns:
            Dict with cost estimate and payment link
        """
        if not self.api_key:
            print("ℹ️  Authentication required for cost estimation.")
            self.login()
            if not self.api_key:
                print("⚠️  Proceeding without authentication (Public pricing only).")

        logger.info(f"Estimating cost for {n_iterations} iterations")
        response = self._make_request(
            "POST",
            "/estimate",
            json={
                "n_iterations": n_iterations,
                "search_space": search_space,
                "n_runs": n_runs
            }
        )
        
        result = response.json()
        print(f"💰 Estimated Cost: ${result['estimated_cost']:.2f}")
        print(f"📊 Recommendations: {result['total_recommendations']}")
        print(f"⏱️  Expected Duration: ~{result['estimated_minutes']} minutes")
        
        return result
    
    def start_optimization(
        self,
        search_space: Dict[str, tuple],
        n_iterations: int = 100,
        objective_name: str = "score",
        maximize: bool = True,
        promo_code: Optional[str] = None
    ) -> str:
        """
        Start a new optimization session
        
        Args:
            search_space: Dict mapping param names to (min, max) tuples
            n_iterations: Number of configurations to try
            objective_name: Name of the metric to optimize
            maximize: Whether to maximize (True) or minimize (False) the objective
            promo_code: Optional promotional code for discounts
            
        Returns:
            session_id: Unique identifier for this optimization session
        """
        if not self.api_key:
            print("🔐 Authentication required.")
            self.login()
            if not self.api_key:
                raise ValueError("Authentication required to start optimization")

        logger.info(f"Starting optimization: {n_iterations} iterations, objective={objective_name}")
        response = self._make_request(
            "POST",
            "/initiate",
            json={
                "search_space": search_space,
                "n_iterations": n_iterations,
                "objective_name": objective_name,
                "maximize": maximize,
                "promo_code": promo_code
            }
        )
        
        data = response.json()
        self.session_id = data["session_id"]
        logger.info(f"Session created: {self.session_id}")
        
        # Handle payment if required
        if "payment_required" in data and data["payment_required"]:
            print(f"\n💳 Payment Required: ${data['amount']:.2f}")
            print(f"🔗 Complete payment at: {data['payment_url']}")
            webbrowser.open(data['payment_url'])
            
            print("\n⏳ Waiting for payment confirmation...")
            while True:
                time.sleep(5)
                status = self.get_session_status()
                if status.get("payment_status") == "completed":
                    logger.info("Payment confirmed")
                    print("✅ Payment confirmed!")
                    break
                elif status.get("payment_status") == "failed":
                    logger.error("Payment failed")
                    raise Exception("Payment failed or was cancelled")
        
        print(f"✅ Optimization session started: {self.session_id}")
        return self.session_id
    
    def get_next_config(self) -> Optional[Config]:
        """
        Get the next configuration to evaluate
        
        Returns:
            Config object with parameters to try, or None if optimization is complete
        """
        if not self.session_id:
            raise ValueError("No active session. Call start_optimization() first")
        
        logger.debug(f"Requesting next config for session {self.session_id}")
        response = self._make_request(
            "POST",
            f"/job/{self.session_id}/next",
        )
        
        data = response.json()
        
        if data.get("status") == "complete":
            logger.info("Optimization job complete")
            print("✅ Optimization complete!")
            return None
        
        return Config(
            params=data["config"],
            config_id=data["config_id"],
            iteration=data["iteration"]
        )
    
    def report_result(self, config: Config, score: float):
        """
        Report the evaluation result for a configuration
        
        Args:
            config: The Config object that was evaluated
            score: The resulting score/metric value
        """
        logger.debug(f"Reporting result: config={config.config_id}, score={score}")
        response = self._make_request(
            "POST",
            f"/job/{self.session_id}/result",
            json={
                "config_id": config.config_id,
                "score": score
            }
        )
        
        # Store in local history
        self.history.append({
            'iteration': config.iteration,
            'config': config.params,
            'score': score
        })
        
        print(f"✅ Result reported: {score:.6f}")
    
    def optimize(
        self,
        objective_function: Callable[[Dict[str, float]], float],
        search_space: Dict[str, tuple],
        n_iterations: int = 100,
        maximize: bool = True,
        promo_code: Optional[str] = None,
        show_progress: bool = True
    ) -> Dict:
        """
        Run complete optimization loop
        
        Args:
            objective_function: Function that takes config dict and returns score
            search_space: Dict mapping param names to (min, max) tuples
            n_iterations: Number of configurations to try
            maximize: Whether to maximize (True) or minimize (False)
            promo_code: Optional promotional code
            show_progress: Whether to show live progress visualization
            
        Returns:
            Dict with best configuration and score
        """
        if not self.api_key:
            print("🔐 Authentication required.")
            self.login()
            if not self.api_key:
                raise ValueError("Authentication required")
        
        # Resume existing session or start new one
        if self.session_id:
            logger.info(f"Resuming session {self.session_id}")
            print(f"📍 Resuming session: {self.session_id}")
            self.get_session_status()
        else:
            self.start_optimization(
                search_space=search_space,
                n_iterations=n_iterations,
                promo_code=promo_code
            )
        
        print(f"\n🚀 Starting optimization for {n_iterations} iterations...\n")
        
        # Optimization loop
        for i in range(n_iterations):
            # Get next config
            config = self.get_next_config()
            if config is None:
                break
            
            print(f"📊 Iteration {config.iteration}/{n_iterations}")
            print(f"   Config: {config.params}")
            
            # Train on client machine
            print("  🔄 Training locally...")
            score = objective_function(config.params)
            
            # Report result
            self.report_result(config, score)
            
            # Update progress visualization
            if show_progress and (i % 5 == 0 or i == n_iterations - 1):
                self.show_progress()
            
            # Safety throttle
            time.sleep(0.5)
        
        # Final results
        self.print_summary()
        if not self.history:
            return {}
            
        best = max(self.history, key=lambda x: x['score'])
        
        return best
    
    def show_progress(self, in_notebook: bool = True):
        """Display live progress visualization"""
        if not _VISUALIZATION_AVAILABLE:
            print("⚠️ Visualization libraries not installed. Install with: pip install eaheog[viz]")
            return

        if not self.history:
            return
        
        df = pd.DataFrame(self.history)
        
        if in_notebook:
            clear_output(wait=True)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
            
            # Score over time
            ax1.plot(df['iteration'], df['score'], 'o-', alpha=0.6)
            ax1.plot(df['iteration'], df['score'].cummax(), 'r-', linewidth=2, label='Best')
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Score')
            ax1.set_title('Optimization Progress')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Parameter importance
            if len(self.history) > 10:
                param_vars = {}
                for param in self.history[0]['config'].keys():
                    values = [h['config'][param] for h in self.history]
                    param_vars[param] = np.var(values)
                
                ax2.barh(list(param_vars.keys()), list(param_vars.values()))
                ax2.set_xlabel('Variance (Exploration)')
                ax2.set_title('Parameter Exploration')
            
            plt.tight_layout()
            plt.show()
            
            display(HTML(f"""
            <div style='background: #f0f0f0; padding: 15px; border-radius: 8px;'>
                <h3>📊 Current Stats</h3>
                <table style='width: 100%;'>
                    <tr><td><b>Iterations:</b></td><td>{len(self.history)}/{self.current_iteration}</td></tr>
                    <tr><td><b>Best Score:</b></td><td>{df['score'].max():.6f}</td></tr>
                    <tr><td><b>Mean Score:</b></td><td>{df['score'].mean():.6f}</td></tr>
                    <tr><td><b>Std Dev:</b></td><td>{df['score'].std():.6f}</td></tr>
                </table>
            </div>
            """))
        else:
            print(f"\n{'='*60}")
            print(f"Iteration: {len(self.history)}/{self.current_iteration}")
            print(f"Best Score: {df['score'].max():.6f}")
            print(f"Mean Score: {df['score'].mean():.6f}")
            print(f"{'='*60}\n")
    
    def print_summary(self):
        """Prints a detailed summary of the optimization run."""
        if not self.history:
            print("No optimization history available.")
            return

        if not _VISUALIZATION_AVAILABLE:
            print(f"Session: {self.session_id}, Count: {len(self.history)}")
            return

        df = pd.DataFrame(self.history)
        best_run = df.loc[df['score'].idxmax()]
        
        print("\n" + "="*60)
        print("📊 OPTIMIZATION RUN SUMMARY")
        print("="*60)
        print(f"Session ID:       {self.session_id}")
        print(f"Total Iterations: {len(df)}")
        print(f"Best Score:       {best_run['score']:.6f}")
        print(f"Average Score:    {df['score'].mean():.6f}")
        print("-" * 60)
        print("🏆 Best Configuration:")
        for param, value in best_run['config'].items():
            print(f"   • {param}: {value}")
        print("-" * 60)
        self.get_web_dashboard_url()
        print("="*60 + "\n")

    def get_web_dashboard_url(self) -> str:
        """Get URL to view progress in web browser"""
        if not self.session_id:
            raise ValueError("No active session")
        
        url = f"https://www.eaheog.com/dashboard/{self.session_id}"
        print(f"🔗 View progress at: {url}")
        webbrowser.open(url)
        return url
    
    def get_session_status(self) -> Dict:
        """Get current session status"""
        response = self._make_request(
            "GET",
            f"/job/{self.session_id}/status",
        )
        return response.json()
    
    def export_results(self, filename: str = "eoghpo_results.csv"):
        """Export optimization history to CSV"""
        if not _VISUALIZATION_AVAILABLE:
            print("⚠️ pandas not installed. Install with: pip install eaheog[viz]")
            return
            
        df = pd.DataFrame(self.history)
        
        # Flatten config dict into columns
        config_df = pd.json_normalize([h['config'] for h in self.history])
        result_df = pd.concat([df[['iteration', 'score']], config_df], axis=1)
        
        result_df.to_csv(filename, index=False)
        print(f"✅ Results exported to {filename}")