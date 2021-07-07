#version =$$(python -c 'import setuptools as sut; print(sut.config.read_configuration("setup.cfg")["metadata"]["version"])')
#pkgname =$$(python -c 'import setuptools as sut; print(sut.config.read_configuration("setup.cfg")["metadata"]["name"])')
version = 0.1
pkgname = createcloth

default: build install
	echo "hello"

install: #dist/$(pkgname)-$(version).tar.gz
	pip uninstall $(pkgname) -y
	pip install dist/$(pkgname)-$(version)-py3-none-any.whl --force-reinstall
	#pip install dist/$(pkgname)-$(version).tar.gz --force-reinstall

.PHONY: build
build: 
	-rm dist/*
	-python -m pep517.build .

create_verbesserung_for_rechtsstrickzuangepasst:
	python -m createcloth.rechtsstrickzuangepasst.src.compile_verbesserer

test_clothfactory:
	python -m unittest clothfactory_parts.test_clothfactory_parts

test_strickgraph:
	python -m unittest createcloth.strickgraph.test_strickgraph

test_meshhandler:
	python -m unittest createcloth.meshhandler.test_meshhandler
	#python -m unittest createcloth.meshhandler.test_meshhandler -k test_wholerelaxing
	#python -m unittest createcloth.meshhandler.test_meshhandler -k test_createsurfacemap


test_manualtoverbesserung:
#	python -m unittest createcloth.verbesserer.test_verbesserer.test_manualtoverbesserung.test_xmlverbesserung
#	python -m unittest createcloth.verbesserer.test_verbesserer.test_manualtoverbesserung.test_tryingsimpleinsert
#	python -m unittest createcloth.verbesserer.test_verbesserer.test_manualtoverbesserung.test_multiersetzer
	python -m unittest createcloth.verbesserer.test_verbesserer

test_builtinverbesserer:
	python -m unittest createcloth.builtin_verbesserer.test_builtinverbesserer

show_relaxing:
	python createcloth/show_relaxing.py

test_toedgetension:
	python -m unittest createcloth.nodespannungtoedgespannung.test_toedgetension


test_myprogram:
	#python -m myprogram.asd createcloth/meshhandler/test_src/surfmap.ply
	#python -m myprogram.asd myprogram/testbody.ply
	python -m myprogram.asd myprogram/test.ply

test_plainknit:
	python -m unittest createcloth.plainknit.test_plainknit

test_rechtsstrickzuangepasst:
	python -m unittest createcloth.rechtsstrickzuangepasst.test_rechtstrickzuangepasst
