SHELL := /bin/bash
dirname := $(notdir $(patsubst %/,%,$(CURDIR)))

list:
	@grep '^[^#[:space:]].*:' Makefile

build:
	rm -rf ../../build/$(dirname) || true
	mkdir -p ../../build/$(dirname)
	cp -r ./apiproxy ../../build/$(dirname)

deploy: build
	cd ../../build/$(dirname) && apigeetool deployproxy -V -o nhsd-nonprod -e internal-dev -n async-slowapp-local -t $$(get_token)

undeploy:
	apigeetool undeploy -V -o nhsd-nonprod -e internal-dev -n async-slowapp-local -t $$(get_token)

delete:
	apigeetool delete -V -o nhsd-nonprod -n async-slowapp-local -t $$(get_token)

clean:
	rm -rf ./node_modules
