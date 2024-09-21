FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir
RUN python manage.py load_ingredients

CMD [ "gunicorn", "--bind", "0.0.0.0:80", "foodgram_backend.wsgi" ]