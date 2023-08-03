FROM python:3.5.6-stretch

COPY ./argos-adf/requirements.txt /usr/src/argos-adf/requirements.txt

RUN pip install --no-cache-dir -r /usr/src/argos-adf/requirements.txt

WORKDIR /usr/src/argos-adf/src/starter

CMD python Starter.py -c /usr/src/config.json
