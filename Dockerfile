FROM python:3-slim AS build-env

WORKDIR /app

ADD requirements.txt .

RUN pip3 install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt


FROM python:3-slim

WORKDIR /app

ADD secrets_file.json .
ADD corona_numbers_bot.py bot.py

COPY --from=build-env /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

CMD [ "python", "bot.py" ]