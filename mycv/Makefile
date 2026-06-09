# Makefile for mycv — data-driven LaTeX CV generator
#
# Targets:
#   generate      - Generate .tex section files from YAML data
#   build         - Generate + compile cv.pdf (default target)
#   test          - Run all tests
#   clean         - Remove LaTeX build artifacts
#   clean-generated - Remove generated .tex files from cv/

.PHONY: all generate build test clean clean-generated

# Default: build the PDF
all: build

# Generate section .tex files from YAML data
generate:
	python -m cvgen.cli --output-dir cv/

# Build PDF: generate then compile
build: generate
	latexmk -xelatex cv.tex

# Run test suite
test:
	pytest tests/ -v

# Remove LaTeX build artifacts (keep .tex and .pdf)
clean:
	latexmk -c
	rm -f cv.bbl cv.bcf cv.blg cv.run.xml

# Remove generated .tex files from cv/ directory
clean-generated:
	rm -f cv/*.tex
