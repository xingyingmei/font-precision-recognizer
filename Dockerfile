FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs static/images

# Create data directories
RUN python3 << 'EOF'
import os
import json

data_dir = './data'
os.makedirs(data_dir, exist_ok=True)

db_path = os.path.join(data_dir, 'font_database.json')
if not os.path.exists(db_path):
    initial_db = {
        'version': '1.0.0',
        'last_updated': '2026-09-16',
        'fonts': []
    }
    with open(db_path, 'w') as f:
        json.dump(initial_db, f, indent=2)

EOF

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

# Run the application
CMD ["python", "app.py"]
