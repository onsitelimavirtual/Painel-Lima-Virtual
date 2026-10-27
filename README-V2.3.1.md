# Painel Lima Virtual 2.3.1 — Ícones Corrigidos

Correção específica dos ícones dos cards.

## O que foi corrigido
- `◈` não é mais usado como fallback visual.
- `icon_url` salvo no Supabase tem prioridade.
- Para links externos, o painel tenta automaticamente:
  1. `icon_url`;
  2. `icon-192.png`;
  3. `icon-512.png`;
  4. `favicon.ico`;
  5. favicon da origem;
  6. iniciais do nome.
- O administrador possui o botão **Reconhecer ícones**.
- URLs externas sem ícone salvo são verificadas automaticamente uma vez ao entrar como administrador.
- É possível escolher uma imagem manual de até 1 MB.
- O catálogo já foi corrigido no Supabase:
  - Chat com Matemática → `CM` + ícone público real;
  - Mentoria Extraordinária → `ME`;
  - Meu Reforço Favorito → `MR`.

A Edge Function `plv-icon-detector` está publicada no Supabase e é usada apenas por administradores.

© 2026 Nailson Lima.
