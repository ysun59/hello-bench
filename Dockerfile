FROM thrift

WORKDIR /
COPY main.sh  /
ENTRYPOINT ["/main.sh"]
