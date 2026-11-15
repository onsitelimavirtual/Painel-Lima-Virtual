(() => {
  const $ = id => document.getElementById(id);
  let latest = null;
  const apiBase = (window.APP_CONFIG?.PRODUCT_API_URL || '').replace(/\/$/, '');
  const safe = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function list(items, kind){
    if(!items?.length) return '<p class="muted">Nenhum item identificado nesta categoria.</p>';
    return items.map(x => {
      const claim=typeof x==='string'?x:x.claim;
      const meta=typeof x==='string'?'':[x.evidence||x.basis||'',x.confidence?'Confiança: '+x.confidence:''].filter(Boolean).join(' · ');
      return `<div class="evidence-item">${safe(claim)}${meta?`<small>${safe(meta)}</small>`:''}</div>`;
    }).join('');
  }
  function buildMaterials(p){
    const name=p.product_name||'Produto';
    const facts=(p.confirmed||[]).slice(0,3).map(x=>x.claim);
    const pending=(p.pending||[]).length;
    const base=facts.join(' ');
    const url=p.sources?.site||'';
    const hook=`Conheça ${name}: uma proposta que merece sua atenção.`;
    const wa=`Olá! Quero apresentar ${name}. ${base} ${url?'Saiba mais: '+url:''}\n\nSe quiser, posso enviar mais informações.`;
    const ig=`${hook}\n\n${base}\n\nConheça os detalhes e veja se faz sentido para você. ${url}\n\n#empreendedorismo #negocios #solucoes`;
    const fb=`${name}\n\n${base}\n\nDescubra os detalhes da proposta. Acesse: ${url}`;
    const carousel=[`1. Capa: ${name}`,`2. O que é: ${p.summary||'Apresentação do produto'}`,`3. Características: ${facts[0]||'Inserir característica confirmada'}`,`4. Como conhecer: ${url||'Inserir link oficial'}`,`5. Chamada: Saiba mais`].join('\n');
    const reel=`ROTEIRO DE VÍDEO CURTO\nAbertura (0–3s): Você conhece ${name}?\nApresentação (3–10s): ${p.summary||base}\nDemonstração (10–20s): Mostrar na tela as características confirmadas: ${facts.join('; ')||'demonstrar o produto real'}.\nEncerramento: ${url?'Acesse '+url:'Inclua o link oficial'}\n\nNão afirmar benefícios, resultados ou funcionalidades não demonstrados.`;
    const visual=`BRIEFING VISUAL\nFormato: peça quadrada e vertical para redes sociais.\nProduto: ${name}\nMensagem principal: ${hook}\nElementos visuais: capturas reais do produto, identidade da marca e chamada para ação.\nEvitar: números, depoimentos, selos ou promessas sem comprovação.\n\nPendências a resolver antes da publicação: ${pending}.`;
    return [{title:'WhatsApp · abordagem pessoal',text:wa},{title:'Instagram · legenda',text:ig},{title:'Facebook · publicação',text:fb},{title:'Carrossel · 5 telas',text:carousel},{title:'Reels · roteiro',text:reel},{title:'Briefing visual',text:visual}];
  }
  function svgEscape(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));}
  function promoSvg(p){const title=svgEscape(p.product_name||'Seu produto');const desc=svgEscape((p.summary||'Conheça esta solução').slice(0,115));const site=svgEscape(p.sources?.site||'');return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080"><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#101d3a"/><stop offset="1" stop-color="#173d79"/></linearGradient><linearGradient id="gold"><stop stop-color="#fff0a8"/><stop offset="1" stop-color="#d99b27"/></linearGradient></defs><rect width="1080" height="1080" rx="48" fill="url(#bg)"/><circle cx="930" cy="130" r="250" fill="#1f65bd" opacity=".22"/><path d="M80 160H1000" stroke="url(#gold)" stroke-width="5"/><text x="82" y="115" fill="#f4d47d" font-family="Arial,sans-serif" font-size="34" letter-spacing="8">DIVULGACERTO</text><text x="82" y="370" fill="#fff" font-family="Arial,sans-serif" font-size="74" font-weight="700">${title.slice(0,45)}</text><foreignObject x="84" y="435" width="900" height="250"><div xmlns="http://www.w3.org/1999/xhtml" style="font:36px Arial,sans-serif;color:#dbe8ff;line-height:1.35">${desc}</div></foreignObject><rect x="82" y="760" width="450" height="92" rx="18" fill="url(#gold)"/><text x="125" y="820" fill="#14213d" font-family="Arial,sans-serif" font-size="32" font-weight="700">SAIBA MAIS</text><text x="82" y="955" fill="#b9c9e5" font-family="Arial,sans-serif" font-size="22">${site.slice(0,65)}</text><text x="82" y="1015" fill="#f4d47d" font-family="Arial,sans-serif" font-size="19">Arte-base editável · revise antes de publicar</text></svg>`;}
  function render(p){
    $('intel-results').classList.remove('hidden');$('intel-product-name').textContent=p.product_name||'Produto não identificado';$('intel-summary').textContent=p.summary||'Não foi possível extrair resumo.';$('intel-type').textContent=p.product_type||'Tipo não identificado';$('intel-method').textContent=`Método: ${p.method||'análise automática'} · Trechos analisados: ${p.evidence_count??'não informado'}`;
    $('intel-confirmed').innerHTML=list(p.confirmed,'confirmed');$('intel-inferred').innerHTML=list(p.inferred,'inferred');$('intel-pending').innerHTML=list(p.pending,'pending');
    const mats=buildMaterials(p);$('intel-materials').innerHTML=mats.map(m=>`<article class="material-card"><h3>${safe(m.title)}</h3><p>${safe(m.text)}</p></article>`).join('');$('intel-visual-preview').innerHTML=promoSvg(p);
  }
  $('analyze-btn').addEventListener('click',async()=>{
    $('intel-error').textContent='';$('intel-progress').textContent='';$('intel-results').classList.add('hidden');
    const site=$('intel-site').value.trim();const file=$('intel-zip').files[0];
    if(!site&&!file){$('intel-error').textContent='Informe um site, selecione um ZIP ou forneça ambos.';return;}
    if(site){try{const u=new URL(site);if(!['http:','https:'].includes(u.protocol))throw Error();}catch{$('intel-error').textContent='O endereço deve ser uma URL válida iniciada por http:// ou https://.';return;}}
    if(file && (!file.name.toLowerCase().endsWith('.zip')||file.size>50*1024*1024)){$('intel-error').textContent='Selecione um ZIP válido de até 50 MB.';return;}
    if(!apiBase){$('intel-error').textContent='O serviço de análise ainda não está conectado. Configure PRODUCT_API_URL em config.js e publique a API de análise. O restante do MVP continua funcionando localmente.';return;}
    const fd=new FormData();if(site)fd.append('site_url',site);if(file)fd.append('file',file);
    $('analyze-btn').disabled=true;$('intel-progress').textContent='Analisando as fontes. Isso pode levar alguns instantes…';
    try{const r=await fetch(apiBase+'/api/analyze',{method:'POST',body:fd});const data=await r.json();if(!r.ok)throw new Error(data.detail||'Falha ao analisar as fontes.');latest=data;render(data);$('intel-progress').textContent='Análise concluída. Revise as evidências e as pendências antes de gerar a campanha.';}
    catch(e){$('intel-error').textContent=e.message||'Não foi possível concluir a análise. Verifique a conexão e tente novamente.';$('intel-progress').textContent='';}
    finally{$('analyze-btn').disabled=false;}
  });
  $('use-analysis-btn').addEventListener('click',()=>{if(!latest)return;window.applyProductAnalysis?.(latest);});
  $('download-visual-btn').addEventListener('click',()=>{if(!latest)return;const blob=new Blob([promoSvg(latest)],{type:'image/svg+xml;charset=utf-8'});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='divulgacerto-arte-promocional.svg';a.click();URL.revokeObjectURL(u);});
  $('export-analysis-btn').addEventListener('click',()=>{if(!latest)return;const blob=new Blob([JSON.stringify(latest,null,2)],{type:'application/json'});const a=document.createElement('a');const u=URL.createObjectURL(blob);a.href=u;a.download='divulgacerto-analise-produto.json';a.click();URL.revokeObjectURL(u);});
  // Carry inputs from the campaign form shortcut to the complete analyzer.
  document.querySelectorAll('[data-view="intelligence"]').forEach(b=>b.addEventListener('click',()=>{if($('source-site')?.value)$('intel-site').value=$('source-site').value;if($('source-zip')?.files?.[0]){const dt=new DataTransfer();dt.items.add($('source-zip').files[0]);$('intel-zip').files=dt.files;}}));
})();
