FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir mcp-server-grist==0.2.1

EXPOSE 8000
CMD ["mcp-server-grist", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
