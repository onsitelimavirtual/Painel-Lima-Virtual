# Painel Lima Virtual 3.0 — Produção

Esta pasta deve ser o CONTEÚDO RAIZ da branch `portfoliolimavirtual`.

Estrutura crítica:
- `index.html` na raiz
- `.github/workflows/deploy-cloudflare.yml`
- `.github/workflows/deploy-firebase.yml`
- `firebase.json`
- `wrangler.jsonc`

Não coloque os YAMLs de deploy na raiz: GitHub Actions só reconhece workflows em `.github/workflows/`.

## Cloudflare
Secrets necessários no repositório:
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

## Firebase
Secrets necessários:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_SERVICE_ACCOUNT_PAINEL_LIMA_VIRTUAL`

O ChatGPT atualmente não tem escrita nesse repositório `onsitelimavirtual/Painel-Lima-Virtual`, então a publicação desses arquivos precisa ser feita pela conta proprietária ou por uma conexão GitHub com permissão de escrita.

© 2026 Nailson Lima.
