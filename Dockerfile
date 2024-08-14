FROM mcr.microsoft.com/playwright:focal

# Install any other dependencies your app needs
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

# Copy your application code
COPY . /app

WORKDIR /app

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
