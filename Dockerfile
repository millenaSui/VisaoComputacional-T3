FROM python:3.9-slim

WORKDIR /app

# Usamos o opencv-python-headless, que não exige instalação de bibliotecas gráficas no Linux
RUN pip install --no-cache-dir opencv-python-headless numpy

CMD ["python", "main.py"]