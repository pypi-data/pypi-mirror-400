run:
	textual run --dev tooi.cli:main

dist: clean
	uv build

publish :
	uv publish

clean:
	rm -rf build dist

changelog:
	./generate_changelog > CHANGELOG.md
