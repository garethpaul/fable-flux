.PHONY: check test

check:
	./scripts/check-baseline.sh

test: check
