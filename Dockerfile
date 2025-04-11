FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV TZ=America/Sao_Paulo

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app
COPY .env /app/.env

# Create virtual environment
RUN uv venv
# Install dependencies
RUN uv sync


# Command to run the application
CMD uv run main.py

