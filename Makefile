.PHONY: locksmith run clean inspect pw nginx server
locksmith:
	docker build -t cessor/locksmith -f Dockerfile .

# Run source auth.sh
run:
	@docker run --name locksmith \
	-e PROXY_USER=$(PROXY_USER) \
	-e PROXY_PASSWORD=$(PROXY_PASSWORD) \
	-e PROXY_URL=$(PROXY_URL) \
	-d \
	cessor/locksmith

clean:
	docker stop locksmith
	docker rm locksmith

inspect:
	docker exec -i -t locksmith /bin/bash

pw:
	docker exec -i -t locksmith /bin/bash -l -c "cat /.secret"

nginx:
	docker build -t cessor/locksmith-nginx -f nginx.Dockerfile .

server:
	docker run --name locksmith-nginx \
	-v $(shell pwd)/../cert:/var/cert/ \
	-v $(shell pwd)/logs:/var/log/nginx_locksmith/ \
	--link locksmith:locksmith \
	-d \
	-p 8443:8443 \
	cessor/locksmith-nginx
