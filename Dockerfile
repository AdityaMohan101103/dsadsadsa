FROM python:3.10-slim

# Install Chromium and matching ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium chromium-driver curl unzip \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/lib/chromium/chromedriver
ENV PATH="${CHROMEDRIVER_PATH}:${PATH}"

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install streamlit selenium

# Streamlit port
EXPOSE 7860

# Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
