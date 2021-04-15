default: insertcolumn_right.xml insertcolumn_left.xml \
	removecolumn_left.xml removecolumn_right.xml \
	plain_extension_lowerleft.xml plain_extension_upperleft.xml \
	plain_extension_lowerright.xml plain_extension_upperright.xml \
	eaves_extension_lowerleft.xml eaves_extension_lowerright.xml \
	eaves_extension_upperleft.xml eaves_extension_upperright.xml

eaves_extension_upperleft.xml: src/eaves_createextension_upperleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.eaves_createextension_upperleft --output $@

eaves_extension_upperright.xml: src/eaves_createextension_upperleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.eaves_createextension_upperleft --reversed --output $@

eaves_extension_lowerleft.xml: src/eaves_createextension_lowerleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.eaves_createextension_lowerleft --output $@

eaves_extension_lowerright.xml: src/eaves_createextension_lowerleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.eaves_createextension_lowerleft --reversed --output $@

plain_extension_lowerleft.xml: src/plain_createextension_lowerleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.plain_createextension_lowerleft --output $@

plain_extension_lowerright.xml: src/plain_createextension_lowerleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.plain_createextension_lowerleft --reversed --output $@

plain_extension_upperleft.xml: src/plain_createextension_upperleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.plain_createextension_upperleft --output $@

plain_extension_upperright.xml: src/plain_createextension_upperleft.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.plain_createextension_upperleft --reversed --output $@

insertcolumn_left.xml: src/insertcolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.insertcolumn_right --reversed --output $@

insertcolumn_right.xml: src/insertcolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.insertcolumn_right --output $@

removecolumn_right.xml: src/removecolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.removecolumn_right --output $@

removecolumn_left.xml: src/removecolumn_right.py
	env PYTHONPATH="../../" python -m createcloth.builtin_verbesserer.src.removecolumn_right --output $@ --reversed


clean:
	-rm insertcolumn_left.xml
	-rm insertcolumn_right.xml
	-rm removecolumn_left.xml
	-rm removecolumn_right.xml
