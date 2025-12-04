.PHONY: venv
venv:
	uv venv .venv --python 3.12
	uv pip install -r requirements.txt	

.PHONY: run
run:
	uv run game/main.py
