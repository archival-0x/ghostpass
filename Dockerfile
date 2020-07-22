FROM golang:alpine

RUN mkdir /app
ADD . /app/
WORKDIR /app

RUN make
RUN adduser -S -D -H -h /app ghostpass
USER ghostpass

CMD ["./ghostpass"]
