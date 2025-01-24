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
		--db_name=city_bike \
		--db_user=root \
		--db_password=root \
		--db_host=localhost \
		--db_port=5433 \

ingest_docker:
	docker run -it \
		--network=city_bike_network \
		city_bike_ingest \
		--country=US \
		--city="New York, NY" \
		--staging_path=staging \
		--logconf_path=./config/ingestion.logconf \
		--db_name=city_bike \
		--db_user=root \
		--db_password=root \
		--db_host=pgdatabase \
		--db_port=5432 \
