FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY src/ ./src/
COPY tests/ ./tests/
COPY docker/examples/ /inputs/

# Optional analysis image; model weights and research data are mounted separately.
FROM base AS analysis
COPY requirements-analysis.txt ./
RUN pip install --no-cache-dir -r requirements-analysis.txt
CMD ["python", "-m", "src.evaluation.check_claim", "--help"]

# Default CLI image uses only the standard library; Ollama runs on the host.
FROM base AS runtime
CMD ["python", "-m", "src.evaluation.check_claim", "--help"]
