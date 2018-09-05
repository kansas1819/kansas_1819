# define Binaries/programs used
PYTHON:=python
CHKQRCODE:= /home/sikshana/sas/flow/bin/checkqrn.py --encrypt
PDFTK:= pdftk
PDFIMAGES=pdfimages 
CONTEXT:= context --once
NUMPAGESOPTS:= dump_data output 
GHOSTSCRIPT=gs
IMGDIR:=pdfImg
TEX:=$(wildcard *.tex)
PDF:=$(patsubst %.tex, %.pdf,${TEX})
LANGTEX:=$(wildcard *-lang.tex)
CORETEX:=$(wildcard *-core.tex)
LANGPDF:=$(patsubst %-lang.tex, %-lang.pdf,${LANGTEX})
PAPER1PDF:=$(patsubst %-lang.tex, %_paper1.pdf,${LANGPDF})
COREPDF:=$(patsubst %-core.tex, %-core.pdf,${CORETEX})
PAPER2PDF:=$(patsubst %-core.tex, %_paper2.pdf,${CORETEX})
SPDF:=$(patsubst %.tex, %_s.pdf,${TEX})
TIF:=$(patsubst %.tex, %.tif, ${TEX})
CHK:=$(patsubst %.tex, %.qrcheck, ${TEX})
PAGES:=$(patsubst %.tex, %.pages, ${TEX})

define exttype =
ext = sed -e 's/.*-//g' $$@
echo $$(PDFIMAGES) -p -j jpg $$(*F) $(ext)
endef


all: $(TIF) $(CHK) 

# pdf generation
%.pdf: %.tex
	$(CONTEXT) --batchmode --silent --noconsole $<

%.tif: %.pdf
	$(eval ext = $(shell echo $@ | sed -e 's/.*-//g' -e 's/.tif//g'))
	mkdir -p $(IMGDIR)$(ext)
	$(PDFIMAGES) -p -tiff $(*F).pdf $(IMGDIR)$(ext)/$(ext)
	touch $@

$(IMGDIR):
	mkdir -p $(IMGDIR)

%.qrcheck: %.tif
	$(eval ext = $(shell echo $< | sed -e 's/.*-//g' -e 's/.tif//g'))
	$(CHKQRCODE) --csv "sch.csv" --dir $(IMGDIR)$(ext) --pattern $(ext)*
	#-rm -rf $(IMGDIR)$(ext)
	touch $@

%.pages: %.pdf
	$(PDFTK) $< $(NUMPAGESOPTS) | grep "NumberOf" > $@

cleanpdf:
	rm -f *.toc *.tuc *.aux *.log *.out *.pdf

cleanchk:
	-rm *.qrcheck
	-rm *.tif

clean:
	rm -f *.toc *.aux *.log *.out 
pclean:
	-rm *_paper*.pdf
cleanall:
	rm -f *.toc *.pdf *.aux *.log *.out

.PHONY: all clean cleanall cleanpdf cleanchk

.PRECIOUS: %.pdf

.DELETE_ON_ERROR:
.ONESHELL:
