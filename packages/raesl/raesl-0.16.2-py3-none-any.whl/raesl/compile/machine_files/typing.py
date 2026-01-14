"""Typing support for the machines data."""
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder

# Function signature of the processing function.
TokensDict = Dict[str, List["Token"]]
ProcessingFunc = Callable[[TokensDict, str, "AstBuilder"], None]

# Triplet in MACHINES variable.
MachineTriplet = Tuple[str, str, Optional[ProcessingFunc]]

# Type of the MACHINES variable.
MachineTripletList = List[MachineTriplet]
