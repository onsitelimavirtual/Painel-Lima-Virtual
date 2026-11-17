# Estabilização 4.1 — Painel Lima Virtual

**Branch:** `stabilizacao-4.1`  
**Base:** `portfoliolimavirtual`  
**Objetivo:** corrigir problemas de baixo risco, adicionar validação reproduzível e registrar os bloqueios que exigem homologação externa.

## Alterações nesta branch

1. **Service Worker 4.1**
   - Removida a referência ao recurso `./assets/lv-logo.png`, que não está presente na raiz atual.
   - Cache inicial passa a tolerar falhas individuais sem abortar a instalação.
   - Cache versionado como `painel-lima-virtual-4-1`.
   - Navegação usa a versão em cache como fallback quando a rede falha.
   - Limpeza limitada aos caches antigos com prefixo do Painel Lima Virtual.

2. **Validação estática reproduzível**
   - Adicionado `scripts/validate_inline_js.py`.
   - Verifica a sintaxe dos scripts JavaScript inline em arquivos HTML com Node.js.
   - Adicionado workflow `.github/workflows/validate.yml`, executado nesta branch, em pull requests para a branch principal e manualmente.
   - O workflow não publica o site nem altera serviços externos.

## Bloqueios mantidos intencionalmente

### Isolamento dos aplicativos em iframe — crítico

O painel ainda usa `allow-scripts` e `allow-same-origin` no mesmo iframe. A correção segura exige definir uma origem isolada para os aplicativos, revisar a comunicação com o painel e testar autenticação, downloads, impressão e compatibilidade. Não foi aplicada uma remoção simplista de permissões porque isso poderia quebrar aplicativos existentes.

### Backend, Supabase e pagamentos

O repositório não contém evidência suficiente para confirmar integralmente as políticas RLS, as Edge Functions em produção, os segredos do ambiente, o webhook Kiwify ou o estado real das licenças. Nenhuma migração SQL ou alteração de configuração Supabase foi executada.

### Hospedagem e PWA em dispositivos reais

O workflow novo executa validação estática apenas. Não publica no Cloudflare, Firebase ou GitHub Pages. A instalação PWA, o modo offline, OAuth Google, Storage e checkout ainda exigem teste de navegador/dispositivo e serviços reais.

## Critérios de aceite para homologação

- [ ] Workflow de validação estática concluído sem falhas.
- [ ] Instalação e atualização do Service Worker testadas em navegador.
- [ ] Modo offline testado após primeira visita online.
- [ ] Aplicativos internos testados após a estratégia de isolamento ser definida.
- [ ] Login Google e e-mail/senha testados.
- [ ] Perfil Master e RLS conferidos no Supabase.
- [ ] Upload, edição e exclusão confirmados no Storage.
- [ ] Checkout e webhook testados em ambiente de teste.
- [ ] Regressão dos aplicativos do catálogo concluída.

## Resultado

Esta branch contém correções estáticas e uma rotina de validação automatizada. Ela **não deve ser considerada homologada para produção** até que os critérios externos acima sejam executados. A branch principal permanece intacta.
