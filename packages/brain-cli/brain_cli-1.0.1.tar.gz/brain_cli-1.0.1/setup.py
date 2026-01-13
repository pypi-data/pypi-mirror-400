from setuptools import setup

setup(
    name="brain-cli", # Mantenha o nome EXATO que você registrou no PyPI
    version="1.0.1",            # <--- VERSÃO NOVA OBRIGATÓRIA
    py_modules=["brain"],       # O Python vai procurar por "brain.py"
    install_requires=[          # <--- ISSO CORRIGE O ERRO "No module named groq"
        "typer",
        "rich",
        "groq",
        "pyperclip",
        "typing-extensions"
    ],
    entry_points={
        "console_scripts": [
            "brain=brain:app",  # Comando 'brain' chama a função 'app' no arquivo 'brain.py'
        ],
    },
)