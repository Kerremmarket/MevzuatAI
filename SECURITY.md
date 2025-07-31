# 🔐 Security Guide for mevzuatAI

## ⚠️ API Key Security

**NEVER** commit API keys to Git! This project uses environment variables for secure key management.

### 🏠 Local Development Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`:**
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ENVIRONMENT=development
   ```

3. **The `.env` file is automatically ignored by Git** ✅

### 🚀 Production Deployment (Railway)

1. **Set environment variables in Railway dashboard:**
   - `OPENAI_API_KEY` = your actual API key
   - `ENVIRONMENT` = production

2. **Never hardcode keys in source code!**

### 🛡️ If Keys Get Exposed

1. **Immediately revoke** the exposed key at [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Generate new keys**
3. **Remove from Git history** (see below)
4. **Update production environment variables**

### 🧹 Clean Git History (if needed)

```bash
# Remove sensitive data from Git history
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch config/config.py' \
--prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: This rewrites history!)
git push origin --force --all
```

### ✅ Security Checklist

- [ ] API keys in environment variables only
- [ ] `.env` file in `.gitignore`
- [ ] No hardcoded secrets in source code
- [ ] Production keys set in Railway dashboard
- [ ] Old exposed keys revoked

## 🚨 Reporting Security Issues

If you find a security vulnerability, please email: [your-email]