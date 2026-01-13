import typer
import sqlite3
import pyperclip
import os
import json
import subprocess
from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt # <--- Adicionado Prompt
from rich import print
from typing_extensions import Annotated

app = typer.Typer()
console = Console()

DB_PATH = os.path.expanduser("~/.brain_ai.db")
CONFIG_PATH = os.path.expanduser("~/.brain_config") # <--- Novo arquivo de configuração

def get_api_key():
    """Recupera a chave do ambiente ou do arquivo de configuração."""
    # 1. Tenta variável de ambiente
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key
    
    # 2. Tenta arquivo local (criado pelo brain config)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return f.read().strip()
        except:
            return None
    return None

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- NOVO COMANDO DE CONFIGURAÇÃO ---
@app.command()
def config():
    """⚙ Configura sua Chave de API (Necessário para IA)."""
    console.print(Panel("Vamos configurar sua conexão com a Inteligência Artificial.", title="Configuração", border_style="cyan"))
    
    print("\n1. Crie uma conta grátis em: [link]https://console.groq.com/keys[/link]")
    print("2. Crie uma nova API Key e copie o código (começa com 'gsk_').\n")
    
    key = Prompt.ask("[bold yellow]Cole sua API Key aqui[/bold yellow]", password=True)
    
    if not key.startswith("gsk_"):
        print("[bold red]❌ Isso não parece uma chave válida da Groq (deve começar com 'gsk_').[/bold red]")
        return

    # Salva no arquivo oculto
    with open(CONFIG_PATH, "w") as f:
        f.write(key.strip())
    
    print(f"\n[bold green]✔ Configurado com sucesso![/bold green]")
    print("A chave foi salva em segurança no seu computador.")

def get_detailed_explanation(command_text: str):
    """Gera uma explicação técnica e direta usando a IA."""
    api_key = get_api_key()
    if not api_key:
        return "[red]⚠ Impossível explicar: Chave não configurada. Rode 'brain config' primeiro.[/red]"

    client = Groq(api_key=api_key)
    
    prompt = f"""
    Você é um colega desenvolvedor experiente.
    O usuário quer entender este comando: "{command_text}"
    
    TAREFA: Explique o que ele faz de forma SIMPLES, DIRETA e RESUMIDA em Português.
    Não precisa de tópicos complexos. Diga apenas o objetivo do comando e o resultado prático.
    Se for algo perigoso (como deletar arquivos), avise claramente.
    
    Não use markdown de código (```) na resposta, apenas texto corrido.
    """
    
    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"[red]Erro na conexão com IA: {e}[/red]"

@app.command()
def info():
    """Manual de Instruções (Versão Completa)."""
    
    welcome_text = """
    # 🧠 BRAIN CLI - Personal Assistant
    Bem-vindo ao assistente híbrido: IA Online + Busca Offline + Automação.
    Criado por Jair Rodrigues - [GitHub](https://github.com/JairRodrigue)
    """
    
    table = Table(title="Lista de Comandos", show_header=True, header_style="bold magenta")
    table.add_column("Comando", style="cyan", width=20)
    table.add_column("O que faz", style="white")
    table.add_column("Exemplo de uso", style="dim green")

    table.add_row("brain config", "Configura a chave da IA", "brain config") # <--- Adicionado
    table.add_row("brain add", "Ensina um novo comando", 'brain add "git s" "status"')
    table.add_row("brain list", "Vê tudo que está salvo", "brain list")
    table.add_row("brain explain", "A IA explica um código", 'brain explain "rm -rf /"')
    table.add_row("brain ask '...'", "Busca comando (Online/Offline)", 'brain ask "commitar"')
    table.add_row("brain ask -r", "Busca e EXECUTA", 'brain ask "listar" --run')
    table.add_row("brain export", "Cria backup (JSON)", "brain export backup.json")
    table.add_row("brain import", "Carrega backup", "brain import backup.json")
    table.add_row("brain info", "Mostra esta tela", "brain info")

    console.print(Panel(Markdown(welcome_text), border_style="green"))
    console.print(table)
    console.print("\n[dim]Dica: Use aspas nos textos! Ex: brain ask \"git log\"[/dim]")

@app.command(name="export") 
def export_brain(
    file: Annotated[str, typer.Argument(help="Nome do arquivo de backup")] = "backup_brain.json"
):
    """ Exporta seu conhecimento para um arquivo."""
    init_db()
    conn = get_db()
    items = conn.execute("SELECT command, description FROM commands").fetchall()
    
    data = [{"command": item['command'], "description": item['description']} for item in items]
    
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"[bold green]✔ Sucesso![/bold green] {len(data)} comandos salvos em '{file}'.")

@app.command(name="import")
def import_brain(
    file: Annotated[str, typer.Argument(help="Nome do arquivo para importar")]
):
    """Importa conhecimento de um arquivo JSON."""
    if not os.path.exists(file):
        print(f"[red]Arquivo '{file}' não encontrado.[/red]")
        return
        
    with open(file, 'r') as f:
        data = json.load(f)
        
    init_db()
    conn = get_db()
    count = 0
    for item in data:
        conn.execute("INSERT INTO commands (command, description) VALUES (?, ?)", (item['command'], item['description']))
        count += 1
    conn.commit()
    conn.close()
    
    print(f"[bold green]✔ Importado![/bold green] {count} novos comandos adicionados.")

@app.command()
def explain(
    command_to_explain: Annotated[str, typer.Argument(help="Cole o comando que você quer entender")]
):
    """Explica o que um comando Git/Linux faz (Requer Internet)."""
    print(f"[dim]🔍 Analisando comando...[/dim]")
    explanation = get_detailed_explanation(command_to_explain)
    console.print(Panel(explanation, title=f"[bold yellow]Explicação[/bold yellow]", border_style="blue"))

@app.command()
def add(
    command: Annotated[str, typer.Argument(help="O comando técnico")],
    description: Annotated[str, typer.Argument(help="Explicação do que ele faz")]
):
    """Adiciona um novo conhecimento."""
    init_db()
    conn = get_db()
    conn.execute("INSERT INTO commands (command, description) VALUES (?, ?)", (command, description))
    conn.commit()
    conn.close()
    print(f"[bold green]✔ Salvo![/bold green] Aprendi: {description}")

@app.command()
def list():
    """Lista tudo o que foi aprendido."""
    init_db()
    conn = get_db()
    items = conn.execute("SELECT * FROM commands").fetchall()
    
    if not items:
        print("[yellow]Cérebro vazio. Use 'brain add' para começar.[/yellow]") 
        return

    table = Table(title="Conhecimento Salvo")
    table.add_column("Comando", style="cyan")
    table.add_column("Descrição", style="magenta")
    for item in items:
        table.add_row(item['command'], item['description'])
    console.print(table)

@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="O que você quer fazer?")],
    run: Annotated[bool, typer.Option("--run", "-r", help="Executa o comando automaticamente após confirmação")] = False
):
    """Busca Híbrida: IA (Online) ou Local (Offline) + Execução."""
    
    if not question or len(question.strip()) < 2:
        print("[yellow]⚠ A pergunta está muito curta. Tente algo como 'listar arquivos' ou 'git commit'.[/yellow]")
        return

    init_db()
    api_key = get_api_key()
    conn = get_db()
    result = None

    if api_key:
        try:
            print(f"[dim]☁ Conectando à IA...[/dim]")
            client = Groq(api_key=api_key)
            
            data = conn.execute("SELECT command, description FROM commands").fetchall()
            if not data:
                 context_list = "Nenhum comando salvo pelo usuário."
            else:
                 context_list = "\n".join([f"- Comando: '{row['command']}' | Descrição: '{row['description']}'" for row in data])
            
            prompt = f"""
            Você é um GERADOR DE COMANDOS LINUX (Bash).
            MEUS COMANDOS SALVOS:
            {context_list}
            PEDIDO: "{question}"
            REGRAS:
            1. Retorne APENAS o código executável. Sem markdown.
            2. Se forem múltiplos passos, use ' && '.
            3. Se não conseguir, responda "ERRO".
            """
            
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0, 
            )
            candidate = chat_completion.choices[0].message.content.strip().replace("`", "")
            
            if "ERRO" not in candidate and "sinto muito" not in candidate.lower():
                result = candidate

        except Exception:
            print("[yellow]⚠ Sem conexão com a IA. Tentando busca local...[/yellow]")
    else:
        # Se não tem chave, avisa e segue para local
        print("[dim]⚠ IA não configurada (use 'brain config'). Buscando local...[/dim]")
    
    if not result:
        print(f"[dim]Buscando no disco local...[/dim]")
        cursor = conn.execute("SELECT command FROM commands WHERE description LIKE ? OR command LIKE ?", (f'%{question}%', f'%{question}%'))
        res = cursor.fetchone()
        if res:
            result = res['command']
            print("[dim]✔ Encontrado na memória local![/dim]")

    if result:
        print(Panel(f"[bold white]{result}[/bold white]", title="[green]Comando Gerado[/green]"))
        pyperclip.copy(result)
        
        if run:
            print(f"\n[bold yellow]⚠ MODO AUTOMÁTICO[/bold yellow]")
            if Confirm.ask(f"Executar este comando agora?"):
                print(f"[dim]Executando...[/dim]\n")
                try:
                    subprocess.run(result, shell=True, check=True, executable='/bin/bash')
                    print(f"\n[bold green]✔ Feito![/bold green]")
                except Exception as e:
                    print(f"\n[bold red] Falha:[/bold red] {e}")
            else:
                print("[dim]Cancelado. O comando continua copiado.[/dim]")
        else:
            print("[dim]✔ Copiado[/dim]")
    else:
        print(f"[bold red]Nada encontrado para '{question}' (Nem na IA, nem local).[/bold red]")
        print("[dim]Dica: Tente ser mais específico ou configure a IA com 'brain config'.[/dim]")

if __name__ == "__main__":
    app()