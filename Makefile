.PHONY: build clean_build run build_wkhtml

build:
	docker build -t invoicer -f docker/Dockerfile .

clean_build:
	docker build --no-cache -t invoicer -f docker/Dockerfile .
	docker build --no-cache -t invoicer-wkhtmltopdf -f docker/wkhtmltopdf/Dockerfile docker/wkhtmltopdf

run:
	docker-compose -f docker/docker-compose.yml up

build_wkhtml:
	 docker build -t invoicer-wkhtmltopdf -f docker/wkhtmltopdf/Dockerfile docker/wkhtmltopdf
