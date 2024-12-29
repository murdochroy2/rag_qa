FROM postgres:15

RUN apt-get update && \
    apt-get install -y postgresql-server-dev-15 gcc make git

RUN git clone https://github.com/pgvector/pgvector.git

RUN cd pgvector && make && make install

RUN apt-get remove -y gcc make postgresql-server-dev-15 && \
    apt-get autoremove -y

RUN rm -rf /var/lib/apt/lists/* /pgvector

