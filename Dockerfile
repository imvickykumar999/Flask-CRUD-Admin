# Use official Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy your project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Run your app
CMD ["python", "app.py"]
