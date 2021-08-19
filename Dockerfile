
ARG ARCH=
FROM ${ARCH}python

ENV SOLAX_IP="5.8.8.8"

RUN pip install aiohttp
RUN pip install voluptuous

COPY solax/solax solax/solax


COPY SolaxGateway.py .

EXPOSE 8000

CMD [ "python", "SolaxGateway.py" ]