#version =$$(python -c 'import setuptools as sut; print(sut.config.read_configuration("setup.cfg")["metadata"]["version"])')
#pkgname =$$(python -c 'import setuptools as sut; print(sut.config.read_configuration("setup.cfg")["metadata"]["name"])')
version = 0.1
pkgname = createcloth

ALTGENOPT = -l 7 -w 26 --continue -n 24 -t 300 --softtimelimit 240 --softmaximumuncommonnodes 8

default: build install
	echo "hello"


install: #dist/$(pkgname)-$(version).tar.gz
	pip uninstall $(pkgname) -y
	pip install dist/$(pkgname)-$(version)-py3-none-any.whl --force-reinstall
	#pip install dist/$(pkgname)-$(version).tar.gz --force-reinstall

CREATEPLAINKNIT_ALTERATOR = python -m createcloth.plainknit.program_create_alterator

test_asdf:
	$(CREATEPLAINKNIT_ALTERATOR) tmp/qq.xml $(ALTGENOPT)

createcloth/plainknit/plainknit_increaser.xml: 
	$(CREATEPLAINKNIT_ALTERATOR) $@ $(ALTGENOPT) --limitend 2000 --limitstart 1000 
	#python -m createcloth.plainknit.program_create_alterator $@ -l 8 -w 30 --continue

createcloth/plainknit/plainknit_decreaser.xml: 
	$(CREATEPLAINKNIT_ALTERATOR) $@ $(ALTGENOPT) --alteratortype decrease --limitstart 1000 --limitend 2000
	#python -m createcloth.plainknit.program_create_alterator $@ -l 8 -w 26 --continue --alteratortype decrease

.PHONY: testoldalt
testoldalt:
	$(CREATEPLAINKNIT_ALTERATOR) createcloth/plainknit/plainknit_decreaser.xml --testold --alteratortype decrease
	$(CREATEPLAINKNIT_ALTERATOR) createcloth/plainknit/plainknit_increaser.xml --testold $(ALTGENOPT)

.PHONY: build
build: 
	-rm dist/*
	-python -m build

documentation:
	cd docs && $(MAKE) html

create_verbesserung_for_rechtsstrickzuangepasst:
	python -m createcloth.rechtsstrickzuangepasst.src.compile_verbesserer


test_stitchinfo:
	python -m unittest createcloth.stitchinfo.test_stitchinfo

.PHONY: test
test: #test_strickgraph test_meshhandler test_manualtoverbesserung test_plainknit
	python -m unittest -k createcloth

test_interactive:
	env INTERACTIVE= python -m unittest -k visualizer


test_clothfactory:
	python -m unittest clothfactory_parts.test_clothfactory_parts

.PHONY: test_strickgraph
test_strickgraph:
	python -m unittest createcloth.strickgraph.test_strickgraph


.PHONY: test_meshhandler
test_meshhandler:
	python -m unittest createcloth.meshhandler.test_meshhandler -k test_wholerelaxing

.PHONY: test_manualtoverbesserung
test_manualtoverbesserung:
	python -m unittest createcloth.verbesserer.test_verbesserer -k test_sidealterator

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

.PHONY: test_plainknit
test_plainknit:
	python -m unittest createcloth.plainknit.test_plainknit

test_rechtsstrickzuangepasst:
	python -m unittest createcloth.rechtsstrickzuangepasst.test_rechtstrickzuangepasst

.PHONY: myk
myk: qq/asdf.mime.xml
	python -m clothfactory_parts.programs.complete_datagraph qq

qq/asdf.mime.xml:
	-mkdir qq
	python -m clothfactory_parts.programs.create_directory_strickcompleter qq/ clothfactory_parts/test/testbody_withmap.ply 
