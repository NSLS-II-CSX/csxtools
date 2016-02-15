NBDIR=../../examples
NOTEBOOKS=$(wildcard $(NBDIR)/*.ipynb)
HTMLFILES=$(NOTEBOOKS:.ipynb=.html)
HTML=$(notdir $(HTMLFILES))

.PHONY: all clean

all: $(HTML)

%.html: $(NBDIR)/%.ipynb
	ipython nbconvert $< --to html

clean:
	find . ! -name Makefile ! -name index.rst ! -name .gitignore -delete

print-%:
	@echo '$*=$($*)'
