# Painel Lima Virtual 2.0

Portal central de subsistemas.

## O que já está pronto
- login pelo Supabase;
- catálogo de subsistemas;
- INKIS IA V10.2 incluído como primeiro subsistema;
- usuário comum vê apenas apps publicados;
- administrador pode implantar URL externa ou HTML standalone;
- Rascunho / Publicado / Oculto;
- abertura no painel, nova aba ou tela inteira;
- busca, categorias e ordenação;
- bucket privado e RLS;
- QA estrutural básico do HTML antes do upload.

## Primeiro administrador
Por segurança nenhuma conta foi promovida automaticamente. Faça login no Painel e execute `SETUP-ADMIN.sql` no SQL Editor, substituindo `SEU_EMAIL`.

## Estrutura Supabase aplicada
- `public.plv_admins`
- `public.plv_apps`
- bucket privado `painel-lima-apps`

O frontend usa apenas a publishable key. Nenhuma service role ou chave secreta foi embutida.

## HTML interno
A V2.0 aceita HTML standalone de até 10 MB. O administrador envia o arquivo diretamente do computador ou celular; o usuário abre por URL temporária assinada.

## URL externa
Pode ser aberta dentro do painel, em nova aba ou tela inteira. Sites que bloqueiam iframe devem usar Nova aba.

## V2.1 sugerida
ZIP multi-arquivo, ícones próprios, grupos de acesso, favoritos e versionamento.


## Identidade visual LV
A logomarca oficial utiliza apenas as letras **LV**, sem o P de “Painel”. Aplicada no cabeçalho, tela de login, favicon e ícones PWA.
