# Build the static site from the files in this repo. The course documents were
# converted once into content/*.html (edit those to fix a page); the original
# material is no longer read. Needs Python 3 only.

FORCE:

html: FORCE
	python3 bin/build.py

# Removes generated pages only; content/ and graphics/ are kept.
clean: FORCE
	rm -rf homework exams index.html
