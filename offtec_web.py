import json
import re
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

HOME = Path.home()
BASE = HOME / "OffTecAI"
WORK = BASE / "workspace"
MODEL = HOME / "modelos/qwen/qwen.gguf"
SERVER = HOME / "llama.cpp/build/bin/llama-server"
API = "http://127.0.0.1:8080"
BASE.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)
server_process = None

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<meta name="theme-color" content="#080b09">
<title>OffTec AI</title>
<style>
:root{--bg:#080b09;--panel:#0e130f;--line:#202b22;--green:#7cff8a;--muted:#849487;--white:#edf7ef}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--white);font:15px system-ui,Arial}
button,input,textarea{font:inherit}
button{cursor:pointer}
.app{display:flex;min-height:100dvh}
aside{width:230px;background:#0b0f0c;border-right:1px solid var(--line);padding:22px 14px;display:flex;flex-direction:column;gap:20px}
.brand{font-weight:900;font-size:22px;letter-spacing:1px}
.brand span{color:var(--green)}
.tag{font-size:10px;color:var(--muted);letter-spacing:2px;margin-top:4px}
.status{border:1px solid var(--line);background:var(--panel);border-radius:12px;padding:12px;font-size:12px;color:var(--muted)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#777;margin-right:7px}
nav{display:grid;gap:8px}
nav button,.secondary{background:transparent;color:#b8c7ba;border:1px solid transparent;text-align:left;border-radius:10px;padding:12px}
nav button.active,nav button:hover{background:#142219;border-color:#254b2d;color:var(--green)}
.small{font-size:11px;color:var(--muted);line-height:1.6}
main{flex:1;min-width:0;display:flex;flex-direction:column;min-height:100dvh}
.top{height:65px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 22px}
.top b{font-size:14px}
.pill{font-size:11px;color:var(--green);border:1px solid #244b2c;border-radius:30px;padding:6px 10px}
.content{width:100%;max-width:900px;margin:0 auto;padding:28px 20px;flex:1}
.welcome{padding:25px 0 22px}
.eyebrow{color:var(--green);font-size:11px;letter-spacing:2px;font-weight:700}
h1{font-size:clamp(27px,5vw,42px);line-height:1.12;margin:12px 0}
h1 em{color:var(--green);font-style:normal}
.muted{color:var(--muted);line-height:1.6}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:22px 0}
.card{border:1px solid var(--line);background:linear-gradient(145deg,#111812,#0b0f0c);border-radius:15px;padding:17px;text-align:left;color:var(--white);min-height:100px}
.card:hover{border-color:#3c7846;transform:translateY(-1px)}
.ico{font-size:21px;margin-bottom:10px}
.card b{display:block;font-size:14px}
.card small{display:block;color:var(--muted);margin-top:5px}
.chat{display:flex;flex-direction:column;gap:14px;padding-bottom:18px}
.msg{padding:14px 16px;border-radius:14px;line-height:1.65;white-space:pre-wrap;overflow-wrap:anywhere}
.msg.user{align-self:flex-end;max-width:90%;background:#17321e;border:1px solid #285a32}
.msg.ai{align-self:stretch;background:#0e130f;border:1px solid var(--line)}
.msg .who{font-size:10px;color:var(--green);letter-spacing:1px;margin-bottom:7px;font-weight:800}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#050806;border:1px solid #263329;padding:12px;border-radius:9px;overflow-x:auto}
.composer{position:sticky;bottom:0;background:linear-gradient(transparent,var(--bg) 20%);padding:15px 0 8px}
.composebox{display:flex;gap:9px;background:#101611;border:1px solid #2a382d;border-radius:15px;padding:10px}
textarea{flex:1;min-width:0;resize:vertical;min-height:45px;max-height:150px;color:var(--white);background:transparent;border:0;outline:0;padding:10px}
.send{border:0;background:var(--green);color:#061008;border-radius:11px;padding:0 17px;font-weight:900}
.hint{text-align:center;color:#718174;font-size:10px;margin-top:9px}
.panel{display:none}
.panel.show{display:block}
.file{display:flex;gap:8px;align-items:center;justify-content:space-between;border:1px solid var(--line);padding:12px;border-radius:10px;margin:8px 0}
.file button{background:#18251b;color:var(--green);border:1px solid #29452e;padding:7px 10px;border-radius:8px}
.action{background:#132219;border:1px solid #2c4c33;color:var(--green);border-radius:9px;padding:10px 12px;margin:5px 5px 5px 0}
#editor{width:100%;min-height:45vh;background:#070a08;color:#c8f8ce;border:1px solid var(--line);border-radius:12px;padding:14px;font:13px monospace}
input{background:#080c09;border:1px solid var(--line);color:white;padding:11px;border-radius:9px;max-width:100%}
@media(max-width:650px){.app{display:block}aside{width:100%;padding:13px 15px;border-right:0;border-bottom:1px solid var(--line);gap:10px}.brand{font-size:19px}.tag{display:none}.status{padding:8px 10px}nav{display:flex;overflow:auto;gap:5px}nav button{white-space:nowrap;padding:9px;font-size:12px}aside .small{display:none}.top{height:49px;padding:0 15px}.content{padding:18px 14px}.welcome{padding-top:10px}.cards{gap:9px}.card{padding:13px;min-height:95px}.msg{font-size:14px}.composebox{padding:6px}.send{padding:0 13px}}
</style>
</head>
<body>
<div class="app">
<aside>
 <div><div class="brand">OFFTEC <span>AI</span></div><div class="tag">LOCAL INTELLIGENCE</div></div>
 <div class="status"><span class="dot" id="dot"></span><span id="status">Verificando modelo...</span><div style="margin-top:7px">Qwen · processamento local</div></div>
 <nav>
  <button class="active" onclick="page('chat',this)">⌘ &nbsp; Chat com IA</button>
  <button onclick="page('files',this)">▤ &nbsp; Arquivos</button>
  <button onclick="page('editor',this)">⌁ &nbsp; Editor de código</button>
 </nav>
 <div class="small" style="margin-top:auto">OFFTEC AI · TERMUX<br>Seus arquivos ficam no dispositivo.</div>
</aside>
<main>
 <div class="top"><b id="topTitle">Painel de inteligência</b><span class="pill">● LOCAL / OFFLINE</span></div>
 <div class="content">
  <section id="chat" class="panel show">
   <div class="welcome" id="welcome">
    <div class="eyebrow">SEU LABORATÓRIO DE CÓDIGO</div>
    <h1>O que vamos<br><em>construir hoje?</em></h1>
    <p class="muted">Uma IA local para ajudar você a programar diretamente no Android.</p>
    <div class="cards">
     <button class="card" onclick="suggest('Crie um programa Python de calculadora com menu no terminal.')"><div class="ico">⌘</div><b>Criar um programa</b><small>Transforme uma ideia em código</small></button>
     <button class="card" onclick="suggest('Me ajude a encontrar e corrigir erros neste código. Explique o processo.')"><div class="ico">⌕</div><b>Corrigir código</b><small>Depurar e entender erros</small></button>
     <button class="card" onclick="page('files')"><div class="ico">▤</div><b>Meus arquivos</b><small>Visualizar projetos salvos</small></button>
     <button class="card" onclick="page('editor')"><div class="ico">⌁</div><b>Editor de código</b><small>Escrever e salvar arquivos</small></button>
    </div>
   </div>
   <div id="messages" class="chat"></div>
   <div class="composer"><div class="composebox"><textarea id="prompt" placeholder="Peça para a IA criar ou explicar um código..." rows="2"></textarea><button class="send" onclick="send()">➤</button></div><div class="hint">Confira o código antes de executar. O modelo pode cometer erros.</div></div>
  </section>
  <section id="files" class="panel">
   <div class="eyebrow">WORKSPACE LOCAL</div><h1>Seus <em>arquivos</em></h1>
   <p class="muted">Arquivos salvos em ~/OffTecAI/workspace</p>
   <button class="action" onclick="newFile()">＋ Novo arquivo</button><button class="action" onclick="loadFiles()">↻ Atualizar</button>
   <div id="filelist"></div>
  </section>
  <section id="editor" class="panel">
   <div class="eyebrow">EDITOR LOCAL</div><h1>Editor de <em>código</em></h1>
   <p class="muted">Crie ou edite um arquivo dentro do workspace.</p>
   <p><input id="filename" placeholder="exemplo.py"></p>
   <textarea id="code" style="width:100%;min-height:38vh;background:#070a08;color:#c8f8ce;border:1px solid #263329;border-radius:12px;padding:14px;font:13px monospace" placeholder="# Escreva seu código aqui"></textarea>
   <p><button class="action" onclick="saveEditor()">Salvar arquivo</button><button class="action" onclick="runEditor()">▶ Executar Python</button></p>
   <pre id="output" style="display:none"></pre>
  </section>
 </div>
</main>
</div>
<script>
const $=id=>document.getElementById(id);
function page(id,btn){
 document.querySelectorAll('.panel').forEach(x=>x.classList.remove('show'));
 $(id).classList.add('show');
 document.querySelectorAll('nav button').forEach(x=>x.classList.remove('active'));
 if(btn)btn.classList.add('active');
 $('topTitle').textContent={chat:'Painel de inteligência',files:'Gerenciador de arquivos',editor:'Editor de código'}[id];
 if(id==='files')loadFiles();
}
function suggest(t){$('prompt').value=t;$('prompt').focus()}
function addMsg(role,text){
 $('welcome').style.display='none';
 const el=document.createElement('div');el.className='msg '+role;
 const who=document.createElement('div');who.className='who';who.textContent=role==='user'?'VOCÊ':'OFFTEC AI';
 const body=document.createElement('div');body.textContent=text;
 el.append(who,body);$('messages').append(el);el.scrollIntoView({behavior:'smooth',block:'end'});return el;
}
async function send(){
 const text=$('prompt').value.trim();if(!text)return;
 $('prompt').value='';addMsg('user',text);
 const bubble=addMsg('ai','Processando no modelo local...');
 try{
  const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
  const d=await r.json();bubble.lastChild.textContent=d.error||d.reply||'Sem resposta.';
  if(d.action==='run' && confirm('Executar '+d.name+'? Confira o código antes.')){
   const rr=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:d.name,location:d.location})});
   const result=await rr.json();
   addMsg('ai','Resultado da execução de '+d.name+':\\n'+(result.error||result.output||'(Sem saída)'));
  }
 }catch(e){bubble.lastChild.textContent='Erro de conexão: '+e}
}
$('prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
async function loadFiles(){
 const r=await fetch('/api/files');const d=await r.json();const box=$('filelist');box.replaceChildren();
 if(!d.files.length){box.textContent='Nenhum arquivo ainda. Crie seu primeiro arquivo.';return}
 d.files.forEach(f=>{
  const row=document.createElement('div');row.className='file';
  const name=document.createElement('span');name.textContent='▤ '+f;
  const actions=document.createElement('span');
  const open=document.createElement('button');open.textContent='Abrir';open.onclick=()=>openFile(f);
  const run=document.createElement('button');run.textContent='Executar';run.style.marginLeft='5px';run.onclick=()=>runFile(f);
  actions.append(open);if(f.endsWith('.py'))actions.append(run);row.append(name,actions);box.append(row);
 });
}
async function openFile(name){
 const d=await (await fetch('/api/read?name='+encodeURIComponent(name))).json();
 if(d.error)return alert(d.error);
 $('filename').value=name;$('code').value=d.content;page('editor');
}
function newFile(){$('filename').value='novo.py';$('code').value='';page('editor')}
async function saveEditor(){
 const r=await fetch('/api/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:$('filename').value,content:$('code').value})});
 const d=await r.json();alert(d.error||d.message);if(!d.error)loadFiles();
}
async function runEditor(){await runFile($('filename').value)}
async function runFile(name){
 if(!name.endsWith('.py'))return alert('Somente arquivos Python podem ser executados.');
 if(!confirm('Executar '+name+'? Confira o código antes.'))return;
 const out=$('output');out.style.display='block';out.textContent='Executando...';page('editor');
 const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})});
 const d=await r.json();out.textContent=d.error||d.output||'(Sem saída)';
}
async function check(){
 try{const d=await(await fetch('/api/status')).json();$('status').textContent=d.model?'Modelo online':'Modelo indisponível';$('dot').style.background=d.model?'#7cff8a':'#ff6868';}
 catch(e){$('status').textContent='Servidor indisponível'}
}
check();setInterval(check,10000);
</script>
</body></html>"""

def safe_file(name, location="workspace"):
    if not isinstance(name, str) or name != Path(name).name:
        raise ValueError("Nome de arquivo inválido.")
    if not name or name.startswith(".") or any(c in name for c in "/\\"):
        raise ValueError("Use um nome simples, sem caminhos.")
    if Path(name).suffix.lower() not in (".py", ".txt", ".md", ".html", ".js", ".json"):
        raise ValueError("Extensão não permitida.")
    root = HOME if location == "home" else WORK
    return root / name

def start_model():
    global server_process
    try:
        urllib.request.urlopen(API + "/health", timeout=1)
        return
    except Exception:
        pass
    if not SERVER.exists():
        print("ERRO: llama-server não encontrado.")
        print("Execute: cd ~/llama.cpp && cmake --build build --target llama-server -j 2")
        raise SystemExit(1)
    if not MODEL.exists():
        print("ERRO: modelo não encontrado em", MODEL)
        raise SystemExit(1)
    log = open(BASE / "server.log", "a")
    server_process = subprocess.Popen(
        [str(SERVER), "-m", str(MODEL), "-c", "1024", "-t", "2",
         "--host", "127.0.0.1", "--port", "8080"],
        stdout=log, stderr=subprocess.STDOUT
    )
    for _ in range(90):
        time.sleep(1)
        try:
            urllib.request.urlopen(API + "/health", timeout=1)
            print("Modelo Qwen iniciado.")
            return
        except Exception:
            if server_process.poll() is not None:
                break
    print("O modelo não iniciou. Veja ~/OffTecAI/server.log")
    raise SystemExit(1)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        url = urlparse(self.path)
        if url.path == "/":
            raw = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif url.path == "/api/status":
            try:
                urllib.request.urlopen(API + "/health", timeout=2)
                self.send_json({"model": True})
            except Exception:
                self.send_json({"model": False})
        elif url.path == "/api/files":
            self.send_json({"files": sorted(p.name for p in WORK.iterdir() if p.is_file())})
        elif url.path == "/api/read":
            try:
                p = safe_file(parse_qs(url.query).get("name", [""])[0])
                if not p.is_file():
                    raise ValueError("Arquivo não encontrado.")
                self.send_json({"content": p.read_text(errors="replace")})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
        else:
            self.send_error(404)

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 1000000:
                return self.send_json({"error": "Requisição muito grande."}, 413)
            data = json.loads(self.rfile.read(size) or b"{}")
            if self.path == "/api/chat":
                msg = str(data.get("message", ""))[:6000]
                low = msg.lower()

                match = re.search(
                    r"([a-zA-Z0-9_.-]+\.(?:py|txt|md|html|js|json))",
                    msg
                )
                filename = match.group(1) if match else None
                location = "home" if re.search(
                    r"\b(home|pasta pessoal|diret[oó]rio pessoal)\b", low
                ) else "workspace"

                # Pedidos explícitos para executar um arquivo.
                wants_run = bool(re.search(
                    r"\b(execut[ae]|rod[ae]|inicie|iniciar)\b", low
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
                    r"\b(crie|criar|cria|gere|gerar|salve|salvar|escreva)\b",
                    low
                ))
                if wants_create and filename:
                    prompt = (
                        "Gere o conteúdo COMPLETO de um único arquivo chamado "
                        + filename + ". Pedido do usuário: " + msg +
                        "\\nResponda somente com o código do arquivo, dentro "
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
                        r"```(?:[a-zA-Z0-9_+.-]+)?\s*\n(.*?)```",
                        answer, re.S
                    )
                    if not block:
                        self.send_json({
                            "reply": "Não encontrei um bloco de código completo. "
                                     "Peça para gerar o arquivo novamente."
                        })
                        return
                    content = block.group(1).strip() + "\\n"
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
                                 "\\nRevise o código antes de executá-lo."
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
            elif self.path == "/api/create":
                p = safe_file(data.get("name", ""))
                content = str(data.get("content", ""))
                if len(content) > 500000:
                    return self.send_json({"error": "Arquivo muito grande."}, 413)
                p.write_text(content)
                self.send_json({"message": "Arquivo salvo: " + p.name})
            elif self.path == "/api/run":
                p = safe_file(data.get("name", ""))
                if p.suffix != ".py" or not p.is_file():
                    return self.send_json({"error": "Arquivo Python não encontrado."}, 400)
                result = subprocess.run([sys.executable, str(p)], cwd=str(WORK),
                    capture_output=True, text=True, timeout=30)
                output = (result.stdout + result.stderr)[-12000:]
                self.send_json({"output": output or "(Programa finalizado sem saída)",
                                "returncode": result.returncode})
            else:
                self.send_error(404)
        except subprocess.TimeoutExpired:
            self.send_json({"error": "Tempo limite: execução interrompida."}, 408)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

def main():
    start_model()
    server = HTTPServer(("127.0.0.1", 8765), Handler)
    print("\nOFFTEC AI pronto!")
    print("Abra no navegador: http://127.0.0.1:8765")
    print("Somente acessível neste dispositivo. Ctrl+C para sair.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando OffTec AI...")
    finally:
        server.server_close()
        if server_process and server_process.poll() is None:
            server_process.terminate()

if __name__ == "__main__":
    main()
