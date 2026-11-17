#!/usr/bin/env python3
"""Validação estática dos scripts JavaScript inline dos documentos HTML."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_TYPES = {"application/json", "application/ld+json", "importmap", "speculationrules"}

class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script" or self.current is not None:
            return
        attrs = dict(attrs)
        if attrs.get("src"):
            return
        kind = (attrs.get("type") or "").split(";")[0].strip().lower()
        if kind in SKIP_TYPES:
            return
        self.current = []
    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)
    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.current is not None:
            code = "".join(self.current).strip()
            if code:
                self.blocks.append(code)
            self.current = None

def main():
    node = subprocess.run(["node", "--version"], capture_output=True, text=True)
    if node.returncode:
        print("ERRO: Node.js não está disponível.")
        return 2
    files = sorted(ROOT.rglob("*.html"))
    failures = []
    checked = 0
    with tempfile.TemporaryDirectory() as temp:
        tempdir = Path(temp)
        for html in files:
            parser = ScriptCollector()
            try:
                parser.feed(html.read_text(encoding="utf-8", errors="replace"))
            except Exception as exc:
                failures.append(f"{html.relative_to(ROOT)}: HTML não pôde ser analisado: {exc}")
                continue
            for index, code in enumerate(parser.blocks, 1):
                checked += 1
                js = tempdir / f"inline-{checked}.js"
                js.write_text(code, encoding="utf-8")
                result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
                if result.returncode:
                    failures.append(f"{html.relative_to(ROOT)} [script {index}]: {result.stderr.strip()}")
    print(f"HTML analisados: {len(files)}")
    print(f"Scripts inline verificados: {checked}")
    print(f"Node.js: {node.stdout.strip()}")
    if failures:
        print("\nFALHAS:")
        print("\n".join(failures))
        return 1
    print("Resultado: validação sintática aprovada.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
