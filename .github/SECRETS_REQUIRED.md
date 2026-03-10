# GitHub Secrets Required

Configure these in: github.com/AURENIX-ADMIN/AURENIX/settings/secrets/actions

## Deploy Secrets (required for all deploy workflows)

| Secret | Value | Where to get |
|--------|-------|-------------|
| `VPS_IP` | `76.13.9.238` | Ya conocido |
| `VPS_SSH_KEY` | Contenido de `jose_root_ed25519` | `_INFRA/Claves_contraseñas/jose_root_ed25519` |
| `TELEGRAM_BOT_TOKEN` | Token del bot | `.env.local` → TELEGRAM_BOT_TOKEN |
| `TELEGRAM_ID_JOSE` | `501092522` | Ya conocido |

## App-specific Secrets (dashboard)

| Secret | Value |
|--------|-------|
| `N8N_API_URL` | `https://n8n.aurenix.cloud` |
| `N8N_API_KEY` | `.env.local` → N8N_API_KEY |
| `S1_WORKFLOW_ID` | `d29Pg2fnLI1evSZh` |
| `S2_WORKFLOW_ID` | `5y2hHEk3lP06yGT8` |

## Steps to configure
1. Go to github.com/AURENIX-ADMIN/AURENIX/settings/secrets/actions
2. Click "New repository secret" for each secret above
3. For VPS_SSH_KEY: paste the FULL content of jose_root_ed25519 (including -----BEGIN/END----- lines)
