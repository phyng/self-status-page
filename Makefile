.PHONY: help
default: help

help:
	@echo "make build"

build:
	@docker build -t phyng/self-status-page:latest ./

test:
	docker run --rm -ti -p 8081:80 \
		-e STATUS_EXAMPLE_NAME=Example \
		-e STATUS_EXAMPLE_TYPE=http \
		-e STATUS_EXAMPLE_URL=http://www.example.com/ \
		phyng/self-status-page:latest

%:
	@:
