PDF=output/paper.pdf
DOCX=output/paper.docx

MAIN=main.md
SECTIONS=$(shell find sections -name '*.md' 2>/dev/null)

PANDOC=pandoc
ENGINE=xelatex

all: pdf docx

pdf: $(PDF)

$(PDF): $(MAIN) $(SECTIONS) include-files.lua
	if not exist output mkdir output
	$(PANDOC) $(MAIN) \
		-o $(PDF) \
		--pdf-engine=$(ENGINE) \
		--resource-path=.:./figures:../figures \
		--lua-filter=include-files.lua \
		--citeproc

docx: $(DOCX)

$(DOCX): $(MAIN) $(SECTIONS) include-files.lua
	if not exist output mkdir output
	$(PANDOC) $(MAIN) \
		-o $(DOCX) \
		--resource-path=.:./figures:../figures \
		--lua-filter=include-files.lua \
		--citeproc \
		$(if $(wildcard $(REFERENCE)),--reference-doc=$(REFERENCE),)

clean:
	if exist output rmdir /s /q output