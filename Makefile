PY ?= python3

.PHONY: help test labs demo clean lint capstone

help:
	@echo "make test      esegue la suite di test unitari"
	@echo "make labs      esegue ogni laboratorio in ordine"
	@echo "make demo      esegue l'agente su questa repo"
	@echo "make capstone  esegue le eval del progetto finale"
	@echo "make lint      controllo di compilazione di ogni file Python"
	@echo "make clean     rimuove cache e output temporaneo"

test:
	$(PY) -m unittest discover -s tests -t . -v

labs:
	@for f in labs/L*.py; do echo "── $$f"; $(PY) "$$f" || exit 1; done

demo:
	$(PY) -m mini_agent "elenca i file di questa repo" --audit ''

capstone:
	$(PY) -m capstone.repo_doctor --eval

lint:
	$(PY) -m compileall -q mini_agent labs capstone tests

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf .mini_agent sandbox .pytest_cache
