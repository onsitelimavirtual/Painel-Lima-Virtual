-- Painel Lima Virtual 2.0 — definir a conta administradora
-- Faça login pelo menos uma vez e troque SEU_EMAIL pelo seu e-mail.
insert into public.plv_admins (user_id)
select id from auth.users where lower(email)=lower('SEU_EMAIL')
on conflict (user_id) do nothing;

select a.user_id,u.email,a.created_at
from public.plv_admins a join auth.users u on u.id=a.user_id
order by a.created_at;
