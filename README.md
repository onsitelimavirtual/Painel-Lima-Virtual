# Painel Lima Virtual 2.3 — Ícones Inteligentes

A V2.3 preserva a arquitetura da V2.2 Final e adiciona reconhecimento visual automático dos subsistemas.

## Como funciona

### URL externa
Ao implantar ou editar uma URL com modo **Automático**, o Painel chama a Edge Function `plv-icon-detector`.
A função:
- exige sessão autenticada;
- confirma que o usuário é administrador;
- consulta a página remotamente;
- procura `apple-touch-icon`, `<link rel="icon">`, ícones do `manifest.webmanifest` e `/favicon.ico`;
- evita consultas explícitas a hosts privados/localhost;
- devolve a imagem detectada;
- o Painel salva o ícone em `painel-lima-icons`.

### HTML interno
O Painel analisa o HTML no próprio navegador e procura:
- favicon embutido em `data:image/...`;
- `apple-touch-icon` embutido;
- imagens embutidas cujo nome/classe/alt indiquem logo ou ícone.

Como o HTML interno da V2.3 continua standalone, um caminho relativo como `assets/logo.png` não existe sozinho no Storage. Nesse caso, use ícone manual ou mantenha a imagem embutida no próprio HTML.

## Três modos de ícone
- **Automático** — tenta reconhecer e salvar.
- **Imagem manual** — administrador seleciona PNG/JPEG/WebP/SVG/ICO.
- **Iniciais automáticas** — gera monograma como `CM` para “Chat com Matemática”.

## Subsistemas já existentes
No modo administrador, use **Reconhecer ícones**.
O Painel percorre os apps que não usam ícone manual, tenta reconhecer cada identidade e salva o resultado. Quando não encontra, aplica iniciais.

## Persistência
Novos campos em `public.plv_apps`:
- `icon_url`
- `icon_mode`
- `icon_storage_path`
- `icon_source`

Bucket:
- `painel-lima-icons` — público para leitura dos ícones, mas gravação/alteração/exclusão restrita a administradores por RLS.

## Segurança
A detecção externa roda no backend para evitar CORS do navegador.
A função rejeita localhost e faixas IP privadas explícitas e valida o administrador antes de consultar a URL.

© 2026 Nailson Lima.
