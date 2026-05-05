PDF=output/paper.pdf
MAIN=main.md
SECTIONS=$(shell find sections -name '*.md' 2>/dev/null)

ENGINE=xelatex
PANDOC=pandoc

all: $(PDF)

$(PDF): $(MAIN) $(SECTIONS) include-files.lua
	if not exist output mkdir output
	$(PANDOC) $(MAIN) \
		-o $(PDF) \
		--pdf-engine=$(ENGINE) \
		--resource-path=.:./figures:../figures \
		--lua-filter=include-files.lua \
		--citeproc

clean:
	if exist output rmdir /s /q output