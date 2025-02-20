build:
	docker build -t hr-agent-v1 .

run: 
	docker run -it --rm \
	-v ".:/app" \
	-v "./company_data:/app/company_data" \
	-e PYTHONPATH=/app \
	-e OLLAMA_HOST=http://host.docker.internal:11434 \
	--add-host=host.docker.internal:host-gateway \
	hr-agent-v1

debug:
	docker run -it --rm \
	-v ".:/app" \
	-v "./company_data:/app/company_data" \
	-e PYTHONPATH=/app \
	-e OLLAMA_HOST=http://host.docker.internal:11434 \
	--add-host=host.docker.internal:host-gateway \
	hr-agent-v1 bash
