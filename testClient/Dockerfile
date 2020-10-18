FROM python:3.8.1-slim-buster as app
LABEL maintainer="ERICK GUBI <erick.gubi@gmail.com>"

COPY queryURL.py queryURL.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD ["python3", "-u", "queryURL.py"]