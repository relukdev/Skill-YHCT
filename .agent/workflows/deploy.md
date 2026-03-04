---
description: Deploy landing page and worker for the YHCT AI project. Use this whenever asked to deploy.
---

# YHCT AI Deployment Workflow

> [!CAUTION]
> **TWO SEPARATE Cloudflare services. NEVER mix them up.**

## 🗺️ Deployment Map

| Component | Type | Project Name | Domains | Command |
|-----------|------|-------------|---------|---------|
| **Landing Page** | Cloudflare Pages | `yhct-ai` | `yhct-ai.pages.dev`, `yhct.todyai.io` | `npx wrangler pages deploy landing --project-name yhct-ai` |
| **Worker API** | Cloudflare Workers | `tuchanai-api` | `tuchanai-api.todyai.workers.dev` | `npm run deploy` (from `tu-chan-ai/worker/`) |

> [!WARNING]
> **NEVER deploy to `khoahochuyetdao`** — that is a completely separate project (KhoaHocHuyetDao blog).

---

## Step 1: Deploy Landing Page

Working directory: project root (`yhct-consultation/`)

```bash
# turbo
npx wrangler pages deploy landing --project-name yhct-ai --commit-dirty=true
```

Verify at: https://yhct.todyai.io

---

## Step 2: Deploy Worker API

Working directory: `tu-chan-ai/worker/`

```bash
# turbo
npm run deploy
```

Verify at: https://tuchanai-api.todyai.workers.dev

---

## Step 3: Git Commit

Working directory: project root

```bash
git add -A && git commit -m "deploy: update landing + worker"
git push origin main
```

---

## Verification

```bash
# Check worker health
curl -s https://tuchanai-api.todyai.workers.dev/ | json_pp

# Check available models
curl -s https://tuchanai-api.todyai.workers.dev/api/models | json_pp

# Check landing page
curl -sI https://yhct.todyai.io | head -5
```
