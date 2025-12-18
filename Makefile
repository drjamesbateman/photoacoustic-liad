# Default target: build all figures
all: comparison.pdf diffraction.pdf spacetime.pdf

# Extract list of scenarios from compare.txt
CASES := $(shell grep -v '^\#' compare.txt | grep -v '^$$' | awk '{print $$1}')
CSV_FILES := $(patsubst %,photoacoustic-%.csv,$(CASES))
PNG_FILES := $(patsubst %,photoacoustic-%.png,$(CASES))
PDF_FILES := $(patsubst %,photoacoustic-%.pdf,$(CASES))

optical_properties.yaml: optical_properties.py
	python3 optical_properties.py
	python3 update_experiments.py  # Sync optical properties to experiments.yaml

photoacoustic-%.csv photoacoustic-%.png: experiments.yaml materials.yaml photoacoustic.py optical_properties.yaml
	python3 photoacoustic.py $*

comparison.pdf: compare.py compare.txt $(CSV_FILES)
	python3 compare.py

diffraction.pdf: diffraction.py
	python3 diffraction.py 2.5 --velocity --per-panel --samples 100000

spacetime.pdf: spacetime.py
	python3 spacetime.py

# Verify Monte Carlo vs cylindrical integration vs thin-skin (specify CASE=...)
verify:
	@if [ -z "$(CASE)" ]; then \
		echo "Usage: make verify CASE=Northup"; \
		exit 1; \
	fi
	python3 verify.py $(CASE)

clean:
	-rm optical_properties.yaml
	-rm comparison.png comparison.pdf
	-rm diffraction.png diffraction.pdf
	-rm spacetime.png spacetime.pdf
	-rm $(CSV_FILES)
	-rm $(PNG_FILES)
	-rm $(PDF_FILES)
	-rm photoacoustic-*-verify.png photoacoustic-*-verify.pdf

.PHONY: all verify clean
