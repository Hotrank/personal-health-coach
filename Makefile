PHONY: start-fhir, loc

start-fhir:
	docker run --name hapi-fhir-server -p 8080:8080   -v hapi_data:/data   -e spring.datasource.url=jdbc:h2:file:/data/hapi --user root --rm  hapiproject/hapi:latest

loc:
	cloc . --exclude-ext=json --exclude-dir=node_modules,build,dist,.venv,alembic