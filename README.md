# FastAPI 2F

Simple feature flag service built with FastAPI. Nothing fancy, just a working implementation for learning and experimentation.

This project was built using:

- FastAPI + Uvicorn for the web service
- Redis pr ElastiCache for caching
- AWS SSM Parameter Store for persistence
- Pydantic for data validation
- Loguru for logging

## What it does

- Create and manage feature flags
- Roll out features gradually (percentage-based, user lists, or all users)
- Cache flags in Redis for speed
- Store flags in AWS SSM Parameter Store for persistence

```sh
Request → Check Redis → If miss, get from SSM → Store in Redis → Response
```

![Project infra on AWS EKS](./assets/2f-eks-infra.png)

## How to Run

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Install and run using UV
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Or with pip
cd app && pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see the API docs.

## Basic usage

```bash
# Create a flag
curl -X POST http://localhost:8000/api/v1/flags \
  -H "Content-Type: application/json" \
  -d '{"key": "new_feature", "enabled": true, "rules": {"strategy": "percentage", "percentage": 50}}'

# Check if enabled for a user
curl "http://localhost:8000/api/v1/flags/new_feature/evaluate?user_id=user123"
```

<!-- ## Project structure

```sh
app/                    # FastAPI application
├── api/v1/            # API endpoints
├── services/          # Business logic
├── models/            # Data models
├── core/              # Redis/AWS clients
└── tests/             # Test suite

cdk/                   # AWS infrastructure (optional)
├── eks_stack.py       # EKS cluster setup
└── app.py             # CDK app

infra/k8s/             # Kubernetes manifests (optional)
``` -->

## Running tests

```bash
uv run pytest app/tests/ -v
```

## Deployment options

### Local development

Just run it with uvicorn. Redis is optional but recommended.

### AWS EKS

There's CDK code to set up an EKS cluster if you want to try that. See `cdk/` directory.

### Docker

```bash
$ docker build -f infra/docker/Dockerfile -t 2f .
$ docker run -p 8000:8000 2f

or

$ cd infra/docker && docker-compose up -d --build
```

## Configuration

Copy `app/.env.example` to `app/.env` and adjust settings:

- `REDIS_ENABLED=true` to use Redis caching
- `SSM_ENABLED=true` to use AWS SSM for persistence
- Set AWS credentials if using SSM

## API endpoints

- `GET /health/ready` - Health check
- `POST /api/v1/flags` - Create flag
- `GET /api/v1/flags` - List flags
- `GET /api/v1/flags/{key}` - Get flag
- `GET /api/v1/flags/{key}/evaluate?user_id=X` - Evaluate flag

See [`app/FEATURE_FLAGS.md`](./app/FEATURE_FLAGS.md) for detailed API docs.

## Future improvements

This project may be expanded to explore different deployment environments, infrastructure-as-code approaches, and cloud providers. Future work includes running the service on Docker and Kubernetes, managing infrastructure with Terraform and AWS CDK, and deploying primarily on AWS with an eye toward portability across clouds. The main goal is learning and experimentation, not completeness.

Todo:

- [x] Improve environment separation (local / staging / production)
- [x] Add Docker Compose setup for local development
- [ ] Add AWS Lambda deployment option
- [ ] Manage infrastructure using Terraform
- [ ] Explore multi-cloud portability (AWS-first)
