"""State machine files for recognizing lines and ESL."""
from typing import Dict, List, Optional, Tuple

from raesl.compile.machine_files import (
    behavior,
    builder,
    comments,
    component_definitions,
    component_instances,
    designs,
    goals,
    groups,
    needs,
    parameters,
    relation_definitions,
    relation_instances,
    transforms,
    type_defs,
    typing,
    variables,
    verb_defs,
)

# If not None, cached dict of line machine name to the state machine object.
_LINE_MACHINES: Optional[Dict[str, builder.ProcessingStateMachine]] = None


def collect_line_machines() -> Dict[str, builder.ProcessingStateMachine]:
    """Construct and collect all available line machine, and return them."""
    global _LINE_MACHINES

    if _LINE_MACHINES is not None:
        return _LINE_MACHINES

    _LINE_MACHINES = {}
    mach_builder = builder.StateMachineBuilder()

    collections: List[List[Tuple[str, str, Optional[typing.ProcessingFunc]]]] = [
        behavior.MACHINES,
        comments.MACHINES,
        component_definitions.MACHINES,
        component_instances.MACHINES,
        designs.MACHINES,
        goals.MACHINES,
        groups.MACHINES,
        needs.MACHINES,
        parameters.MACHINES,
        relation_definitions.MACHINES,
        relation_instances.MACHINES,
        transforms.MACHINES,
        type_defs.MACHINES,
        variables.MACHINES,
        verb_defs.MACHINES,
    ]

    for mach_collection in collections:
        for name, spec_text, proc_func in mach_collection:
            mach = mach_builder.create(spec_text, proc_func)
            _LINE_MACHINES[name] = mach

    return _LINE_MACHINES
