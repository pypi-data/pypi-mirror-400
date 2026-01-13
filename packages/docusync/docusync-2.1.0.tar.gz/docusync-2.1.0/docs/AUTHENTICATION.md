# Authentication Guide

DocuSync supports two methods for authenticating with GitHub: **SSH** and **HTTPS with Personal Access Token (PAT)**.

## Quick Comparison

| Method | Use Case | Setup Complexity | Security |
|--------|----------|------------------|----------|
| **SSH** | Local development | Medium (one-time SSH key setup) | ✅ Very secure |
| **HTTPS + PAT** | CI/CD pipelines, automation | Low (just set env var) | ✅ Secure with proper token management |

## SSH Authentication (Default)

### When to Use
- Local development environments
- When you have SSH keys already configured with GitHub
- When you prefer not to use tokens

### Setup

1. **Generate SSH key** (if you don't have one):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. **Add SSH key to GitHub**:
- Copy your public key: `cat ~/.ssh/id_ed25519.pub`
- Go to GitHub → Settings → SSH and GPG keys
- Click "New SSH key" and paste your public key

3. **Configure DocuSync** (SSH is default, but you can be explicit):
```json
{
  "git": {
    "clone_depth": 1,
    "default_branches": ["main", "master"],
    "default_protocol": "ssh",
    "default_ssh_key_path": "~/.ssh/id_ed25519"
  }
}
```

4. **Sync your docs**:
```bash
docusync sync
```

### SSH URL Format
```
git@github.com:owner/repository.git
```

### Using Specific SSH Keys

You can specify different SSH keys for different repositories:

**Global default SSH key:**
```json
{
  "git": {
    "default_ssh_key_path": "~/.ssh/id_ed25519"
  }
}
```

**Per-repository SSH key:**
```json
{
  "repositories": [
    {
      "github_path": "acme-corp/api-gateway",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/acme_corp_key",
      ...
    },
    {
      "github_path": "partner-org/service",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/partner_org_key",
      ...
    }
  ]
}
```

**Key Priority:**
1. Repository-specific `ssh_key_path` (highest priority)
2. Global `default_ssh_key_path`
3. System default SSH key (if neither specified)

---

## HTTPS with Personal Access Token

### When to Use
- CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, etc.)
- Docker containers
- Environments where SSH is not configured
- Temporary or automated setups

### Setup

#### 1. Create a GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "DocuSync CI")
4. Select scopes:
   - ✅ `repo` (for private repositories)
   - For public repos only, you might not need any scopes
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

#### 2. Set the Token as Environment Variable

**Local development:**
```bash
# Add to your ~/.bashrc, ~/.zshrc, or equivalent
export GITHUB_PAT_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Or set temporarily for current session
export GITHUB_PAT_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**GitHub Actions:**
```yaml
- name: Sync Documentation
  env:
    GITHUB_PAT_TOKEN: ${{ secrets.GITHUB_PAT_TOKEN }}
  run: docusync sync
```

**GitLab CI:**
```yaml
sync_docs:
  variables:
    GITHUB_PAT_TOKEN: $GITHUB_PAT_TOKEN
  script:
    - docusync sync
```

**Docker:**
```bash
docker run -e GITHUB_PAT_TOKEN="ghp_xxxx" your-image
```

#### 3. Configure DocuSync

```json
{
  "git": {
    "clone_depth": 1,
    "default_branches": ["main", "master"],
    "default_protocol": "https",
    "default_pat_token_env": "GITHUB_PAT_TOKEN"
  }
}
```

#### 4. Sync your docs

```bash
docusync sync
```

### HTTPS URL Format
```
https://github.com/owner/repository.git
```

With token injected automatically:
```
https://ghp_token@github.com/owner/repository.git
```

---

## Mixed Authentication (Advanced)

### Different Protocols for Different Repositories

You can use different protocols for different repositories:

```json
{
  "repositories": [
    {
      "github_path": "acme-corp/public-docs",
      "docs_path": "docs",
      "display_name": "Public Docs",
      "position": 1,
      "description": "Public documentation",
      "protocol": "https"
    },
    {
      "github_path": "acme-corp/private-internal-docs",
      "docs_path": "docs",
      "display_name": "Internal Docs",
      "position": 2,
      "description": "Private internal documentation",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/acme_corp_key"
    }
  ],
  "git": {
    "default_protocol": "ssh",
    "default_ssh_key_path": "~/.ssh/id_ed25519",
    "default_pat_token_env": "GITHUB_PAT_TOKEN"
  }
}
```

In this example:
- `public-docs` will use HTTPS (even though default is SSH)
- `private-internal-docs` will use SSH with a specific key

### Multiple Organizations with Different SSH Keys

When working with multiple GitHub accounts/organizations via SSH:

```json
{
  "repositories": [
    {
      "github_path": "acme-corp/api-docs",
      "docs_path": "docs",
      "display_name": "ACME API",
      "position": 1,
      "description": "ACME Corp API documentation",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/acme_corp_key"
    },
    {
      "github_path": "partner-org/service-docs",
      "docs_path": "docs",
      "display_name": "Partner Service",
      "position": 2,
      "description": "Partner org service documentation",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/partner_org_key"
    },
    {
      "github_path": "my-personal/project-docs",
      "docs_path": "docs",
      "display_name": "Personal Project",
      "position": 3,
      "description": "Personal project documentation",
      "protocol": "ssh"
    }
  ],
  "git": {
    "default_protocol": "ssh",
    "default_ssh_key_path": "~/.ssh/id_ed25519",
    "clone_depth": 1,
    "default_branches": ["main", "master"]
  }
}
```

**Generate separate keys for each organization:**
```bash
# Generate key for ACME Corp
ssh-keygen -t ed25519 -f ~/.ssh/acme_corp_key -C "work@acme-corp.com"

# Generate key for Partner Org
ssh-keygen -t ed25519 -f ~/.ssh/partner_org_key -C "partner@partner-org.com"

# Default personal key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "personal@email.com"
```

**Add each key to the respective GitHub organization/account:**
1. Copy public key: `cat ~/.ssh/acme_corp_key.pub`
2. Go to GitHub (organization account) → Settings → SSH keys
3. Add the public key
4. Repeat for each organization

### Multiple Organizations with Different PAT Tokens

**This is a common real-world scenario!** When aggregating documentation from multiple organizations, each organization may require its own PAT token.

**Example Configuration:**

```json
{
  "repositories": [
    {
      "github_path": "acme-corp/api-gateway",
      "docs_path": "docs",
      "display_name": "ACME API Gateway",
      "position": 1,
      "description": "ACME Corp API gateway",
      "protocol": "https",
      "pat_token_env": "ACME_CORP_PAT_TOKEN"
    },
    {
      "github_path": "partner-org/billing-service",
      "docs_path": "docs",
      "display_name": "Partner Billing",
      "position": 2,
      "description": "Partner organization billing service",
      "protocol": "https",
      "pat_token_env": "PARTNER_ORG_PAT_TOKEN"
    },
    {
      "github_path": "my-company/internal-tools",
      "docs_path": "documentation",
      "display_name": "Internal Tools",
      "position": 3,
      "description": "My company internal tools",
      "protocol": "https"
    }
  ],
  "git": {
    "default_protocol": "https",
    "default_branches": ["main", "master"],
    "clone_depth": 1,
    "default_pat_token_env": "MY_COMPANY_PAT_TOKEN"
  }
}
```

**Setup environment variables:**

```bash
# ACME Corp token (for acme-corp repositories)
export ACME_CORP_PAT_TOKEN="ghp_xxxxxxxxxxxxxxxx"

# Partner Org token (for partner-org repositories)
export PARTNER_ORG_PAT_TOKEN="ghp_yyyyyyyyyyyyyyyy"

# Default token (for my-company and any repository without specific token)
export MY_COMPANY_PAT_TOKEN="ghp_zzzzzzzzzzzzzzzz"
```

**Token Priority:**
1. **Repository-specific token** (`pat_token_env` in repository config) - highest priority
2. **Global default token** (`default_pat_token_env` in git config) - fallback
3. **No token** - for public repositories with HTTPS

**Benefits:**
- ✅ Each organization's token has minimal required permissions
- ✅ Easier to rotate/revoke tokens per organization
- ✅ Better security isolation between organizations
- ✅ Can mix public and private repositories easily

### Ultimate Flexibility: Combining SSH Keys and PAT Tokens

You can mix SSH (with different keys) and HTTPS (with different tokens) for maximum flexibility:

```json
{
  "repositories": [
    {
      "github_path": "acme-corp/api-docs",
      "display_name": "ACME API",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/acme_corp_key",
      ...
    },
    {
      "github_path": "partner-org/service-docs",
      "display_name": "Partner Service",
      "protocol": "https",
      "pat_token_env": "PARTNER_ORG_PAT_TOKEN",
      ...
    },
    {
      "github_path": "contractor-team/integration-docs",
      "display_name": "Integration Docs",
      "protocol": "https",
      "pat_token_env": "CONTRACTOR_PAT_TOKEN",
      ...
    },
    {
      "github_path": "my-company/internal-docs",
      "display_name": "Internal Docs",
      "protocol": "ssh",
      ...
    }
  ],
  "git": {
    "default_protocol": "ssh",
    "default_ssh_key_path": "~/.ssh/id_ed25519",
    "pat_token_env": "GITHUB_PAT_TOKEN",
    "clone_depth": 1,
    "default_branches": ["main", "master"]
  }
}
```

**When to use SSH vs HTTPS:**
- **Use SSH when:**
  - You have long-term access to the organization
  - SSH keys are already set up with the organization
  - Working with your own or company repositories
  - Security policies require SSH

- **Use HTTPS + PAT when:**
  - Temporary access to external repositories
  - CI/CD pipelines
  - Contractor/partner access with limited scope
  - Easy token rotation required
  - SSH is not available/configured

---

## CI/CD Examples

### GitHub Actions

```yaml
name: Sync Documentation

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install DocuSync
        run: pip install docusync

      - name: Sync Documentation
        env:
          GITHUB_PAT_TOKEN: ${{ secrets.GITHUB_PAT_TOKEN }}
        run: docusync sync -v

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "docs: sync documentation" || echo "No changes"
          git push
```

### GitLab CI

```yaml
sync_docs:
  stage: deploy
  image: python:3.12
  before_script:
    - pip install docusync
  script:
    - docusync sync -v
    - git config user.email "ci@gitlab.com"
    - git config user.name "GitLab CI"
    - git add docs/
    - git commit -m "docs: sync documentation" || echo "No changes"
    - git push https://oauth2:${CI_PUSH_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_PATH}.git HEAD:${CI_COMMIT_BRANCH}
  variables:
    GITHUB_PAT_TOKEN: $GITHUB_PAT_TOKEN
  only:
    - schedules
```

---

## Troubleshooting

### SSH Issues

**Problem:** `Permission denied (publickey)`

**Solution:**
1. Check SSH key is added to GitHub
2. Test SSH connection: `ssh -T git@github.com`
3. Verify SSH agent is running: `eval "$(ssh-agent -s)"`
4. Add key to agent: `ssh-add ~/.ssh/id_ed25519`

### HTTPS Issues

**Problem:** `Authentication failed` or `fatal: could not read Username`

**Solution:**
1. Verify token is set: `echo $GITHUB_PAT_TOKEN`
2. Check token has correct permissions (repo scope)
3. Ensure token hasn't expired
4. Verify `pat_token_env` (repository-level) or `default_pat_token_env` (global) matches your environment variable name

**Problem:** Token visible in error messages

**Solution:** DocuSync automatically sanitizes error messages, but ensure:
1. You're using the latest version
2. You're not logging Git output elsewhere
3. You're not running Git commands directly with the token

### General Issues

**Problem:** `Repository not found`

**Solution:**
1. Verify the repository path is correct
2. Check you have access to the repository
3. For private repos, ensure your authentication method has access
4. Try cloning manually to test: `git clone <url>`

---

## Security Best Practices

### For PAT Tokens

1. **Never commit tokens to Git**: Always use environment variables
2. **Use minimal scopes**: Only grant necessary permissions
3. **Rotate tokens regularly**: Update tokens every few months
4. **Use different tokens for different purposes**: Don't reuse CI tokens locally
5. **Revoke unused tokens**: Clean up old tokens in GitHub settings
6. **Use repository secrets**: In CI/CD, store tokens as encrypted secrets

### For SSH Keys

1. **Use passphrase-protected keys**: Add extra security layer
2. **Use separate keys for different purposes**: Don't reuse personal keys for CI
3. **Rotate keys periodically**: Update SSH keys regularly
4. **Remove unused keys**: Clean up old keys from GitHub settings

---

## Need Help?

- 🐛 [Report issues](https://github.com/Roman505050/docusync/issues)
- 💡 [Request features](https://github.com/Roman505050/docusync/issues)

