default: insertcolumn_right.xml insertcolumn_left.xml removecolumn_left.xml removecolumn_right.xml

insertcolumn_left.xml: src/insertcolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.insertcolumn_right --reversed --output $@

insertcolumn_right.xml: src/insertcolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.insertcolumn_right --output $@

removecolumn_right.xml: src/removecolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.removecolumn_right > $@

removecolumn_left.xml: src/removecolumn_left.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.removecolumn_left > $@


clean:
	-rm insertcolumn_left.xml
	-rm insertcolumn_right.xml
	-rm removecolumn_left.xml
	-rm removecolumn_right.xml
