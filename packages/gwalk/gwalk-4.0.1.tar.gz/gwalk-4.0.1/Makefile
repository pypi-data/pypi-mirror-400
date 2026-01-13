.PHONY: all

######## Variables ########
VERSION = 4.0.1
DIST=dist/gwalk-${VERSION}.tar.gz
version: clean
	sed --in-place "s/version = .*/version = \"${VERSION}\"/g" pyproject.toml
	sed --in-place "s/ version: .*/ version: '${VERSION}',/g" meson.build
	echo "__version__ = ${VERSION}" > __version__.py
	echo "__version__ = ${VERSION}" > src/gwalk/__version__.py
HERE=$(shell pwd)
DATA=${HERE}/data

# Location of catalog
FNAME_CATALOG = data/catalog_samples.hdf5
# Location of GWXXXXXX.h5 files from LIGO release
# May require some renaming of files (or linking)
GWTC_1_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_1_sample_release
GWTC_2_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_2
GWTC_2p1_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_2p1
GWTC_3_RELEASE = 	${HOME}/Projects/gwalk/data/GWTC_3
######## Installation ########

$(DIST): clean version
	- git add src meson.build __version__.py
	- git commit
	python3 -m build

install: $(DIST)
	python3 -m pip install $(DIST)

testpypi: install unit_tests
	python3 -m twine upload --repository testpypi $(DIST)

pypi: testpypi
	python3 -m twine upload $(DIST)

######## Unit tests ########

unit_tests: \
	test_maha \
	test_decomposition \
	test_pdf \
	test_object \
	test_kl \
	test_grid \
	test_mixture \
	test_fixed \
	test_kde

production_tests: unit_tests \
	test_data \
	test_catalog \
	GW150914-aligned3d_source-IMRPhenomPv2

test_data: install
	python3 tests/test_data.py

test_catalog: install
	python3 tests/test_catalog.py

test_maha: install
	python3 tests/test_maha.py

test_decomposition: install
	python3 tests/test_decomposition.py

test_pdf: test_maha test_decomposition
	python3 tests/test_pdf.py

test_object: install
	python3 tests/test_object.py

test_kl: test_object test_pdf
	python3 tests/test_kl.py

test_grid: install test_kl
	python3 tests/test_grid.py

test_mixture: install
	python3 src/gwalk/mixture/mixture.py

test_fixed: install test_object
	python3 src/gwalk/mixture/fixed.py

test_kde: install test_object
	python3 src/gwalk/mixture/kde.py

test_dpgmm: install test_kl
	python3 tests/test_dpgmm.py

GW150914-aligned3d_source-IMRPhenomPv2: install
	python3 tools/fit_catalog_samples.py \
		--catalog GWTC-1 \
		--event GW150914 \
		--approximant IMRPhenomPv2 \
		--coordinates aligned3d_source \
		--fname-nal GW150914.nal.hdf5 \
		--min-bins 10 \
		--max-bins2d 30 \
		--verbosity 3
	python3 tools/plot_nal_fit.py \
		--catalog GWTC-1 \
		--event GW150914 \
		--approximant IMRPhenomPv2 \
		--coordinates aligned3d_source \
		--fname-nal GW150914.nal.hdf5 \
		--fname-out GW150914_IMRPhenomPv2_aligned3d_source_genetic.png \
		--nal-method genetic \
		--resample 1_000_000 \
		--verbosity 3


GW150914-aligned3d_source-NRSur7dq4: install
	python3 tools/fit_catalog_samples.py \
		--catalog NRSurCat-1 \
		--event GW150914_095045 \
		--approximant NRSur7dq4 \
		--coordinates aligned3d_source \
		--fname-nal GW150914.nal.hdf5 \
		--min-bins 10 \
		--max-bins2d 30 \
		--verbosity 3
	python3 tools/plot_nal_fit.py \
		--catalog NRSurCat-1 \
		--event GW150914_095045 \
		--approximant NRSur7dq4 \
		--coordinates aligned3d_source \
		--fname-nal GW150914.nal.hdf5 \
		--fname-out GW150914_NRSur7dq4_aligned3d_source_simple.png \
		--nal-method simple \
		--resample 1_000_000 \
		--verbosity 3
	python3 tools/plot_nal_fit.py \
		--catalog NRSurCat-1 \
		--event GW150914_095045 \
		--approximant NRSur7dq4 \
		--coordinates aligned3d_source \
		--fname-nal GW150914.nal.hdf5 \
		--fname-out GW150914_NRSur7dq4_aligned3d_source_grid.png \
		--nal-method grid \
		--resample 1_000_000 \
		--verbosity 3
	python3 tools/plot_nal_fit.py \
		--catalog NRSurCat-1 \
		--event GW150914_095045 \
		--approximant NRSur7dq4 \
		--coordinates aligned3d_source \
		--fname-nal GW150914.nal.hdf5 \
		--fname-out GW150914_NRSur7dq4_aligned3d_source_genetic.png \
		--nal-method genetic \
		--resample 1_000_000 \
		--verbosity 3

GW150914: install
	python3 tools/fit_event_loop.py \
		--catalog GWTC-1 \
		--event GW150914 \
		--wkdir ${DATA}/GWTC-1/GW150914 

GW170817: install
	python3 tools/fit_event_loop.py \
		--catalog GWTC-1 \
		--event GW170817 \
		--wkdir ${DATA}/GWTC-1/GW170817 

GW190425_problems: install
	#python3 tools/fit_catalog_samples.py --approximant SEOBNRv4T_surrogate_highspin_RIFT --coordinates aligned3d_dist --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	#python3 tools/fit_catalog_samples.py --approximant IMRPhenomPv2_NRTidal-HS --coordinates mass_tides --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	#python3 tools/fit_catalog_samples.py --approximant TaylorF2-LS --coordinates mass_tides --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	#python3 tools/fit_catalog_samples.py --approximant IMRPhenomD_NRTidal-LS --coordinates mass_tides_source --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	#python3 tools/fit_catalog_samples.py --approximant SEOBNRv4T_surrogate_highspin_RIFT --coordinates aligned_tides --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	#python3 tools/fit_catalog_samples.py --approximant TEOBResumS-HS --coordinates aligned_tides --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	#python3 tools/fit_catalog_samples.py --approximant IMRPhenomD_NRTidal-HS --coordinates aligned_tides_dist --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	python3 tools/fit_catalog_samples.py --approximant IMRPhenomD_NRTidal-HS --coordinates spin6d --catalog GWTC-2 --event GW190425 --fname-nal GW190425.nal.hdf5 --min-bins 10 --max-bins2d 20 --nstep 100 --nwalk 100 --verbosity 2
	

GW190425: install
	python3 tools/fit_event_loop.py \
		--catalog GWTC-2 \
		--wkdir ${DATA}/GWTC-2/GW190425 \
		--event GW190425 \
		--min-bins 10 \
		--max-bins2d 20 \
		--nstep 300 \
		--nwalk 1000

GW231123: install
	python3 tools/fit_event_loop.py \
		--catalog GWTC-4 \
		--event GW231123_135430 \
		--fname-nal GW231123_135430.nal.hdf5 \
		--min-bins 10 \
		--max-bins2d 30 \
		--nstep 300 \
		--nwalk 1000 \
		--nloop 2 \
		--verbosity 2

######## Catalog ########

build-catalog: 
	mkdir -p data
	python3 tools/build_catalog.py $(FNAME_CATALOG) clean
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-1 		$(GWTC_1_RELEASE)
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-2 		$(GWTC_2_RELEASE)
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-2p1 	$(GWTC_2p1_RELEASE)
	python3 tools/build_catalog.py $(FNAME_CATALOG) GWTC-3 		$(GWTC_3_RELEASE)

GWTC-1: install
	python3 tools/NAL_event_pipeline.py \
		--catalog GWTC-1 \
		--wkdir ${DATA}/GWTC-1 \
		--threads 1 \
		--max-bins2d 31 \
		--nstep 300 \
		--nwalk 1000 \
		--make-plots

GWTC-2: install
	python3 tools/NAL_event_pipeline.py \
		--catalog GWTC-2 \
		--wkdir ${DATA}/GWTC-2 \
		--threads 1 \
		--verbosity 3 \
		--max-bins2d 31 \
		--nstep 300 \
		--nwalk 1000 \
		--make-plots

GWTC-2p1: install
	python3 tools/NAL_event_pipeline.py \
		--catalog GWTC-2p1 \
		--wkdir ${DATA}/GWTC-2p1 \
		--threads 1 \
		--max-bins2d 31 \
		--nstep 300 \
		--nwalk 1000 \
		--make-plots

GWTC-3: install
	python3 tools/NAL_event_pipeline.py \
		--catalog GWTC-3 \
		--wkdir ${DATA}/GWTC-3 \
		--threads 1 \
		--max-bins2d 31 \
		--nstep 300 \
		--nwalk 1000 \
		--make-plots

GWTC-4: install
	python3 tools/NAL_event_pipeline.py \
		--catalog GWTC-4 \
		--wkdir ${DATA}/GWTC-4 \
		--threads 1 \
		--max-bins2d 31 \
		--nstep 300 \
		--nwalk 1000 \
		--make-plots

NRSurCat-1: install
	python3 tools/NAL_event_pipeline.py \
		--catalog NRSurCat-1 \
		--wkdir ${DATA}/NRSurCat-1 \
		--threads 1 \
		--max-bins2d 31 \
		--nstep 300 \
		--nwalk 1000 \
		--make-plots

######## Clean ########

clean:
	rm -rf .eggs
	rm -rf src/gwalk.egg-info
	rm -rf .tox
	rm -rf dist
	rm -rf build
	rm -f test_matern_plot.png
	rm -f src/gp_api/kernels/compact_kernel_cython.c
	rm -f src/gwalk/compat*so
	rm -f src/*so
	rm -f test_mesh.hdf5
	rm -rf test_*.png
	rm -rf test_*.hdf5

clear: clean
	rm -rf GW*.png
	rm -rf GW*.hdf5
	rm -rf data/*
