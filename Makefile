format:
	uv run ruff check --select I --fix
	uv run ruff format

ingest:
	mkdir -p ./logs && touch ./logs/ingestion.log && \
	uv run python3 -m ingestion.pipeline \
		--country=US \
		--city="New York, NY" \
		--staging_path=staging \
		--logconf_path=./config/ingestion.logconf \
		--db_name=city_bikes_staging \
		--db_user=test \
		--db_password=test \
		--db_host=localhost \
		--db_port=5432 \