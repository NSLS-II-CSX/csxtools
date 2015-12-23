NOTEBOOKS = $(wildcard ../../notebooks/*.ipynb)

all: $(NOTEBOOKS)
	ipython nbconvert $^ --to rst
