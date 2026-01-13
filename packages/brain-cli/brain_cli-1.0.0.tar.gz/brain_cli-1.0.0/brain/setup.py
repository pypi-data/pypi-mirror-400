from setuptools import setup

setup(
    name="brain-cli-assistant",  # Nome do pacote
    version="1.0.0",
    py_modules=["brain"],        # Nome do seu arquivo de código (sem .py)
    install_requires=[
        "typer",
        "rich",
        "groq",
        "pyperclip",
        "typing-extensions"
    ],
    entry_points={
        "console_scripts": [
            "brain=brain:app",   # O comando 'brain' chama a função 'app' dentro de 'brain.py'
        ],
    },
)