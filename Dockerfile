FROM python:3.9-slim

# Install System Dependencies 
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Set WD
WORKDIR /app

# Down Required Dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . ./

# Expose Flask Port
EXPOSE 5002

# Set ENV Vars
ENV FLASK_APP=backend/app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5002


# Run
CMD ["flask", "run"]