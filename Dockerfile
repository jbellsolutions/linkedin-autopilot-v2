FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Pillow image generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libfreetype6-dev libjpeg62-turbo-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create runtime data directories
RUN mkdir -p data/{analytics,briefs,drafts,engagement,influencers,leads,posting-queue,published,swipe-file,trend-intel,visuals}

EXPOSE 8080

CMD ["python", "main.py"]
