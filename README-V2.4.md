# Painel Lima Virtual 2.4

## Correção principal
O ícone do INKIS IA agora está embutido diretamente no `index.html`.

Na versão anterior, quando `assets/inkis-ia-logo.png` não era encontrado na publicação,
o painel acionava o fallback e mostrava `II`.

Na V2.4:
- o card INKIS IA usa a logomarca real;
- o botão inferior INKIS IA usa a mesma logomarca;
- não depende de `assets/inkis-ia-logo.png`;
- o destino continua sendo `https://motoforce.github.io/Painel-IA-V7/`;
- o cache do Service Worker foi alterado para `painel-lima-virtual-2-4`.

© 2026 Nailson Lima.
