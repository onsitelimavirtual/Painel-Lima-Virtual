import io, zipfile
from analyzer_service import extract_html, zip_extract, analyze

def test_extract_html_and_evidence():
    html='<html><head><title>Loja Teste</title><meta name="description" content="Sistema de gestão para pequenas empresas"></head><body><h1>Gestão simples</h1><p>O sistema permite cadastrar clientes e emitir relatórios.</p></body></html>'
    entries=extract_html(html,'https://example.com')
    result=analyze(entries,'https://example.com',[])
    assert result['product_name']=='Loja Teste'
    assert result['confirmed']
    assert result['pending']

def test_zip_without_extracting_files():
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,'w') as z:
        z.writestr('README.md','# Meu App\n\nAplicativo para organizar tarefas e projetos com relatórios e calendário.')
        z.writestr('package.json','{"name":"meu-app","description":"Sistema web para tarefas"}')
    entries,names=zip_extract(mem.getvalue())
    result=analyze(entries,None,names)
    assert 'README.md' in names
    assert result['evidence_count']>0

def test_empty_sources_are_pending_not_invented():
    result=analyze([],None,[])
    assert result['product_name']=='Produto não identificado'
    assert result['pending']
    assert result['confirmed']==[]


def test_zip_rejects_invalid_archive():
    import pytest
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as err:
        zip_extract(b"not-a-zip")
    assert err.value.status_code == 400

def test_zip_ignores_path_traversal_and_binary_payloads():
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,'w') as z:
        z.writestr('../outside.txt','must not be read')
        z.writestr('assets/payload.exe','not executable')
        z.writestr('docs/readme.md','This product provides a simple customer management dashboard and reporting tools.')
    entries,names=zip_extract(mem.getvalue())
    assert '../outside.txt' not in names
    assert not any('must not be read' in e['text'] for e in entries)
    assert any('customer management' in e['text'] for e in entries)
