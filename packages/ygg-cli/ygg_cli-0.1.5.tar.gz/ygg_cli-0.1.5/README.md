# YGG CLI

Command line interface for the [YGG platform](https://ygg.kluglabs.net).

## Installation

```bash
pip install ygg-cli
```

## Configuration

The CLI requires the `YGG_API_KEY` environment variable to be set. The API key must have `*:*:admin:*` permissions.

```bash
export YGG_API_KEY="ygg_api_..."
```

**Note:** The API base URL is always `https://ygg-api.kluglabs.net` and cannot be changed.

## Features

### List Projects and Environments

List all projects and their environments:

```bash
ygg ls
```

Output:
```
✓ proj_123 (My Project)
  └─ dev (5 vars)
  └─ prod (8 vars)
✓ proj_456 (Another Project)
  └─ staging (3 vars)
```

### Environment Management

**Export environment as .env format:**

```bash
ygg env <project_id> <env>
```

Example:
```bash
ygg env proj_123 dev
# Outputs:
# DATABASE_URL=postgres://...
# API_KEY=secret123
# REDIS_URL=redis://...
```

**Import environment from stdin:**

```bash
cat .env | ygg env <project_id> <env>
```

Example:
```bash
cat .env | ygg env proj_123 prod
```

You can also pipe environment variables directly:
```bash
echo "DATABASE_URL=postgres://localhost" | ygg env proj_123 dev
```

### Database Schema Export

Export database schema in B3 format:

```bash
ygg db <project_id> <env>
```

Example:
```bash
ygg db proj_123 dev
# Outputs B3 schema format
```

### Project Management

**Create a new project:**

```bash
ygg mkproj <project_id>
```

Example:
```bash
ygg mkproj my-new-project
```

**Rename a project:**

```bash
ygg mv <old_project_id> <new_project_id>
```

Example:
```bash
ygg mv old-project new-project
```

**Delete a project:**

```bash
ygg rm <project_id>
```

Example:
```bash
ygg rm proj_123
```

### Environment Management

**Create a new environment:**

```bash
ygg mkenv <project_id> <env>
```

Example:
```bash
ygg mkenv proj_123 staging
```

**Rename an environment:**

```bash
ygg mv <project_id> <old_env> <new_env>
```

Example:
```bash
ygg mv proj_123 dev development
```

**Delete an environment:**

```bash
ygg rm <project_id> <env>
```

Example:
```bash
ygg rm proj_123 staging
```

## Requirements

- Python 3.7+
- `requests` library (installed automatically with `ygg-cli`)

## Notes

- All computations are done in the YGG server. The Python CLI is a thin client that makes HTTP requests.
- The API key must have `*:*:admin:*` permissions to work.
- The key only works for a specific account.

## Learn More

Visit [ygg.kluglabs.net](https://ygg.kluglabs.net) for more information about the YGG platform.
