from pathlib import Path
import re
import shutil

p = Path.home() / "OffTecAI/offtec_web.py"
src = p.read_text()
backup = p.with_suffix(".py.backup")
shutil.copy2(p, backup)

# 1. Permitir arquivos na workspace ou na home.
start = src.index("def safe_file(name):")
end = src.index("\ndef start_model():", start)

safe = '''def safe_file(name, location="workspace"):
    if not isinstance(name, str) or name != Path(name).name:
        raise ValueError("Nome de arquivo inválido.")
    if not name or name.startswith(".") or any(c in name for c in "/\\\\"):
        raise ValueError("Use um nome simples, sem caminhos.")
    if Path(name).suffix.lower() not in (".py", ".txt", ".md", ".html", ".js", ".json"):
        raise ValueError("Extensão não permitida.")
    root = HOME if location == "home" else WORK
    return root / name
'''
src = src[:start] + safe + src[end:]

# 2. Fazer o chat criar arquivos e solicitar confirmação para executar.
start = src.index('            if self.path == "/api/chat":')
end = src.index('            elif self.path == "/api/create":', start)

chat = '''            if self.path == "/api/chat":
                msg = str(data.get("message", ""))[:6000]
                low = msg.lower()

                match = re.search(
                    r"([a-zA-Z0-9_.-]+\\\\.(?:py|txt|md|html|js|json))",
                    msg
                )
                filename = match.group(1) if match else None
                location = "home" if re.search(
                    r"\\\\b(home|pasta pessoal|diret[oó]rio pessoal)\\\\b", low
                ) else "workspace"

                # Pedidos explícitos para executar um arquivo.
                wants_run = bool(re.search(
                    r"\\\\b(execut[ae]|rod[ae]|inicie|iniciar)\\\\b", low
                ))
                if wants_run and filename:
                    self.send_json({
                        "reply": "Posso executar " + filename +
                                 " após sua confirmação.",
                        "action": "run",
                        "name": filename,
                        "location": location
                    })
                    return

                # Pedidos para criar ou salvar um arquivo.
                wants_create = bool(re.search(
                    r"\\\\b(crie|criar|cria|gere|gerar|salve|salvar|escreva)\\\\b",
                    low
                ))
                if wants_create and filename:
                    prompt = (
                        "Gere o conteúdo COMPLETO de um único arquivo chamado "
                        + filename + ". Pedido do usuário: " + msg +
                        "\\\\nResponda somente com o código do arquivo, dentro "
                        "de um bloco Markdown com a linguagem apropriada. "
                        "Não inclua explicações fora do bloco."
                    )
                    payload = json.dumps({
                        "messages": [
                            {"role": "system", "content":
                             "Você é OffTec AI, assistente de programação. "
                             "Gere código completo, simples e seguro. "
                             "Não invente que executou ferramentas."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 900
                    }).encode()
                    req = urllib.request.Request(
                        API + "/v1/chat/completions",
                        data=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=240) as res:
                        result = json.loads(res.read())
                    answer = result["choices"][0]["message"]["content"]
                    block = re.search(
                        r"```(?:[a-zA-Z0-9_+.-]+)?\\\\s*\\\\n(.*?)```",
                        answer, re.S
                    )
                    if not block:
                        self.send_json({
                            "reply": "Não encontrei um bloco de código completo. "
                                     "Peça para gerar o arquivo novamente."
                        })
                        return
                    content = block.group(1).strip() + "\\\\n"
                    if len(content) > 100000:
                        self.send_json({"error": "Código gerado muito grande."}, 413)
                        return
                    target = safe_file(filename, location)
                    if target.exists():
                        self.send_json({
                            "reply": "O arquivo " + str(target) +
                                     " já existe. Renomeie-o ou faça backup antes."
                        })
                        return
                    target.write_text(content)
                    self.send_json({
                        "reply": "Arquivo criado com sucesso: " + str(target) +
                                 "\\\\nRevise o código antes de executá-lo."
                    })
                    return

                payload = json.dumps({
                    "messages": [
                        {"role": "system", "content":
                         "Você é OffTec AI, um assistente de programação em português. "
                         "Ajude a escrever, explicar e depurar código. Seja prático. "
                         "Você só pode afirmar que criou ou executou um arquivo "
                         "quando o sistema confirmar essa ação."},
                        {"role": "user", "content": msg}
                    ],
                    "temperature": 0.3, "max_tokens": 700
                }).encode()
                req = urllib.request.Request(
                    API + "/v1/chat/completions", data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=240) as res:
                    result = json.loads(res.read())
                self.send_json({
                    "reply": result["choices"][0]["message"]["content"]
                })
'''
src = src[:start] + chat + src[end:]

# 3. Aceitar o destino home/workspace nos endpoints de criação e execução.
src = src.replace(
    'p = safe_file(data.get("name", ""))\\n                content =',
    'p = safe_file(data.get("name", ""), data.get("location", "workspace"))\\n                content ='
)
src = src.replace(
    'p = safe_file(data.get("name", ""))\\n                if p.suffix != ".py"',
    'p = safe_file(data.get("name", ""), data.get("location", "workspace"))\\n                if p.suffix != ".py"'
)

# 4. Ligar o pedido de execução à confirmação do navegador.
old = "const d=await r.json();bubble.lastChild.textContent=d.error||d.reply||'Sem resposta.';"
new = """const d=await r.json();bubble.lastChild.textContent=d.error||d.reply||'Sem resposta.';
  if(d.action==='run' && confirm('Executar '+d.name+'? Confira o código antes.')){
   const rr=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:d.name,location:d.location})});
   const result=await rr.json();
   addMsg('ai','Resultado da execução de '+d.name+':\\\\n'+(result.error||result.output||'(Sem saída)'));
  }"""
if old not in src:
    raise SystemExit("Não encontrei o trecho do chat. Backup preservado; arquivo original não foi alterado.")
src = src.replace(old, new, 1)

p.write_text(src)
print("Atualização aplicada:", p)
print("Backup:", backup)
