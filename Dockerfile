FROM python:3.11-slim

WORKDIR /AzanSchedularApp

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY /AzanSchedularApp/. .

# Expose the API port (change if your app uses a different port)
EXPOSE 8000

# Start the API (adjust if you use Flask or another framework)
CMD ["uvicorn", "azan_scheduler:app", "--host", "0.0.0.0", "--port", "8000"]