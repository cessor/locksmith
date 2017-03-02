.PHONY: tornado nginx serve stop clean pw

# To inspect, use
# docker exec -i -t locksmith /bin/bash

tornado:
	docker build -t cessor/locksmith -f Dockerfile .

nginx:
	docker build -t cessor/locksmith-nginx -f nginx.Dockerfile .

serve:
	docker run --name locksmith -d cessor/locksmith
	docker run --name locksmith-nginx -v $(shell pwd)/../cert:/var/cert/ -v $(shell pwd)/logs:/var/log/nginx_locksmith/ --link locksmith:locksmith -d -p 8443:8443 cessor/locksmith-nginx

stop:
	docker stop locksmith
	docker stop locksmith-nginx

clean:
	docker rm locksmith
	docker rm locksmith-nginx

pw:
	docker exec -i -t locksmith /bin/bash -l -c "cat /.secret"