FROM mysql:8

COPY ./docker/mysql/check.sh /check.sh
RUN chmod 755 /check.sh
COPY ./docker/mysql/config/conf.d/custom.cnf /etc/mysql/conf.d/