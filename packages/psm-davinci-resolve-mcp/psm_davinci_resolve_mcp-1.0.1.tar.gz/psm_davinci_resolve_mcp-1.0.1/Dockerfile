FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY pyproject.toml ./
COPY src/ ./src/

# Install package
RUN pip install --no-cache-dir .

# Run the server
CMD ["python", "-m", "psm_davinci_resolve_mcp"]
