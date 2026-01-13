.PHONY: help clean build check release test-install test-release release-test release-prod bump-version

help:
	@echo "OrcaLink Release Commands"
	@echo "=========================="
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean              - Clean build artifacts"
	@echo ""
	@echo "Building:"
	@echo "  make build              - Build distribution packages"
	@echo "  make check              - Check package quality"
	@echo ""
	@echo "Version:"
	@echo "  make bump-version       - Bump version (prompts for version)"
	@echo ""
	@echo "Testing:"
	@echo "  make test-install-local - Test install from local wheel"
	@echo "  make test-install-test  - Test install from TestPyPI"
	@echo "  make test-install-prod  - Test install from PyPI"
	@echo ""
	@echo "Release:"
	@echo "  make release-test       - Release to TestPyPI"
	@echo "  make release-prod       - Release to PyPI (production)"
	@echo ""

clean:
	./scripts/release/clean.sh

build: clean
	./scripts/release/build.sh

check: build
	./scripts/release/check.sh

bump-version:
	@read -p "Enter new version (e.g., 0.1.0): " version; \
	./scripts/release/bump_version.sh $$version

test-install-local: build
	./scripts/release/test_install.sh local

test-install-test:
	./scripts/release/test_install.sh test

test-install-prod:
	./scripts/release/test_install.sh prod

release-test: check
	./scripts/release/upload_test.sh

release-prod: check
	./scripts/release/upload_prod.sh

# Full release workflow to TestPyPI
test-release: clean build check release-test
	@echo "✅ TestPyPI release completed!"

# Full release workflow to PyPI
release: clean build check release-prod
	@echo "✅ PyPI release completed!"

