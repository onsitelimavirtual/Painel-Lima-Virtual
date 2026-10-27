# Painel Lima Virtual 2.2 Final

Versão final consolidada do portal de subsistemas.

## Acesso
- Administrador configurado no Supabase: `onsite.limavirtual@gmail.com`
- Usuários comuns veem somente subsistemas publicados.
- Operações administrativas continuam protegidas por RLS no Supabase.

## Correções definitivas
- Logo LV incorporada ao próprio HTML, evitando imagem quebrada no login.
- Login com timeout e mensagens de rede claras.
- HTML interno deixou de depender de URL assinada.
- Arquivos privados são obtidos pelo endpoint autenticado do Supabase Storage e abertos como `blob:` temporário.
- Isso corrige o cenário em que o arquivo existe no Storage, mas o navegador recebia `Object not found` ao abrir a URL assinada.
- O administrador pode substituir/reimplantar o HTML de um subsistema já cadastrado.
- A versão antiga do arquivo é excluída somente após a atualização do catálogo ter sido salva.
- Diagnóstico administrativo verifica INKIS IA e todos os HTMLs internos.
- Cards recebem indicador de disponibilidade depois do diagnóstico.
- Service Worker usa estratégia network-first para o shell principal, reduzindo risco de ficar preso em uma versão antiga após nova publicação.
- Layout, tema claro/escuro, catálogo, categorias e INKIS IA foram preservados.

## Publicação
Publique a pasta inteira, preservando:
- `index.html`
- `manifest.webmanifest`
- `service-worker.js`
- `icons/`
- `assets/`
- `subsystems/`

O INKIS IA está incluído em `subsystems/inkis-ia/`.

## HTML interno
A V2.2 mantém a regra de HTML standalone de até 10 MB. CSS, JavaScript e demais recursos necessários ao aplicativo devem estar incorporados no próprio HTML para máxima compatibilidade.

## Diagnóstico
No modo administrador, use **Diagnóstico**. Para cada HTML interno:
- ✅ disponível: arquivo acessível com a sessão atual;
- ⚠ indisponível: o painel mostra a causa e oferece **Reimplantar**.

## Segurança
- Bucket `painel-lima-apps` permanece privado.
- Nenhuma service_role está exposta no frontend.
- Autorização de administrador é feita pela tabela `plv_admins` + RLS.
- HTML interno é exibido em iframe sandbox quando aberto dentro do painel.

© 2026 Nailson Lima.
