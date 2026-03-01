.PHONY: make_deb

make_deb:
	@echo "Invoking debian package builder..."
	bash packaging/make_deb.sh
