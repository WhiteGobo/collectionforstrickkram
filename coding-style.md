# Module Construction

## Constants
Constants are declared in the corresponding `__init__.py`, e.g.
`createcloth.strickgraph.__init__.py` has the attribute
`handknitting_terms`. The description of each constant is below the
attribute e.g.:

	handknitting_terms=["thread", "handknit", "handknitting"]
	"""List of all available terms, that describe handknittint"""

Constants can be imported via importing the module itself and using 
its attributes:

	from .. import strickgraph as mymodule
	mymodule.handknitting_terms

*Dont import constants directly!* Always use the showed indirect import. 
**Do not** `from ..strickgraph import handknitting_terms` to import constants.

### a little reasoning behind this
Having modulewide constants is hard. Sometimes you need them in different files
and having to search for them is not nice. Also python imports doesnt allow
loops. But you can import modules which would create import-loops,
if you dont unpack them. So importing the module works, but importing a variable
from the module may lead to an import-loop.
