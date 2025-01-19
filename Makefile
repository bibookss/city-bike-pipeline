format:
	uv run ruff check --select I --fix
	uv run ruff format

ingest:
	mkdir -p ./logs && touch ./logs/ingestion.log && \
	uv run python3 -m ingestion.pipeline \
		--country=US \
		--city=NewYork-NY \
		--timezone=UTC \
		--staging_path=staging \
		--logconf_path=./config/ingestion.logconf
		