# CXRaide Security Guide

## Managing Credentials and Secrets

The backend now runs statelessly and does not require a database connection. Only a few secrets remain relevant (for example `SECRET_KEY`).

### Principles

1. **Never commit secrets to Git**
  - Keep `.env` files local; they are ignored by Git
2. **Use environment variables**
  - Define values such as `SECRET_KEY` via deployment platform secrets or local `.env`
3. **Rotate quickly if leaked**
  - Replace the secret, remove it from history (e.g., with BFG), and redeploy

### Minimal `.env` example (optional)

Place in `server/.env` if you want to override defaults:

```
SECRET_KEY=your_secure_random_key
USE_MOCK_MODELS=false
```

### Checklist

- Audit commits for accidental secrets before pushing
- Prefer platform secret stores instead of hardcoding values
- Keep local `.env` files out of backups shared with others

Remember: Security is everyone's responsibility. When in doubt, err on the side of caution.