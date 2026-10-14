FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir opencv-python-headless numpy

CMD ["python", "main.py"]