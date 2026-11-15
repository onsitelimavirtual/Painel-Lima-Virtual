"""API opcional do DivulgaCerto 2.1 para análise de sites e arquivos ZIP.
Não executa código recebido nem extrai arquivos para o sistema de arquivos.
"""
from __future__ import annotations
import io, ipaddress, json, re, socket, zipfile, os, uuid
from html import unescape
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI(title="DivulgaCerto Product Intelligence API", version="2.2.0")
# Exibe o botão Authorize do Swagger e documenta corretamente o Bearer token do Supabase.
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="SupabaseBearer")
app.add_middleware(CORSMiddleware, allow_origins=["https://onsitelimavirtual.github.io"], allow_methods=["POST", "GET"], allow_headers=["*"])
MAX_ZIP = 50 * 1024 * 1024
MAX_SITE = 2 * 1024 * 1024
MAX_FILES = 250
MAX_TOTAL_UNCOMPRESSED = 100 * 1024 * 1024
TEXT_EXTS = {'.html','.htm','.txt','.md','.json','.js','.jsx','.ts','.tsx','.css','.xml','.yaml','.yml','.csv','.svg'}

class UnsafeTarget(Exception): pass

def public_url(raw: str) -> str:
    try:
        u = urlparse(raw.strip())
        if u.scheme not in ('http','https') or not u.hostname or u.username or u.password:
            raise ValueError()
        host = u.hostname.lower()
        if host in {'localhost','localhost.localdomain'} or host.endswith('.local'):
            raise ValueError()
        infos = socket.getaddrinfo(host, u.port or (443 if u.scheme=='https' else 80), type=socket.SOCK_STREAM)
        if not infos: raise ValueError()
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if not ip.is_global: raise ValueError()
        return raw.strip()
    except Exception:
        raise UnsafeTarget('Endereço inválido ou destino não público. Informe um site público HTTP/HTTPS.')

async def fetch_site(url: str) -> tuple[str,str]:
    url = public_url(url)
    headers = {'User-Agent':'DivulgaCertoProductAnalyzer/2.1 (+public-site-analysis)', 'Accept':'text/html,text/plain;q=0.9'}
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=False, headers=headers) as client:
            r = await client.get(url)
            if r.status_code in (301,302,303,307,308):
                loc = r.headers.get('location')
                if not loc: raise HTTPException(422,'O site redirecionou sem informar destino.')
                from urllib.parse import urljoin
                dest = public_url(urljoin(url,loc))
                r = await client.get(dest)
            r.raise_for_status()
            if len(r.content) > MAX_SITE: raise HTTPException(413,'A página excede o limite de análise de 2 MB.')
            ctype = r.headers.get('content-type','')
            if 'html' not in ctype and 'text' not in ctype:
                raise HTTPException(415,'O endereço não retornou uma página HTML ou texto analisável.')
            return str(r.url), r.text
    except HTTPException: raise
    except UnsafeTarget as e: raise HTTPException(422,str(e))
    except Exception as e: raise HTTPException(502,'Não foi possível acessar o site. Verifique o endereço, a disponibilidade e se ele permite acesso público.')

def clean_text(s: str) -> str:
    return re.sub(r'\s+',' ',unescape(s or '')).strip()

def extract_html(text: str, source: str) -> list[dict]:
    soup=BeautifulSoup(text,'html.parser')
    for x in soup(['script','style','noscript','svg']): x.decompose()
    out=[]
    title=clean_text(soup.title.get_text(' ',strip=True)) if soup.title else ''
    if title: out.append({'kind':'title','text':title,'source':source})
    for key in ('description','og:description','og:title','keywords'):
        tag=soup.find('meta',attrs={'name':key}) or soup.find('meta',attrs={'property':key})
        if tag and tag.get('content'): out.append({'kind':'meta','text':clean_text(tag['content']),'source':source})
    for tag in soup.find_all(['h1','h2','h3','p','li'])[:100]:
        t=clean_text(tag.get_text(' ',strip=True))
        if len(t)>=25: out.append({'kind':tag.name,'text':t[:700],'source':source})
    return out

def zip_extract(data: bytes) -> tuple[list[dict], list[str]]:
    if len(data)>MAX_ZIP: raise HTTPException(413,'ZIP excede o limite de 50 MB.')
    try: z=zipfile.ZipFile(io.BytesIO(data))
    except Exception: raise HTTPException(400,'Arquivo ZIP inválido ou corrompido.')
    infos=z.infolist()
    if len(infos)>MAX_FILES: raise HTTPException(413,f'O ZIP contém mais de {MAX_FILES} arquivos.')
    if sum(i.file_size for i in infos)>MAX_TOTAL_UNCOMPRESSED: raise HTTPException(413,'O conteúdo descompactado excede 100 MB.')
    entries=[]; names=[]
    for info in infos:
        name=info.filename.replace('\\','/')
        if info.is_dir() or name.startswith('/') or '..' in name.split('/') or info.flag_bits & 1: continue
        names.append(name)
        ext='.'+name.rsplit('.',1)[-1].lower() if '.' in name else ''
        if ext not in TEXT_EXTS or info.file_size>1_500_000: continue
        try:
            raw=z.read(info)
            txt=raw.decode('utf-8-sig',errors='replace')
            if ext in ('.html','.htm'): entries.extend(extract_html(txt, f'ZIP:{name}'))
            elif ext in ('.json',) and name.lower().endswith('package.json'):
                try:
                    pkg=json.loads(txt)
                    bits=[f"Projeto: {pkg.get('name')}" if pkg.get('name') else '',f"Descrição: {pkg.get('description')}" if pkg.get('description') else '', 'Dependências: '+', '.join(list((pkg.get('dependencies') or {}).keys())[:25]) if pkg.get('dependencies') else '']
                    for b in bits:
                        if b: entries.append({'kind':'manifest','text':b,'source':f'ZIP:{name}'})
                except Exception: pass
            else:
                lines=[clean_text(x) for x in txt.splitlines()]
                for line in lines[:120]:
                    if len(line)>=35 and not line.startswith(('import ','export ','function ','const ','let ','var ','//','/*','* ')):
                        entries.append({'kind':'file-text','text':line[:700],'source':f'ZIP:{name}'})
        except Exception: continue
    return entries,names

def analyze(entries: list[dict], url: str|None, filenames: list[str]) -> dict:
    # Deduplicate evidence while preserving traceable source snippets.
    seen=set(); evidence=[]
    for e in entries:
        t=e['text']
        k=t.lower()
        if k not in seen:
            seen.add(k); evidence.append(e)
    corpus=' '.join(e['text'] for e in evidence)
    lower=corpus.lower()
    name=''
    for e in evidence:
        if e['kind'] in ('title','meta') and len(e['text'])<120:
            name=e['text']; break
    if not name and evidence: name=evidence[0]['text'][:90]
    type_rules=[('software/aplicativo',r'\b(app|aplicativo|software|sistema|plataforma|dashboard|painel)\b'),('curso digital',r'\b(curso|aulas|módulo|modulo|aprenda|capacitação)\b'),('e-book/material digital',r'\b(e-book|ebook|livro digital|apostila|pdf)\b'),('serviço profissional',r'\b(consultoria|mentoria|assessoria|serviço|servico)\b'),('produto físico',r'\b(produto físico|produto fisico|frete|estoque|tamanho|material)\b')]
    scores=[(label,len(re.findall(pattern,lower))) for label,pattern in type_rules]
    product_type=max(scores,key=lambda x:x[1])[0] if scores and max(x[1] for x in scores)>0 else 'não identificado'
    facts=[]
    for e in evidence:
        if e['kind'] in ('title','meta','h1','h2','h3'):
            facts.append({'claim':e['text'],'evidence':e['source']+' · '+e['kind'],'status':'comprovada no material','basis':'Trecho encontrado na fonte analisada.'})
    # Extract explicit features from lists and sentences containing feature verbs.
    feature_terms=('oferece','permite','inclui','contém','possui','disponibiliza','funcionalidade','recurso','módulo','modulo')
    for e in evidence:
        if any(term in e['text'].lower() for term in feature_terms) and len(e['text'])<400:
            facts.append({'claim':e['text'],'evidence':e['source'],'status':'declarada na fonte','basis':'A própria fonte descreve esta característica; não houve teste independente do recurso.'})
    facts=facts[:24]
    inferences=[]
    if product_type!='não identificado': inferences.append({'claim':f'O material parece descrever {product_type}.','basis':'Classificação heurística por palavras encontradas no conteúdo.','confidence':'média' if max(x[1] for x in scores)>1 else 'baixa'})
    if any(w in lower for w in ('preço','preco','r$','parcelamento','comprar','checkout')): inferences.append({'claim':'Há indícios de oferta comercial ou fluxo de compra.','basis':'Termos comerciais encontrados; não comprovam que o checkout esteja ativo.','confidence':'média'})
    if any(w in lower for w in ('whatsapp','instagram','facebook','contato')): inferences.append({'claim':'A fonte menciona canais de contato ou divulgação.','basis':'Menções textuais detectadas.','confidence':'baixa'})
    pending=[]
    if not name: pending.append('Nome oficial do produto não foi identificado com segurança.')
    if not any(e['kind']=='meta' for e in evidence): pending.append('Descrição comercial resumida não foi encontrada em metadados; confirme a proposta do produto.')
    if not any(w in lower for w in ('preço','preco','r$','valor','gratuito','grátis','gratis')): pending.append('Preço, condições de pagamento e modelo de acesso precisam ser confirmados.')
    if not any(w in lower for w in ('público','publico','para quem','empreendedor','professor','aluno','empresa')): pending.append('Público-alvo não foi identificado; confirme antes de direcionar anúncios.')
    if not facts: pending.append('Pouco conteúdo textual foi encontrado. Envie documentação, imagens com texto ou uma descrição manual complementar.')
    return {'product_name':name or 'Produto não identificado','product_type':product_type,'summary':(evidence[0]['text'] if evidence else 'Não foi possível extrair texto útil das fontes.')[:500], 'confirmed':facts,'inferred':inferences,'pending':pending,'sources':{'site':url,'zip_files':filenames[:80]},'evidence_count':len(evidence),'method':'Extração e classificação heurística local; sem modelo generativo externo nesta API.'}

@app.get('/health')
def health(): return {'status':'ok','service':'DivulgaCerto Product Intelligence','version':'2.2.0'}

@app.post('/api/analyze')
async def analyze_product(site_url: str|None=Form(default=None), file: UploadFile|None=File(default=None)):
    if not site_url and not file: raise HTTPException(400,'Informe um endereço de site, envie um ZIP ou forneça ambos.')
    entries=[]; filenames=[]; final_url=None
    if site_url:
        final_url, page=await fetch_site(site_url)
        entries.extend(extract_html(page,final_url))
    if file:
        if not file.filename or not file.filename.lower().endswith('.zip'): raise HTTPException(415,'Envie um arquivo .zip.')
        data=await file.read(MAX_ZIP+1)
        zip_entries,filenames=zip_extract(data); entries.extend(zip_entries)
    return analyze(entries,final_url,filenames)


# DivulgaCerto 2.2 — rastreamento de cliques e conversões por webhook.
# Configure no Render: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e DIVULGACERTO_WEBHOOK_TOKEN.
class TrackingRegistration(BaseModel):
    campaign_id: str
    destination: str

class ConversionEvent(BaseModel):
    campaign_id: str
    order_id: str
    amount: float | None = None
    currency: str = "BRL"
    status: str = "approved"
    source: str = "webhook"

def _supabase_env():
    url=os.getenv("SUPABASE_URL","").rstrip("/")
    key=os.getenv("SUPABASE_SERVICE_ROLE_KEY","")
    if not url or not key:
        raise HTTPException(503,"Rastreamento indisponível: configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no serviço.")
    return url,key

async def _sb_request(method: str, path: str, *, params=None, json_body=None, prefer=None, token=None):
    url,key=_supabase_env()
    headers={"apikey":key,"Authorization":f"Bearer {token or key}","Content-Type":"application/json"}
    if prefer: headers["Prefer"]=prefer
    async with httpx.AsyncClient(timeout=12) as client:
        response=await client.request(method,url+"/rest/v1/"+path,params=params,json=json_body,headers=headers)
    if response.status_code>=400:
        raise HTTPException(502,"Falha ao consultar o banco de métricas. Verifique a migração SQL e as variáveis do Supabase.")
    return response

async def _authenticated_user(access_token: str) -> str:
    url,key=_supabase_env()
    async with httpx.AsyncClient(timeout=10) as client:
        r=await client.get(url+"/auth/v1/user",headers={"apikey":key,"Authorization":"Bearer "+access_token})
    if r.status_code!=200: raise HTTPException(401,"Sessão inválida. Entre novamente com sua conta Google.")
    return str(r.json().get("id") or "")

@app.post("/api/tracking/register")
async def register_tracking_link(payload: TrackingRegistration, credentials: HTTPAuthorizationCredentials|None=Depends(bearer_scheme)):
    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(401,"Entre com sua conta para criar um link rastreável.")
    user_id=await _authenticated_user(credentials.credentials)
    destination=public_url(payload.destination)
    token=uuid.uuid4().hex
    await _sb_request("POST","divulgacerto_tracking_links",json_body={"token":token,"campaign_id":payload.campaign_id,"user_id":user_id,"destination":destination},prefer="resolution=merge-duplicates,return=minimal")
    base=os.getenv("PUBLIC_API_URL","https://divulgacerto-product-intelligence.onrender.com").rstrip("/")
    return {"tracking_url":base+"/r/"+token,"campaign_id":payload.campaign_id}

@app.get("/r/{token}")
async def track_click(token: str):
    if not re.fullmatch(r"[a-f0-9]{32}",token): raise HTTPException(404,"Link não encontrado.")
    rows=(await _sb_request("GET","divulgacerto_tracking_links",params={"token":"eq."+token,"select":"campaign_id,user_id,destination","limit":"1"})).json()
    if not rows: raise HTTPException(404,"Link de campanha não encontrado.")
    row=rows[0]
    await _sb_request("POST","divulgacerto_click_events",json_body={"token":token,"campaign_id":row["campaign_id"],"user_id":row["user_id"]},prefer="return=minimal")
    return RedirectResponse(row["destination"],status_code=302)

@app.get("/api/tracking/stats/{campaign_id}")
async def tracking_stats(campaign_id: str, credentials: HTTPAuthorizationCredentials|None=Depends(bearer_scheme)):
    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(401,"Entre com sua conta para consultar as métricas.")
    user_id=await _authenticated_user(credentials.credentials)
    owned=(await _sb_request("GET","divulgacerto_tracking_links",params={"campaign_id":"eq."+campaign_id,"user_id":"eq."+user_id,"select":"token","limit":"1"})).json()
    if not owned: raise HTTPException(404,"Campanha sem link rastreável ou não pertence a esta conta.")
    rows=(await _sb_request("GET","divulgacerto_click_events",params={"campaign_id":"eq."+campaign_id,"user_id":"eq."+user_id,"select":"id,created_at"})).json()
    conversions=(await _sb_request("GET","divulgacerto_conversion_events",params={"campaign_id":"eq."+campaign_id,"select":"order_id,amount,currency,created_at"})).json()
    revenue=sum(float(x.get("amount") or 0) for x in conversions)
    return {"campaign_id":campaign_id,"clicks":len(rows),"conversions":len(conversions),"revenue":round(revenue,2),"events":rows}

@app.post("/api/webhooks/conversion")
async def conversion_webhook(payload: ConversionEvent, x_webhook_token: str|None=Header(default=None)):
    expected=os.getenv("DIVULGACERTO_WEBHOOK_TOKEN","")
    if not expected or x_webhook_token!=expected: raise HTTPException(401,"Webhook não autorizado.")
    if payload.status.lower() not in {"approved","paid","completed","approved_payment"}:
        return {"received":True,"recorded":False,"reason":"status_not_confirmed"}
    if payload.amount is not None and payload.amount<0: raise HTTPException(422,"Valor inválido.")
    await _sb_request("POST","divulgacerto_conversion_events",json_body={"campaign_id":payload.campaign_id,"order_id":payload.order_id,"amount":payload.amount,"currency":payload.currency,"source":payload.source},prefer="resolution=ignore-duplicates,return=minimal")
    return {"received":True,"recorded":True,"campaign_id":payload.campaign_id}
