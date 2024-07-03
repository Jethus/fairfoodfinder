FROM python:3.11-slim-bullseye

WORKDIR /fairfoodfinder

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_spider.py"]