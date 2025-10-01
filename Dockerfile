FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# NUCLEAR CACHE BUST: Force Docker to see requirements fix
RUN echo "Cache bust for tenacity fix: $(date)" > /tmp/cache_bust

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD ["streamlit", "run", "app/Home.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
