FROM python:3-slim

WORKDIR /app

ADD requirements.txt .
ADD secrets_file.json .

RUN python -m pip install -r requirements.txt

ADD corona_numbers_bot.py bot.py

CMD [ "python", "bot.py" ]