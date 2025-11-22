dev:
	@echo "Starting MCP gateway..."
	uv run src/exaspoon_mcp_gateway.py & \
	sleep 3 && \
	echo "Starting FastAPI app..." && \
	uv run src/app.py & \
	sleep 5 && \
	open http://0.0.0.0:5556

stop:
	./stop.sh

console:
	uv run src/exaspoon_agent.py

# Test the ExaSpoon agent functionality
test-agent:
	@echo "🧪 Running ExaSpoon Agent Tests..."
	uv run test_agent.py

# Quick syntax and import check
test-syntax:
	@echo "🔍 Testing syntax and imports..."
	python -m py_compile src/exaspoon_agent.py src/app.py src/exaspoon_mcp_gateway.py src/chart_service.py
	python -c "import sys; sys.path.insert(0, 'src'); import exaspoon_agent, chart_service; print('✅ All imports successful')"

# Run all tests
test: test-syntax test-agent
	@echo "✅ All tests completed!"

# Docker commands
docker-dev:
	@echo "🐳 Starting services with Docker Compose..."
	docker-compose up --build -d
	@echo "⏳ Waiting for services to start..."
	sleep 10
	@echo "🌐 Opening browser..."
	open http://localhost:5556

docker-stop:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	@echo "🔄 Restarting Docker services..."
	docker-compose restart

docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --rmi all

docker-status:
	@echo "📊 Docker services status:"
	docker-compose ps

# Docker development with logs
docker-dev-logs:
	@echo "🐳 Starting services with Docker Compose and showing logs..."
	docker-compose up --build

# Enter container shell
docker-shell:
	@echo "🐚 Entering FastAPI container shell..."
	docker-compose exec fastapi-app /bin/bash

docker-shell-gateway:
	@echo "🐚 Entering MCP Gateway container shell..."
	docker-compose exec mcp-gateway /bin/bash
