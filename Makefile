all: upload

.PHONY: all upload

README.rst: README.md
	@pandoc -t rst -f markdown README.md > README.rst

upload: README.rst
	@python setup.py sdist
	@twine upload dist/*
	@rm -r dist/

