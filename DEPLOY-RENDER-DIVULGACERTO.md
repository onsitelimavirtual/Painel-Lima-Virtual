# Publicação da API do DivulgaCerto no Render

## O que será publicado
API FastAPI que analisa páginas públicas e arquivos ZIP, sem executar os códigos enviados.
A API usa `analyzer_service.py` e `requirements-analyzer.txt`.

## Publicar
1. Entre em https://dashboard.render.com/ e conecte a conta GitHub que tem acesso a este repositório.
2. Selecione **New + → Blueprint**.
3. Escolha `onsitelimavirtual/Painel-Lima-Virtual`, branch `portfoliolimavirtual`.
4. O Render lerá `render.yaml`. Revise o serviço `divulgacerto-product-intelligence` e confirme a criação.
5. Aguarde o deploy e abra a URL HTTPS gerada pelo Render.
6. Teste `https://SUA-URL.onrender.com/health`. A resposta esperada contém `"status":"ok"`.

## Conectar o front-end
Depois de obter a URL HTTPS do Render, edite `config.js` no GitHub e preencha somente:
```js
PRODUCT_API_URL: "https://SUA-URL.onrender.com"
```
Mantenha `SUPABASE_URL` e `SUPABASE_ANON_KEY` conforme a configuração real do projeto. Nunca coloque a chave `service_role` no navegador.
O HTML carrega `config.js` externamente; não duplique a configuração dentro de `DivulgaCerto-Android.html`.

## Testes
- GET `/health`: serviço disponível.
- POST `/api/analyze` com `site_url`: extração de conteúdo de página pública.
- POST `/api/analyze` com arquivo `.zip`: leitura limitada de arquivos textuais, sem executar conteúdo.
- Testar também campos vazios, URL inválida, ZIP corrompido e ZIP acima de 50 MB.

## Limites conhecidos
- A análise atual é extração e classificação heurística, não um modelo generativo/LLM.
- Sites que exigem login, bloqueiam robôs ou dependem de JavaScript podem não fornecer conteúdo suficiente.
- O plano gratuito do Render pode suspender serviços ociosos e aumentar o tempo da primeira resposta.
- Antes de uso público, revisar CORS para restringir a origem ao domínio publicado do DivulgaCerto e adicionar limites de requisição/monitoramento.

## Ativar métricas reais — DivulgaCerto 2.2

1. No Supabase SQL Editor, execute o arquivo `divulgacerto_2_2_metrics.sql` deste repositório.
2. No Render, abra o serviço da API → **Environment** e configure:
   - `SUPABASE_URL`: URL do projeto Supabase.
   - `SUPABASE_SERVICE_ROLE_KEY`: chave secreta service_role do projeto. Cadastre somente no Render; nunca no `config.js`, HTML ou GitHub.
   - `PUBLIC_API_URL`: URL pública HTTPS da API Render, sem barra final.
   - `DIVULGACERTO_WEBHOOK_TOKEN`: token aleatório forte, criado por você para autenticar o webhook de conversões.
3. Salve e faça novo deploy. O endpoint `/health` deve indicar versão 2.2.0.
4. No aplicativo, entre com Google, abra uma campanha e clique em **Gerar link rastreável**. Divulgue esse link em vez do destino original. Cada visita ao link conta um clique antes do redirecionamento.
5. A contagem automática aparece quando o usuário autenticado abre a campanha novamente. Os cliques só são rastreados em links criados pelo botão; links antigos não são retroativamente rastreados.

### Testar autenticação pela documentação Swagger

1. Abra `/docs` na URL pública do Render.
2. Entre no DivulgaCerto com Google e obtenha uma sessão ativa no aplicativo.
3. Para chamadas feitas pelo Swagger, use o access token JWT da sessão Supabase no botão **Authorize** (esquema HTTP Bearer). Não use a chave publishable/anon como token de usuário.
4. Execute `POST /api/tracking/register` com `campaign_id` e `destination`. A API valida o JWT em `/auth/v1/user` e associa o link ao ID do usuário autenticado.
5. Consulte as métricas com o mesmo usuário autenticado. O Swagger agora documenta o esquema Bearer no botão Authorize; os endpoints não aceitam chamadas anônimas.

Não compartilhe access tokens, service_role ou webhook token em capturas de tela ou mensagens.

### Webhook de conversões
A API aceita POST em `/api/webhooks/conversion`, com cabeçalho `X-Webhook-Token` igual ao segredo cadastrado no Render e JSON:
```json
{
  "campaign_id": "ID-DA-CAMPANHA",
  "order_id": "ID-UNICO-DO-PEDIDO",
  "amount": 49.90,
  "currency": "BRL",
  "status": "approved",
  "source": "kiwify"
}
```
Somente status aprovados/pagos/concluídos são registrados. O identificador `order_id` é único para evitar duplicidade. O webhook exige que sua integração envie o ID da campanha correspondente; a configuração do webhook na plataforma de checkout é uma etapa separada.

### Limitações e proteção
- Cliques são contados por acesso ao link, não são deduplicados por pessoa/dispositivo e podem incluir robôs ou pré-visualizações de mensageiros.
- Conversões automáticas só aparecem depois que o checkout estiver configurado para enviar o webhook com o ID da campanha e o token secreto.
- Conversões inseridas manualmente permanecem disponíveis como registro manual.
- Configure limites de requisição e monitore o uso da API antes de divulgar links em larga escala.
