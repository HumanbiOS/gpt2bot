FROM python:3.7-slim-stretch

WORKDIR /app/usr/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . .
CMD python server.py
