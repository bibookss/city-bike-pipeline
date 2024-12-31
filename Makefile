format:
	uv run ruff check --select I --fix
	uv run ruff format

ingest:
	uv run python3 -m ingestion.pipeline \
		--country=US \
		--timezone=UTC \
		--staging_path=staging \
		--logconf_path=./config/ingestion.logconf
		