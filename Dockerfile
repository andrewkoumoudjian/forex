FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make port 8080 available (Cloud Run default)
EXPOSE 8080

# Define environment variable
ENV PORT=8080

# Run the web service
CMD ["python", "app.py"]