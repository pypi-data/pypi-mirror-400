# EOG-HPO Client SDK

The official Python client for the EOG-HPO Hyperparameter Optimization Cloud Service.

## Installation

```bash
pip install eaheog
```

For visualization support:
```bash
pip install eaheog[viz]
```

## Quick Start

```python
from eaheog import EOGHPOClient

# Initialize client with your API endpoint
client = EOGHPOClient(base_url="https://your-api-gateway-url.amazonaws.com/prod")

# Authenticate
client.login()

# Define your objective function (runs on YOUR machine)
def train_model(config):
    # Your training code here
    lr = config['learning_rate']
    batch_size = int(config['batch_size'])
    
    # Train and evaluate
    score = your_training_function(lr, batch_size)
    return score

# Define search space
search_space = {
    'learning_rate': (0.0001, 0.1),
    'batch_size': (16, 256),
    'dropout': (0.0, 0.5)
}

# Run optimization
best = client.optimize(
    objective_function=train_model,
    search_space=search_space,
    n_iterations=50
)

print(f"Best config: {best['config']}")
print(f"Best score: {best['score']}")
```

## Configuration

### Method 1: Environment Variables (Recommended)
```bash
export EOGHPO_BASE_URL="https://your-api-gateway.amazonaws.com/prod"
export EOGHPO_API_KEY="your-api-key"  # Optional: set after login
```

### Method 2: Initialize with Parameters
```python
client = EOGHPOClient(
    base_url="https://your-api-gateway.amazonaws.com/prod",
    api_key="your-api-key"  # Optional
)
```

### Method 3: Configuration File
The SDK automatically saves credentials to `~/.eaheog/credentials.json` after login.

## Features

- ✅ **Cloud-based Bayesian Optimization** - Smart hyperparameter recommendations
- 💰 **Cost Estimation** - Know costs before running
- 📊 **Live Visualization** - Real-time progress tracking (with `[viz]` install)
- 🔐 **Secure Authentication** - Token-based auth with local credential storage
- 🔄 **Session Management** - Resume interrupted optimization runs
- 📁 **Export Results** - Save optimization history to CSV

## Authentication

### Sign Up
```python
client = EOGHPOClient(base_url="https://your-api-endpoint.com")
client.signup()
```

### Login
```python
client.login()  # Interactive login
```

### Logout
```python
client.logout()  # Clear stored credentials
```

## Advanced Usage

### Cost Estimation
```python
# Estimate costs before starting
estimate = client.estimate_cost(
    n_iterations=100,
    search_space=search_space
)
print(f"Estimated cost: ${estimate['estimated_cost']}")
```

### Session Management
```python
# Start a session
session_id = client.start_optimization(
    search_space=search_space,
    n_iterations=100
)

# Resume later
client.session_id = session_id
status = client.get_session_status()
```

### Export Results
```python
# Export optimization history
client.export_results("my_results.csv")
```

### Web Dashboard
```python
# View progress in browser
client.get_web_dashboard_url()
```

## Requirements

- Python >= 3.7
- requests >= 2.25.0

Optional (for visualization):
- pandas >= 1.3.0
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- ipython >= 7.0.0

## API Endpoints

The client expects your AWS API Gateway to expose these endpoints:

- `POST /auth/signup` - User registration
- `POST /auth/login` - Authentication
- `POST /estimate` - Cost estimation
- `POST /start` - Start optimization session
- `POST /job/{session_id}/next` - Get next configuration
- `POST /job/{session_id}/result` - Report result
- `GET /job/{session_id}/status` - Get session status

## Architecture

```
User's Machine                     AWS Cloud
┌─────────────────┐               ┌──────────────────┐
│                 │               │                  │
│  Your Training  │               │  API Gateway     │
│     Code        │               │                  │
│                 │               └────────┬─────────┘
└────────┬────────┘                        │
         │                                 │
         │  EOGHPOClient                   │
         │  • Get config                   ▼
         │  • Train locally         ┌──────────────┐
         │  • Report result         │   Lambda     │
         │                          │  Functions   │
         └──────────────────────────┤              │
                                    │ • auth_broker│
                                    │ • optimizer  │
                                    │ • payments   │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  Firestore   │
                                    │   Database   │
                                    └──────────────┘
```

## Security

- API keys are stored locally in `~/.eaheog/credentials.json` with restricted permissions (600)
- All API calls use HTTPS
- Bearer token authentication
- Credentials are never sent to third parties

## Troubleshooting

### Connection Errors
```python
# Verify your base URL is correct
client = EOGHPOClient(base_url="https://your-api-gateway.amazonaws.com/prod")

# Test connection
try:
    client.login()
except ConnectionError as e:
    print(f"Cannot connect: {e}")
    print("Verify your API Gateway URL is correct")
```

### Authentication Issues
```python
# Clear stored credentials and re-login
client.logout()
client.login()
```

### Timeout Errors
```python
# Increase timeout (default: 30s)
client.timeout = 60
```

## Support

- Documentation: https://docs.eaheog.com
- Website: https://www.eaheog.com
- Email: support@eaheog.com
- Issues: https://github.com/yourusername/eaheog/issues

## License

MIT License - see LICENSE file for details