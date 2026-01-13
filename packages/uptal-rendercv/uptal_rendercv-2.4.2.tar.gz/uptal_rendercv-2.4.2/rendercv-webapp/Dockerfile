# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Fix requirements to use pip package instead of local
RUN sed -i 's/-e \.\.$/rendercv[full]/' requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for PDF storage
RUN mkdir -p static/pdf

# Expose port
EXPOSE 5000

# Run the application for development
CMD ["python", "app.py"]