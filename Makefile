default:
	echo "hello"

install:
	echo "asd"


test:
	echo "test test"

create_verbesserung_for_rechtsstrickzuangepasst:
	python -m pippackage.rechtsstrickzuangepasst.src.compile_verbesserer

test_strickgraph:
	python -m unittest pippackage.strickgraph.test_strickgraph

test_meshhandler:
	#python -m unittest pippackage.meshhandler.test_meshhandler
	#python -m unittest pippackage.meshhandler.test_meshhandler.TestMeshhandlerMethods.test_create_surfacemap
	python -m unittest pippackage.meshhandler.test_meshhandler.TestMeshhandlerMethods.test_wholerelaxing

test_manualtoverbesserung:
#	python -m unittest pippackage.verbesserer.test_verbesserer.test_manualtoverbesserung.test_xmlverbesserung
#	python -m unittest pippackage.verbesserer.test_verbesserer.test_manualtoverbesserung.test_tryingsimpleinsert
#	python -m unittest pippackage.verbesserer.test_verbesserer.test_manualtoverbesserung.test_multiersetzer
	python -m unittest pippackage.verbesserer.test_verbesserer

test_builtinverbesserer:
	python -m unittest pippackage.builtin_verbesserer.test_builtinverbesserer

show_relaxing:
	python pippackage/show_relaxing.py

test_toedgetension:
	python -m unittest pippackage.nodespannungtoedgespannung.test_toedgetension

test_rechtsstrickzuangepasst:
	python -m unittest pippackage.rechtsstrickzuangepasst.test_rechtstrickzuangepasst
