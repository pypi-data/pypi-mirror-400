.ONESHELL:

.PHONY: build_bin
build_bin:
	cd src
	nuitka --standalone \
			--plugin-enable=pyside6 \
			--remove-output \
			--onefile \
			--python-flag=-m \
			archliner