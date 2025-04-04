FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables directly in Dockerfile
ENV FLASK_ENV=production
ENV MONGO_URI=mongodb+srv://cxraide-admin:OhbYaa4VRXmEolR9@cxraide.av2tc7q.mongodb.net/?retryWrites=true&w=majority&appName=CXRaide
ENV DB_NAME=cxraide
ENV SECRET_KEY=ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce

# Expose the port the app runs on
EXPOSE 5000

# Use python to run the app directly for development or troubleshooting
# CMD ["python", "app.py"]

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"] 