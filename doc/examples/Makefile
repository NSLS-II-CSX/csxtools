NBDIR=../../examples
NOTEBOOKS=$(wildcard $(NBDIR)/*.ipynb)
HTMLFILES=$(NOTEBOOKS:.ipynb=.html)
HTML=$(notdir $(HTMLFILES))
IPYNB=$(notdir $(NOTEBOOKS))

.PHONY: all clean

all: $(HTML)

%.html: $(NBDIR)/%.ipynb
	ipython nbconvert $< --to html
	cp $< .

clean:
	find . ! -name Makefile ! -name index.rst ! -name .gitignore -delete

print-%:
	@echo '$*=$($*)'
