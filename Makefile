.PHONY: run

run:
	@ uv run -- sdi-cards.py --verbose
rev:
	@ uv run -- sdi-cards.py --verbose -r
stats:
	@ uv run -- sdi-cards.py --verbose --stats

