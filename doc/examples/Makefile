NBDIR=../../examples
NOTEBOOKS=$(wildcard $(NBDIR)/*.ipynb)
RSTFILES=$(NOTEBOOKS:.ipynb=.rst)
RST=$(notdir $(RSTFILES))

.PHONY: all clean

all: $(RST)

%.rst: $(NBDIR)/%.ipynb
	ipython nbconvert $< --to rst

clean:
	find . ! -name Makefile ! -name index.rst ! -name .gitignore -delete
