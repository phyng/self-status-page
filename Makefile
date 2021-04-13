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
		-e STATUS_GOOGLE_DNS_NAME=Google \
		-e STATUS_GOOGLE_DNS_TYPE=ping \
		-e STATUS_GOOGLE_DNS_IP=8.8.8.8 \
		-e STATUS_SHELL_NAME=Shell \
		-e STATUS_SHELL_TYPE=shell \
		-e STATUS_SHELL_CMD='curl -o /dev/null -s -w "%{time_total}" https://www.baidu.com' \
		phyng/self-status-page:latest

%:
	@:
