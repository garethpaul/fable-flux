.PHONY: build check lint test

check:
	./scripts/check-baseline.sh

lint: check

test: check

build: check
