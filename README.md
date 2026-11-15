# DivulgaCerto 2.0 — Inteligência de Produtos e Divulgação Multicanal

Aplicação web responsiva e instalável para empreendedores analisarem produtos, criarem campanhas e prepararem conteúdos para WhatsApp, Instagram e Facebook.

## O que funciona nesta versão

- Cadastro, edição e exclusão de campanhas.
- Geração local de textos por canal.
- Edição e cópia dos conteúdos.
- Abertura de opções de compartilhamento.
- Registro local de ações de compartilhamento.
- Registro manual de cliques e conversões confirmados externamente.
- Dashboard e histórico.
- Exportação de backup JSON.
- PWA com cache básico para arquivos da aplicação.
- Estrutura de autenticação Google via Supabase, aguardando credenciais.

## Limitações conhecidas

1. Os dados ficam no armazenamento local do navegador (`localStorage`). Não sincronizam entre dispositivos nem usuários.
2. O login Google só será ativado depois de configurar Supabase e Google OAuth.
3. Não há publicação automática nas redes sociais. Instagram e Facebook têm restrições e permissões próprias; o app abre destinos de compartilhamento quando disponíveis.
4. A ação de compartilhar não comprova entrega, alcance, visualização ou venda.
5. A PWA precisa ser servida por HTTPS ou localhost. Abrir `index.html` diretamente pode impedir service worker e alguns recursos.
6. O cache offline cobre os arquivos do app, mas não garante autenticação nem acesso a serviços externos sem internet.

## Executar localmente

Requer Python 3 instalado:

```bash
python -m http.server 8000
```

Abra `http://localhost:8000`.

Também pode usar qualquer servidor estático ou GitHub Pages.

## Ativar Google OAuth com Supabase

1. Crie/seleciona um projeto Supabase.
2. Em Authentication > Providers, habilite Google.
3. Configure as credenciais OAuth no Google Cloud Console.
4. Cadastre as URLs de redirecionamento permitidas no Supabase e no Google.
5. Copie a Project URL e a chave `anon`/publishable.
6. Preencha `config.js`:

```js
window.APP_CONFIG = {
  SUPABASE_URL: "https://SEU-PROJETO.supabase.co",
  SUPABASE_ANON_KEY: "SUA_CHAVE_PUBLICA"
};
```

Nunca use `service_role` no navegador.

**Importante:** nesta entrega, OAuth autentica a sessão, mas os dados das campanhas ainda são locais. Para sincronização multiusuário, será necessária uma etapa posterior com tabelas, políticas RLS e migração dos dados para Supabase.

## Estrutura

- `index.html` — interface e telas.
- `styles.css` — layout responsivo e acessibilidade visual.
- `app.js` — lógica de campanhas, conteúdos, métricas e autenticação.
- `config.js` — configuração opcional do Supabase.
- `manifest.webmanifest` — metadados PWA.
- `sw.js` — cache básico offline.

## Roteiro de testes manuais

- [ ] Abrir em desktop e celular.
- [ ] Tentar salvar campanha vazia: deve mostrar erro.
- [ ] Informar URL inválida: deve rejeitar.
- [ ] Salvar campanha válida: deve aparecer no histórico.
- [ ] Abrir conteúdos dos três canais e editar o texto.
- [ ] Copiar conteúdo.
- [ ] Acionar compartilhamento e verificar abertura do destino.
- [ ] Registrar cliques/conversões e conferir dashboard.
- [ ] Exportar JSON e verificar o arquivo.
- [ ] Recarregar a página e confirmar persistência local.
- [ ] Testar navegação por teclado.

## Privacidade

Os dados da campanha permanecem no navegador até que o usuário limpe os dados do site ou exporte o backup. Não inserir dados pessoais sensíveis. Em computador compartilhado, sair da conta Google não apaga os dados locais.


## Identidade e documentos legais

Nome de trabalho: DivulgaCerto. Identificação autoral: Copyright © 2026 Nailson Lima. Inclui `termos.html` e `privacidade.html` como minutas preliminares. Substituir os campos `[INSERIR E-MAIL DE CONTATO CONFIRMADO]` e revisar juridicamente antes de lançamento público. A busca de nome no INPI ainda precisa de análise formal de anterioridade e classes.


## DivulgaCerto 2.0 — consolidação e estabilidade

### Melhorias desta versão
- Corrigida a referência ao elemento de status da nuvem, que podia interromper a inicialização quando já havia uma sessão Google ativa.
- A sincronização agora mantém o indicador de estado consistente e libera o bloqueio mesmo quando ocorre falha.
- A autenticação mostra estado de inicialização e não dispara aviso temporário durante o carregamento da biblioteca.
- Em falha persistente, o usuário recebe um estado discreto e pode tentar novamente; a operação local continua disponível.
- O logout Supabase permanece normal, com alternativa local de segurança.
- Identificação visual da versão 2.0, backup JSON com versão 2.0.0 e cache PWA renovado.
- O atalho de instalação abre diretamente `DivulgaCerto-Android.html`.

### Validação antes de considerar a versão estável
- Testar login Google com sessão nova e sessão já existente.
- Testar logout e novo login no mesmo dispositivo.
- Testar sincronização com rede disponível e indisponível.
- Confirmar que campanhas locais permanecem preservadas quando a nuvem falha.
- Atualizar a PWA e confirmar que a versão 2.0 substitui o cache anterior.

## DivulgaCerto 1.2 — Inteligência de Produtos

### Interface
- Acesse a navegação **Inteligência de produtos** ou o atalho na criação de campanha.
- Informe uma URL pública, selecione um ZIP de até 50 MB ou use ambos.
- Revise separadamente informações encontradas nas fontes, inferências heurísticas e pendências.
- Gere materiais de texto avançados: WhatsApp, Instagram, Facebook, roteiro de Reels, carrossel e briefing visual.
- Use a análise para preencher o formulário da campanha; confirme e edite os dados antes de salvar.
- Exporte o resultado da análise em JSON.

### API de análise real
A leitura de sites e ZIPs é feita pelo serviço FastAPI em `analyzer_service.py`. O serviço extrai HTML e arquivos textuais sem executar o conteúdo do ZIP. A classificação atual é heurística local; não é um modelo de IA generativa e não valida independentemente se os recursos anunciados funcionam.

Instalação da API:
```bash
pip install -r requirements-analyzer.txt
uvicorn analyzer_service:app --host 0.0.0.0 --port 8000
```
Configure `PRODUCT_API_URL` em `config.js` com a URL HTTPS publicada da API. A API deve ser hospedada separadamente do GitHub Pages. Configure CORS para o domínio final do app e use HTTPS. Não exponha o serviço sem proteção contra abuso/rate limit em produção.

### Limitações importantes
- Sites com autenticação, JavaScript pesado, bloqueios anti-bot ou conteúdo não público podem não ser analisados.
- ZIPs: até 50 MB, 250 entradas e 100 MB descompactados; apenas tipos textuais permitidos são inspecionados. Código recebido nunca é executado.
- A análise gera evidências textuais e inferências, não certificação de qualidade, segurança ou funcionamento do produto.
- Publicação automática em redes sociais não está habilitada. A distribuição híbrida nesta versão significa preparar, revisar, copiar e abrir os canais; automação oficial exige APIs e permissões próprias.
- Geração de imagens finais ainda não está incluída; o sistema entrega briefing visual e estrutura de peças.
