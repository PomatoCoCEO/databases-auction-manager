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

COPY createTable.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
