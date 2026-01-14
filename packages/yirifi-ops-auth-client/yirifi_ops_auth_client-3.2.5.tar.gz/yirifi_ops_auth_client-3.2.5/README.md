# Yirifi Ops Auth Client

Authentication client library for Yirifi Ops microsites.

## Installation

### Option 1: Git Submodule (Recommended)

Add as a submodule to your project:

```bash
git submodule add git@github.com:yirifi/yirifi-ops-auth-client.git vendor/yirifi-ops-auth-client
```

Then install using the provided script:

```bash
source venv/bin/activate
./vendor/yirifi-ops-auth-client/scripts/install.sh
```

To update to the latest version:

```bash
git submodule update --remote vendor/yirifi-ops-auth-client
./vendor/yirifi-ops-auth-client/scripts/install.sh
```

### Option 2: Direct Install

```bash
pip install -e /path/to/yirifi-ops-auth-client
```

## Quick Start

### 1. Configure your Flask app

```python
from flask import Flask, g
from yirifi_ops_auth import YirifiOpsAuthClient, setup_auth_middleware

def create_app():
    app = Flask(__name__)

    # Load config
    app.config['AUTH_SERVICE_URL'] = 'http://localhost:5100'
    app.config['MICROSITE_ID'] = 'sidebyside'

    # Initialize auth client
    auth_client = YirifiOpsAuthClient(app.config['AUTH_SERVICE_URL'])

    # Setup middleware (handles authentication automatically)
    setup_auth_middleware(
        app=app,
        auth_client=auth_client,
        microsite_id=app.config['MICROSITE_ID']
    )

    return app
```

### 2. Access current user in routes

```python
from flask import g
from yirifi_ops_auth import require_auth, require_admin

@app.route('/dashboard')
@require_auth
def dashboard():
    user = g.current_user
    return f"Hello {user.display_name}!"

@app.route('/admin')
@require_admin
def admin():
    return "Admin only content"
```

### 3. Environment variables

Add to your `.env`:

```bash
AUTH_SERVICE_URL=http://localhost:5100
MICROSITE_ID=sidebyside
```

## Features

### Dual-mode Authentication

The middleware supports both:
- **Session cookies** - For browser users (automatic redirect to login)
- **API keys** - For programmatic access (returns 401 JSON response)

### Current User

After authentication, the user is available in `g.current_user`:

```python
from flask import g

user = g.current_user
print(user.id)           # User ID
print(user.email)        # Email address
print(user.display_name) # Display name
print(user.is_admin)     # True if admin
print(user.microsites)   # List of accessible microsite IDs
```

### Decorators

```python
from yirifi_ops_auth import require_auth, require_admin, require_access

@require_auth           # Requires any authenticated user
@require_admin          # Requires admin user
@require_access('ms')   # Requires access to specific microsite
```

### Excluding Paths

```python
setup_auth_middleware(
    app=app,
    auth_client=auth_client,
    microsite_id='sidebyside',
    excluded_paths=['/public'],
    excluded_prefixes=['/api/v1/health', '/static']
)
```

## API Reference

### YirifiOpsAuthClient

```python
client = YirifiOpsAuthClient(
    auth_service_url='http://localhost:5100',
    timeout=5.0,
    verify_ssl=True
)

# Verify credentials
result = client.verify(
    session_cookie='sess_...',
    api_key='yirifi_ops_...',
    microsite_id='sidebyside'
)

if result.valid:
    print(result.user.email)
else:
    print(result.error)
```

### AuthUser

```python
@dataclass
class AuthUser:
    id: int
    email: str
    display_name: str
    is_admin: bool
    microsites: list[str]

    def has_access_to(self, microsite_id: str) -> bool: ...
```

### Exceptions

- `AuthenticationError` - User not authenticated
- `AuthorizationError` - User lacks required permissions
- `AuthServiceError` - Auth service communication failure

## Migration from HTTP Basic Auth

Replace:

```python
# Old
from app.auth import check_auth, authenticate

@app.before_request
def require_auth():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
```

With:

```python
# New
from yirifi_ops_auth import YirifiOpsAuthClient, setup_auth_middleware

auth_client = YirifiOpsAuthClient(app.config['AUTH_SERVICE_URL'])
setup_auth_middleware(app, auth_client, microsite_id='your-app')
```

Remove the old `app/auth.py` file.
