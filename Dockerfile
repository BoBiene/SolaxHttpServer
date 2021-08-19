
ARG ARCH=
FROM ${ARCH}python

ENV SOLAX_IP="5.8.8.8"

# RUN pip install solax
COPY solax/solax solax/solax
RUN python solax/setup.py install

COPY SolaxGateway.py .

EXPOSE 8000

CMD [ "python", "SolaxGateway.py" ]