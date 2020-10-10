
FROM python:3.6

ENV SOLAX_IP="5.8.8.8"

RUN pip install solax
COPY SolaxGateway.py .

EXPOSE 8000

CMD [ "python", "SolaxGateway.py" ]