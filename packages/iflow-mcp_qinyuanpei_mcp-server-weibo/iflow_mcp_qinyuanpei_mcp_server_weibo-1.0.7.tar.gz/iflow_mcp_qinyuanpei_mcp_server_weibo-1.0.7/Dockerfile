FROM python:3.10-slim

WORKDIR /app

# Install uv first
RUN pip install --upgrade pip && pip install uv

# Copy project files
COPY . .

# Install dependencies using uv (use --system for global install)
RUN uv pip install --upgrade pip --system
RUN uv pip install --system .

# Expose the port used by the MCP server (default 4200, can be overridden by PORT env)
EXPOSE 4200
ENV PORT=4200

# Run the server using the streamable-http mode and allow PORT env override
CMD ["uvx", "--from", ".", "mcp-server-weibo", "--http"]