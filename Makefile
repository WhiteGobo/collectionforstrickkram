default:
	echo "hello"

install:
	echo "asd"


test:
	echo "test test"

create_verbesserung_for_rechtsstrickzuangepasst:
	python -m createcloth.rechtsstrickzuangepasst.src.compile_verbesserer

test_strickgraph:
	python -m unittest createcloth.strickgraph.test_strickgraph

test_meshhandler:
	#python -m unittest createcloth.meshhandler.test_meshhandler
	#python -m unittest createcloth.meshhandler.test_meshhandler.TestMeshhandlerMethods.test_create_surfacemap
	python -m unittest createcloth.meshhandler.test_meshhandler.TestMeshhandlerMethods.test_wholerelaxing

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

test_rechtsstrickzuangepasst:
	python -m unittest createcloth.rechtsstrickzuangepasst.test_rechtstrickzuangepasst
