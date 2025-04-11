FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app
COPY .env /app/.env


# update the system
RUN apt-get update && apt-get install -y curl

# Create virtual environment
RUN uv venv
# Install dependencies
RUN uv sync

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD uv run uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4

