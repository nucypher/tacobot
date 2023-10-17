FROM python:3.9.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "bot.py"]
