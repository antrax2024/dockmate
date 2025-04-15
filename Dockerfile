FROM python:3.14.0a7-alpine3.21
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


ENV TZ=America/Sao_Paulo

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app
COPY .env /app/.env

# Create virtual environment
RUN uv venv --python 3.13
# Install dependencies
RUN uv sync


# Command to run the application
ENTRYPOINT [ "uv run docker-whatch" ] uv run docker-watch

