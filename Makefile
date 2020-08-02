all:
	go build && go build cmd/ghostpass/main.go
	mv ./main ./ghostpass

clean:
	rm ./ghostpass
