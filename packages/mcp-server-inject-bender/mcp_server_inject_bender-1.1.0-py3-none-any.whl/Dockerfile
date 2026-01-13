# Inject Bender MCP Server - Docker Image
# Security through absurdity - transforms attacks into comedy
#
# Build: docker build -t mcp-server-inject-bender .
# Run:   docker run -i mcp-server-inject-bender
#
# Part of HumoticaOS/SymbAIon - https://humotica.com

FROM python:3.11-slim

LABEL maintainer="Jasper van de Meent <info@humotica.com>"
LABEL org.opencontainers.image.source="https://github.com/jaspertvdm/mcp-server-inject-bender"
LABEL org.opencontainers.image.description="Inject Bender - Security through absurdity, AI-powered humor defense"
LABEL org.opencontainers.image.licenses="MIT"

# Install from PyPI
RUN pip install --no-cache-dir mcp-server-inject-bender

# MCP servers communicate via stdio
ENTRYPOINT ["mcp-server-inject-bender"]
