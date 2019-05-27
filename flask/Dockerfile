FROM python:3.7-alpine
EXPOSE 8080
WORKDIR /app

COPY . .

RUN apk add python3-dev build-base linux-headers pcre-dev
RUN pip3 install -r requirements.txt

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]