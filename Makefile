.PHONY: help
default: help

help:
	@echo "make build"

build:
	@docker build -t self-status-page:latest ./

test:
	@docker run --rm -ti -p 8081:80 self-status-page:latest

%:
	@:
