# 
# Bases de Dados 2020/2021
# Trabalho Prático
#
# Authors: 
#   Nuno Antunes <nmsa@dei.uc.pt>
#   BD 2021 Team - https://dei.uc.pt/lei/
#   University of Coimbra

FROM library/postgres

ENV POSTGRES_USER admin
ENV POSTGRES_PASSWORD admin
ENV POSTGRES_DB leiloes

COPY aaacreateTable.sql /docker-entrypoint-initdb.d/
COPY procedures/* /docker-entrypoint-initdb.d/
COPY test_data/* /docker-entrypoint-initdb.d/

EXPOSE 5432
