FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl unzip chromium-driver chromium \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="$PATH:/usr/bin"

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Streamlit runs on port 7860 by default
EXPOSE 7860

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
