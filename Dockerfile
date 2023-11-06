FROM python:3

WORKDIR /opt/app/
EXPOSE 8080

RUN apt update
RUN apt install -y postgresql-client

COPY setup_database.sh /bin/
RUN chmod +x /bin/setup_database.sh

COPY requirements.txt /opt/app/
RUN pip install -r ./requirements.txt

COPY . /opt/app/
RUN pip install .

CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "8080", "server.wsgi:app" ]
