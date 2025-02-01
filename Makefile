format:
	uv run ruff check --select I --fix
	uv run ruff format

ingest:
	mkdir -p ./logs && touch ./logs/ingestion.log && \
	uv run -m ingestion.pipeline \
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
	if ! docker image inspect city_bike_ingest > /dev/null 2>&1; then \
		docker build -t city_bike_ingest -f ingestion/Dockerfile .; \
	fi && \
	docker run --rm -it \
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
