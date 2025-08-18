.PHONY: run

run:
	@ uv run -- sdi-cards.py --verbose
rev:
	@ uv run -- sdi-cards.py --verbose -r
