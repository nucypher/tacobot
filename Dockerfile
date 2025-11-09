FROM nucypher/rust-python:3.12.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN sudo apt-get update && sudo apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "bot.py"]
