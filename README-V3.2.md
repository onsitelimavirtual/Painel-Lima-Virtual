# Painel Lima Virtual 3.2 — Google + Plano Educacional

## Implementado
- Login com Google via Supabase Auth.
- E-mail/senha mantido como alternativa.
- Perfil → Meu plano.
- Plano Educacional configurável pelo administrador.
- Checkout iniciado pela Edge Function `plv-checkout-start`.
- Webhook Kiwify `plv-kiwify-webhook`.
- Compra vinculada ao usuário por `sck=plv_<attempt_id>`.
- Idempotência: o mesmo pedido não duplica licença.
- Reembolso e chargeback revogam o acesso.
- Pagamentos sem vínculo vão para conciliação.
- Cada app pode exigir ou não um plano ativo.
- HTMLs internos pagos são protegidos por política no Supabase Storage.

## Configuração rápida do plano
Entre como administrador:
1. Perfil → Administração.
2. Plano Educacional.
3. Informe preço real, duração em dias e URL do checkout da Kiwify.
4. Marque Oferta ativa.
5. Teste com uma conta Google não administrativa.

## Webhook
`https://piagfpnjiwpngbikkkfp.supabase.co/functions/v1/plv-kiwify-webhook`

A oferta permanece bloqueada se preço, duração ou URL não estiverem completos.

© 2026 Nailson Lima.

## Monitoramento administrativo
Em **Perfil → Administração → Pagamentos** o administrador consegue acompanhar:
- últimos eventos recebidos da Kiwify;
- presença da assinatura;
- estado do processamento;
- pagamentos enviados para conciliação manual;
- URL exata do webhook com botão para copiar.

Os registros são sanitizados e não exibem o e-mail do comprador.
