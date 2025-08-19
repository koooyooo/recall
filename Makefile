.PHONY: run

run:
	@ uv run -- recall.py quiz --verbose
rev:
	@ uv run -- recall.py quiz --verbose -r
stats:
	@ uv run -- recall.py stats 
info:
	@ uv run -- recall.py info
