# 🧠 BRAIN CLI - Personal Assistant

> Seu assistente de terminal híbrido: Inteligência Artificial (Groq) + Memória Local + Automação.

O **Brain CLI** é uma ferramenta de linha de comando escrita em Python que ajuda desenvolvedores a lembrar, gerar e entender comandos de terminal (Linux/Git/Docker) instantaneamente.

## ✨ Funcionalidades

- **🤖 IA Generativa:** Usa a API da Groq (Llama 3) para gerar comandos complexos a partir de perguntas em linguagem natural.
- **💾 Memória Local:** Salva comandos úteis em um banco de dados SQLite local para acesso offline e instantâneo.
- **🚀 Modo Automação:** Gera e executa o comando imediatamente com a flag `-r`.
- **🧐 Professor Linux:** Explica detalhadamente o que qualquer comando faz (`brain explain`).
- **📋 Área de Transferência:** Copia automaticamente o comando gerado para o seu clipboard.

## 🛠 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/brain-cli.git
cd brain-cli
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure sua API Key (Opcional para modo Offline, Obrigatório para IA):
```bash
export GROQ_API_KEY="sua_chave_aqui"
```

## 🚀 Como Usar

### 1. Criar um Alias (Recomendado)

```bash
alias brain='python3 /caminho/para/o/projeto/main.py'
```

### 2. Comandos Disponíveis

| Comando | Descrição | Exemplo |
|-------|-----------|--------|
| brain ask "texto" | Pergunta à IA ou busca localmente | brain ask "como desfazer commit" |
| brain ask ... -r | Pergunta e executa o comando | brain ask "listar pastas" -r |
| brain add | Salva um comando manualmente | brain add "git s" "git status" |
| brain explain | Explica o que um comando faz | brain explain "chmod 777 app" |
| brain list | Lista todos os comandos salvos | brain list |
| brain info | Mostra ajuda e versão | brain info |

## 📦 Backup e Restauração

```bash
brain export backup.json
brain import backup.json
```

## 🛡 Tecnologias

- Typer
- Rich
- Groq SDK
- SQLite

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para testar e modificar.

---

## 📌 Como baixar e usar o Brain CLI

```bash
git clone https://github.com/SEU_USUARIO/brain-cli.git
cd brain-cli
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py info
```

**ATENÇÃO:** Nunca coloque sua `GROQ_API_KEY` diretamente no código. Use sempre variáveis de ambiente.