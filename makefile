install:
	python3 -m venv --clear .venv
	.venv/bin/pip install -r requirements.txt

run-local:
	.venv/bin/uvicorn app.main:app --reload
