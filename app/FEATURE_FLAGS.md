# Feature Flag Service API

## Architecture

```
Request → FastAPI → Service Layer → Cache (Redis) → SSM Parameter Store
                                    ↓
                                 Response
```

## API Endpoints

### Create Feature Flag

```bash
POST /api/v1/flags
Content-Type: application/json

{
  "key": "new_checkout_flow",
  "enabled": true,
  "description": "New checkout flow redesign",
  "rules": {
    "strategy": "percentage",
    "percentage": 25
  },
  "metadata": {
    "team": "checkout",
    "jira": "PROJ-123"
  }
}
```

### List All Flags

```bash
GET /api/v1/flags
```

### Get Single Flag

```bash
GET /api/v1/flags/new_checkout_flow
```

### Update Flag

```bash
PUT /api/v1/flags/new_checkout_flow
Content-Type: application/json

{
  "enabled": true,
  "rules": {
    "strategy": "percentage",
    "percentage": 50
  }
}
```

### Delete Flag

```bash
DELETE /api/v1/flags/new_checkout_flow
```

### Evaluate Flag (POST)

```bash
POST /api/v1/flags/evaluate
Content-Type: application/json

{
  "key": "new_checkout_flow",
  "user_id": "user123",
  "context": {
    "country": "US",
    "plan": "premium"
  }
}
```

### Evaluate Flag (GET)

```bash
GET /api/v1/flags/new_checkout_flow/evaluate?user_id=user123
```

## Rollout Strategies

### 1. All Users

Enable for all users:

```json
{
  "strategy": "all"
}
```

### 2. Percentage Rollout

Enable for X% of users (consistent per user):

```json
{
  "strategy": "percentage",
  "percentage": 25
}
```

### 3. User List

Enable for specific users:

```json
{
  "strategy": "user_list",
  "user_ids": ["user1", "user2", "user3"]
}
```

## Configuration

Environment variables:

```bash
# Redis (for caching)
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# AWS SSM (for persistence)
SSM_ENABLED=true
AWS_REGION=us-east-1
SSM_PREFIX=/feature-flags

# Cache TTL (seconds)
FEATURE_FLAG_CACHE_TTL=300
```

## Examples

### Example 1: Gradual Rollout

```bash
# Create flag at 10%
curl -X POST http://localhost:8000/api/v1/flags \
  -H "Content-Type: application/json" \
  -d '{
    "key": "new_ui",
    "enabled": true,
    "description": "New UI redesign",
    "rules": {
      "strategy": "percentage",
      "percentage": 10
    }
  }'

# Increase to 25%
curl -X PUT http://localhost:8000/api/v1/flags/new_ui \
  -H "Content-Type: application/json" \
  -d '{
    "rules": {
      "strategy": "percentage",
      "percentage": 25
    }
  }'

# Increase to 50%
curl -X PUT http://localhost:8000/api/v1/flags/new_ui \
  -H "Content-Type: application/json" \
  -d '{
    "rules": {
      "strategy": "percentage",
      "percentage": 50
    }
  }'

# Enable for all
curl -X PUT http://localhost:8000/api/v1/flags/new_ui \
  -H "Content-Type: application/json" \
  -d '{
    "rules": {
      "strategy": "all"
    }
  }'
```

### Example 2: Beta Testing

```bash
# Create flag for beta users
curl -X POST http://localhost:8000/api/v1/flags \
  -H "Content-Type: application/json" \
  -d '{
    "key": "beta_feature",
    "enabled": true,
    "description": "Beta feature for selected users",
    "rules": {
      "strategy": "user_list",
      "user_ids": ["beta_user_1", "beta_user_2", "beta_user_3"]
    }
  }'

# Evaluate for beta user
curl "http://localhost:8000/api/v1/flags/beta_feature/evaluate?user_id=beta_user_1"

# Evaluate for regular user
curl "http://localhost:8000/api/v1/flags/beta_feature/evaluate?user_id=regular_user"
```

### Example 3: Kill Switch

```bash
# Create enabled flag
curl -X POST http://localhost:8000/api/v1/flags \
  -H "Content-Type: application/json" \
  -d '{
    "key": "payment_gateway_v2",
    "enabled": true,
    "description": "New payment gateway",
    "rules": {
      "strategy": "all"
    }
  }'

# Disable immediately if issues found
curl -X PUT http://localhost:8000/api/v1/flags/payment_gateway_v2 \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

## Response Examples

### Evaluation Result

```json
{
  "key": "new_checkout_flow",
  "enabled": true,
  "matched_rule": "percentage_25",
  "source": "cache"
}
```

### Flag Object

```json
{
  "key": "new_checkout_flow",
  "enabled": true,
  "description": "New checkout flow redesign",
  "rules": {
    "strategy": "percentage",
    "percentage": 25,
    "user_ids": null,
    "custom_rules": null
  },
  "metadata": {
    "team": "checkout",
    "jira": "PROJ-123"
  },
  "created_at": "2024-01-16T10:00:00Z",
  "updated_at": "2024-01-16T10:30:00Z"
}
```

## Local Development (Without AWS)

For local development without AWS SSM:

```bash
# Set SSM_ENABLED=false in .env
SSM_ENABLED=false
REDIS_ENABLED=true

# Flags will only be stored in Redis (cache)
# Good for testing, but data is not persistent
```

## Production Setup

1. Enable Redis for caching
2. Enable SSM for persistence
3. Configure IRSA for EKS pods
4. Set appropriate cache TTL

```bash
REDIS_ENABLED=true
REDIS_HOST=your-elasticache-endpoint
SSM_ENABLED=true
AWS_REGION=us-east-1
FEATURE_FLAG_CACHE_TTL=300
```
