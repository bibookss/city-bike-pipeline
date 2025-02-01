format:
	uv run ruff check --select I --fix
	uv run ruff format

build_ingest:
	docker build -t city_bike_ingest -f ingestion/Dockerfile .

ingest_docker: build_ingest	
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
