.PHONY: test build

build-env:
	python3 -m venv .venv
	.venv/bin/pip install poetry
	.venv/bin/poetry install

setup-resources:
	test -d resources/lucide || git clone https://github.com/lucide-icons/lucide.git resources/lucide

generate-icons:
	python3 scripts/generate_icons.py

test:
	.venv/bin/pytest -s test/test_icons.py

run:
	.venv/bin/uvicorn app:app --port 3000 --reload

build:
	.venv/bin/poetry build
