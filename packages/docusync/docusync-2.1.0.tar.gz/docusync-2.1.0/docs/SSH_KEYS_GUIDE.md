# SSH Keys Configuration Guide

This guide explains how to configure and use different SSH keys with DocuSync for accessing multiple GitHub organizations.

## Why Use Different SSH Keys?

When working with multiple GitHub organizations or accounts, you may need different SSH keys:

- 🏢 **Company repositories** - Use company-specific key
- 🤝 **Partner organizations** - Use partner-specific key  
- 👤 **Personal repositories** - Use personal key
- 🔒 **Security isolation** - Each key has limited access scope

## Quick Setup

### 1. Generate SSH Keys

Generate a separate key for each organization:

```bash
# Company key
ssh-keygen -t ed25519 -f ~/.ssh/company_key -C "work@company.com"

# Partner organization key
ssh-keygen -t ed25519 -f ~/.ssh/partner_key -C "partner@partner-org.com"

# Personal key (if not exists)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "personal@email.com"
```

### 2. Add Public Keys to GitHub

For each key, add the public key to the corresponding GitHub organization:

```bash
# Display public key
cat ~/.ssh/company_key.pub
```

Then:
1. Go to GitHub (logged in with appropriate account)
2. Settings → SSH and GPG keys
3. Click "New SSH key"
4. Paste the public key
5. Save

### 3. Configure DocuSync

**Option A: Global default key**

```json
{
  "git": {
    "default_ssh_key_path": "~/.ssh/id_ed25519"
  }
}
```

**Option B: Per-repository keys**

```json
{
  "repositories": [
    {
      "github_path": "company/api-docs",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/company_key",
      ...
    },
    {
      "github_path": "partner-org/service-docs",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/partner_key",
      ...
    },
    {
      "github_path": "myusername/personal-docs",
      "protocol": "ssh",
      ...
    }
  ],
  "git": {
    "default_protocol": "ssh",
    "default_ssh_key_path": "~/.ssh/id_ed25519"
  }
}
```

### 4. Sync Documentation

```bash
docusync sync
```

DocuSync will automatically use the correct SSH key for each repository!

## Complete Example

Let's say you work with 3 different GitHub organizations:

### Setup Script

```bash
#!/bin/bash

# Generate keys
ssh-keygen -t ed25519 -f ~/.ssh/acme_corp_key -C "john@acme-corp.com" -N ""
ssh-keygen -t ed25519 -f ~/.ssh/partner_org_key -C "john@partner-org.com" -N ""
ssh-keygen -t ed25519 -f ~/.ssh/contractor_key -C "john@contractor.com" -N ""

# Display keys to add to GitHub
echo "=== ACME Corp Key (add to acme-corp GitHub org) ==="
cat ~/.ssh/acme_corp_key.pub
echo ""

echo "=== Partner Org Key (add to partner-org GitHub org) ==="
cat ~/.ssh/partner_org_key.pub
echo ""

echo "=== Contractor Key (add to contractor GitHub org) ==="
cat ~/.ssh/contractor_key.pub
```

### Configuration

```json
{
  "repositories": [
    {
      "github_path": "acme-corp/api-gateway",
      "docs_path": "docs",
      "display_name": "ACME API Gateway",
      "position": 1,
      "description": "API Gateway documentation",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/acme_corp_key"
    },
    {
      "github_path": "acme-corp/user-service",
      "docs_path": "docs",
      "display_name": "ACME User Service",
      "position": 2,
      "description": "User service documentation",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/acme_corp_key"
    },
    {
      "github_path": "partner-org/billing-service",
      "docs_path": "documentation",
      "display_name": "Partner Billing",
      "position": 3,
      "description": "Partner billing service",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/partner_org_key"
    },
    {
      "github_path": "contractor/integration-api",
      "docs_path": "docs",
      "display_name": "Integration API",
      "position": 4,
      "description": "Contractor integration API",
      "protocol": "ssh",
      "ssh_key_path": "~/.ssh/contractor_key"
    }
  ],
  "paths": {
    "temp_dir": ".temp-repos",
    "docs_dir": "docs"
  },
  "git": {
    "clone_depth": 1,
    "default_branches": ["main", "master"],
    "default_protocol": "ssh",
    "default_ssh_key_path": "~/.ssh/id_ed25519"
  }
}
```

## Testing Your Setup

Test each SSH key individually:

```bash
# Test ACME Corp key
ssh -i ~/.ssh/acme_corp_key -T git@github.com

# Test Partner Org key
ssh -i ~/.ssh/partner_org_key -T git@github.com

# Test Contractor key
ssh -i ~/.ssh/contractor_key -T git@github.com
```

You should see: `Hi <username>! You've successfully authenticated...`

## Key Priority

DocuSync uses SSH keys in this order:

1. 🥇 **Repository-specific** `ssh_key_path` (highest priority)
2. 🥈 **Global default** `default_ssh_key_path`
3. 🥉 **System default** (usually `~/.ssh/id_rsa` or `~/.ssh/id_ed25519`)

## Advanced: SSH Config Alternative

Instead of specifying keys in DocuSync, you can also configure SSH:

**~/.ssh/config:**
```ssh
# ACME Corp
Host github.com-acme
    HostName github.com
    User git
    IdentityFile ~/.ssh/acme_corp_key
    IdentitiesOnly yes

# Partner Org
Host github.com-partner
    HostName github.com
    User git
    IdentityFile ~/.ssh/partner_org_key
    IdentitiesOnly yes
```

However, **DocuSync's built-in SSH key configuration is simpler** because:
- ✅ No need to modify SSH config
- ✅ Keys are specified directly in `docusync.json`
- ✅ No need for custom Git remotes
- ✅ Works with standard GitHub URLs

## Troubleshooting

### Permission Denied

**Error:** `Permission denied (publickey)`

**Solutions:**
1. Verify key is added to correct GitHub account/organization
2. Test SSH connection: `ssh -i ~/.ssh/your_key -T git@github.com`
3. Check key file permissions: `chmod 600 ~/.ssh/your_key`
4. Ensure public key exists: `ls -la ~/.ssh/your_key.pub`

### Wrong Key Being Used

**Error:** Repository not found or access denied

**Solutions:**
1. Verify `ssh_key_path` points to correct key
2. Use absolute path instead of `~` if issues persist
3. Check verbose output: `docusync sync -v`

### Key File Not Found

**Error:** `No such file or directory`

**Solutions:**
1. Verify path is correct: `ls -la ~/.ssh/your_key`
2. Use absolute path: `/Users/yourname/.ssh/your_key`
3. Check file permissions: `chmod 600 ~/.ssh/your_key`

## Security Best Practices

1. 🔐 **Use passphrases** - Protect keys with strong passphrases
2. 🔄 **Rotate keys regularly** - Update keys every 6-12 months
3. 🗑️ **Remove old keys** - Delete unused keys from GitHub
4. 📁 **Correct permissions** - `chmod 600 ~/.ssh/*_key`
5. 🔒 **Separate keys per organization** - Better security isolation
6. 📝 **Document key usage** - Keep track of which key is for what
7. 🚫 **Never commit private keys** - Keep them out of Git repos

## CI/CD Considerations

For CI/CD pipelines, consider using **HTTPS with PAT tokens** instead of SSH keys:

**Why?**
- ✅ Easier secret management
- ✅ Simpler to rotate
- ✅ No SSH agent required
- ✅ Better suited for containerized environments

**Example:**
```json
{
  "repositories": [
    {
      "github_path": "company/api-docs",
      "protocol": "https",
      "pat_token_env": "COMPANY_PAT_TOKEN",
      ...
    }
  ],
  "git": {
    "default_pat_token_env": "GITHUB_PAT_TOKEN"
  }
}
```

See [AUTHENTICATION.md](AUTHENTICATION.md) for PAT token setup.

## Need Help?

- 📖 [Full Authentication Guide](AUTHENTICATION.md)
- 🐛 [Report issues](https://github.com/Roman505050/docusync/issues)
- 💡 [Request features](https://github.com/Roman505050/docusync/issues)

