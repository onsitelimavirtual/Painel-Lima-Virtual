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
