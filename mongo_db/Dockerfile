FROM mongo
ARG CACHEBUST=1
COPY dump /dump
COPY restore.sh /docker-entrypoint-initdb.d/
