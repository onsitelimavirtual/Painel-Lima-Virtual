# Painel Lima Virtual 2.3.2 — Correção do INKIS IA

## Problema confirmado

O botão nativo do INKIS IA estava apontando para:

`./subsystems/inkis-ia/index.html`

Esse caminho depende de a pasta `subsystems/inkis-ia/` existir exatamente na mesma publicação do Painel Lima Virtual.

O INKIS IA funcional está publicado em:

`https://motoforce.github.io/Painel-IA-V7/`

## Correção

A V2.3.2 usa o endereço público funcional como destino principal do card e do botão inferior **INKIS IA**.

O caminho local foi preservado apenas como referência/fallback no objeto do subsistema, mas não é mais o destino principal.

## Resultado esperado

- Card INKIS IA → abre a publicação funcional no GitHub Pages.
- Botão inferior INKIS IA → abre o mesmo endereço.
- Não depende da pasta `subsystems/inkis-ia/` para funcionar.
- Se o navegador bloquear nova aba, o painel mostra um aviso claro.

© 2026 Nailson Lima.
