from abc import ABC, abstractmethod
from collections.abc import Sequence, Mapping, Hashable, Container, MappingView, Iterable, Callable
from .strickgraph import strickgraph

#class comparable( ABC ):
#    __eq__, __gt__, __ge__, __lt__, __le__, __ne__

class identifier( ABC ):
    """
    
    :cvar attributes: possible attribute to classify a strickgraph
    """
    attributes: Mapping[ Hashable, Container ]
    
    @abstractmethod
    def classify( mystrickgraph: strickgraph ) -> Mapping[ Hashable, object ]:
        """asdf"""
        pass

    @abstractmethod
    def create_strickgraph( attributes: Mapping[ Hashable, object ] )\
                                    -> strickgraph:
        """asdf"""
        pass

    @abstractmethod
    def find_path( input_attributes: Mapping, output_attributes: Mapping )\
                                    -> Callable:#[ strickgraph, strickgraph ]:
        """asdf"""
        pass
