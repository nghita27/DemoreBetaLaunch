# Use official Python image (full version for better compatibility)
FROM python:3.11

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (to leverage Docker cache)
COPY requirements.txt .

# Upgrade pip and install lightweight dependencies first
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --default-timeout=100 \
        -r requirements.txt \
        --no-deps

# Install heavy packages (like torch) separately to avoid memory crashes
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# Copy project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "BeautyBlendApp.py", "--server.port=8501", "--server.address=0.0.0.0"]
