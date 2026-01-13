from setuptools import setup

setup(
    name="brain-cli", 
    version="1.0.5",           
    py_modules=["brain"],       
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "groq>=0.4.0",
        "pyperclip>=1.8.0",
        "typing-extensions>=4.0.0"
    ],
    entry_points={
        "console_scripts": [
            "brain=brain:app",
        ],
    },
)