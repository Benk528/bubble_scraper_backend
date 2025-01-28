# Use a base image that supports Playwright & Python
FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy AS builder

# Set up environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Set up virtual environment
RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Use a slim image for deployment
FROM python:3.9.6-slim

WORKDIR /app

# Copy over the virtual environment and project files
COPY --from=builder /app/.venv .venv/
COPY . .

# Expose the application port
EXPOSE 8000

# Run FastAPI with Uvicorn (adjusted for `api/` folder)
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
