# Use official Python image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install debugpy for remote debugging with VS Code
RUN pip install debugpy

# Copy everything else in current directory to /app
COPY . /app

# Expose Flask port and debugpy port
EXPOSE 5000 5678

# Optional: NLTK data setup (uncomment if needed)
# RUN python -m nltk.downloader punkt stopwords

# Launch Flask with debugpy
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
