.PHONY: build clean_build

build:
	docker build -t invoicer -f docker/Dockerfile .

clean_build:
	docker build --no-cache -t invoicer -f docker/Dockerfile .