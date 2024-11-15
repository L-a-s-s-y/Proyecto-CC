## Hito 2
### Gestor de tareas
Como gestor de tareas se ha elegido *GNU Make* pues es potente, polivalente y se tiene experiencia en su uso. La *Makefile* inicial para el proyecto es la siguiente (es bastante básico y seguramente se amplíe y mejore conforme el proyecto avance):
~~~
# define the name of the virtual environment directory
VENV := venv

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: requirements.txt
	python -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

run: venv
	./$(VENV)/bin/python main.py

test: pytest

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

.PHONY: all venv run clean
~~~
### Biblioteca de tests/aserciones
Se ha elegido *Pytest* ya que es el que se recomienda en la documentación proporcionada en el hito y además tiene una documentación bastante detallada. Además, parece más sencillo de usar que *unittest*, que es el módulo por defecto en Python. Un ejemplo de un test sería el siguiente:
~~~
import pytest
from main import funcTestFunc

def test_sample():
    assert funcTestFunc("tests/Three Samples_ASCII.cue") == dict
~~~
### Integración continua
Para la integración continua se ha elegido Github Actions. Es uno de los sistemas más usado, tiene un *free tier* bastante holgado antes de tener que pagar.

La configuración es bastante sencilla. Hay que crear en el proyecto un archivo `.yml`en el siguiente directorio:
> .github/workflows/[nombre_al_gusto].yml

Tras esto hay que configurar el trabajo que se quiere hacer. Para el caso de este proyecto se usa la siguiente configuración (seguramente se amplíe conforme avance el proyecto):
~~~
name: Integración continua v.0.1

on:
    push:
        branches: [master, main]
    pull_request:
        branches: [master, main]

jobs:
    build:
        runs-on: ubuntu-latest

        steps:
            - name: Install ffmpeg
              run: sudo apt install -y ffmpeg

            - name: Checkout code
              uses: actions/checkout@v2
            
            - name: Set up Python
              uses: actions/setup-python@v2
              with:
                python-version: '3.12.7'

            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                pip install -r requirements.txt

            - name: Run tests
              run: |
                pytest test_basics.py
~~~
