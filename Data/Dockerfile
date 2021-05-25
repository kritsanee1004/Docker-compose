FROM python:3.7
ADD . /tmp
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY consumer.py consumer.py
COPY database.py database.py

CMD ["python", "consumer.py"]
