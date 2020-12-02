FROM python

WORKDIR /app

ADD requirements.txt .

RUN python -m pip install -r requirements.txt
RUN touch secrets_file.json

ADD corona_numbers_bot.py bot.py

CMD [ "python", "bot.py" ]