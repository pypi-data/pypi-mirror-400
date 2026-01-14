"""State machines to recognize lines of ESL."""
from typing import List, Set

from raesl.compile import machine_files
from raesl.compile.state_machine import StateMachine


def get_all_line_machines() -> List[StateMachine]:
    """Get all line state machines (for testing)."""
    machines: List[StateMachine] = list(machine_files.collect_line_machines().values())
    return machines


def get_line_machine_names() -> Set[str]:
    """Get the name of all line state machines (for testing)."""
    names = set(machine_files.collect_line_machines().keys())
    return names


def get_line_machine(name: str) -> machine_files.builder.ProcessingStateMachine:
    """Retrieve a line matcher state machine by name."""
    machine = machine_files.collect_line_machines()[name]
    return machine


# Specification defining the ESL language. Here, the token to take the
# transition is a successful match with a line machine (that is, recognition of
# one line ESL). Also, the 'epsilon' token exists here, which is a silent
# transition and can always be taken. Its use is to include other states in the
# search for a line match without copying all the transitions from that state.
# In this ESL specification, [epsilon] is used to recognize header lines while
# processing content.
_ESL_SPEC = """
esl:
    start initial, accept=esl_spec;
    start -> types [DEFINE_TYPE_MACHINE];
        types -> types_may_end [NEW_TYPE_MACHINE];
        types -> types_may_end [TYPE_IS_A_TYPE_MACHINE];
        types -> type_bundle [BUNDLE_TYPE_MACHINE];

        type_bundle -> type_bundle_may_end [BUNDLE_FIELD_MACHINE];

        type_bundle_may_end -> type_bundle_may_end [BUNDLE_FIELD_MACHINE];
        type_bundle_may_end -> types_may_end [epsilon];

        types_may_end -> types_may_end [NEW_TYPE_MACHINE];
        types_may_end -> types_may_end [TYPE_IS_A_TYPE_MACHINE];
        types_may_end -> type_bundle [BUNDLE_TYPE_MACHINE];
        types_may_end -> start [epsilon];


    start -> verbs [DEFINE_VERB_MACHINE];
        verbs -> verbs_may_end [VERB_PREPOS_MACHINE];

        verbs_may_end -> verbs_may_end [VERB_PREPOS_MACHINE];
        verbs_may_end -> start [epsilon];

    start -> reldefs [DEFINE_RELATION_MACHINE];
        reldefs -> new_reldef [RELATION_NAME_LINE_MACHINE];

        new_reldef -> reldef_params [RELATION_PARAMETER_HEADER_MACHINE];

        reldef_params -> reldef_params_may_end [RELATION_PARAMETER_LINE_MACHINE];

        reldef_params_may_end -> reldef_params_may_end [RELATION_PARAMETER_LINE_MACHINE];
        reldef_params_may_end -> reldef_params [RELATION_PARAMETER_HEADER_MACHINE];
        reldef_params_may_end -> new_reldef [RELATION_NAME_LINE_MACHINE];
        reldef_params_may_end -> start [epsilon];

    # Includes both normal definitions as well as 'world'.
    start -> component [DEFINE_COMPONENT_MACHINE];
        component -> start [EMPTY_MACHINE];

        component -> variables [VARIABLE_HEADER_MACHINE];
        component -> parameters [PARAMETER_HEADER_MACHINE];
        component -> groups [GROUP_SECTION_HEADER_MACHINE];
        component -> components [COMPONENT_HEADER_MACHINE];
        component -> needs [NEED_HEADER_MACHINE];
        component -> goals [GOAL_HEADER_MACHINE];
        component -> transforms [TRANSFORM_HEADER_MACHINE];
        component -> designs [DESIGN_HEADER_MACHINE];
        component -> relations [RELATION_HEADER_MACHINE];
        component -> behavior [BEHAVIOR_HEADER_MACHINE];
        component -> comments [COMMENT_HEADER_MACHINE];

        component_may_end -> variables [VARIABLE_HEADER_MACHINE];
        component_may_end -> parameters [PARAMETER_HEADER_MACHINE];
        component_may_end -> groups [GROUP_SECTION_HEADER_MACHINE];
        component_may_end -> components [COMPONENT_HEADER_MACHINE];
        component_may_end -> needs [NEED_HEADER_MACHINE];
        component_may_end -> goals [GOAL_HEADER_MACHINE];
        component_may_end -> transforms [TRANSFORM_HEADER_MACHINE];
        component_may_end -> designs [DESIGN_HEADER_MACHINE];
        component_may_end -> relations [RELATION_HEADER_MACHINE];
        component_may_end -> behavior [BEHAVIOR_HEADER_MACHINE];
        component_may_end -> comments [COMMENT_HEADER_MACHINE];


    # Variables
    variables -> variables_may_end [VARIABLE_LINE_MACHINE];

    variables_may_end -> variables_may_end [VARIABLE_LINE_MACHINE];
    variables_may_end -> start [epsilon];
    variables_may_end -> component_may_end [epsilon];


    # Parameters
    parameters -> parameters_may_end [PARAMETER_LINE_MACHINE];

    parameters_may_end -> parameters_may_end [PARAMETER_LINE_MACHINE];
    parameters_may_end -> start [epsilon];
    parameters_may_end -> component_may_end [epsilon];


    # Groups
    groups -> group_started [GROUP_START_MACHINE];

    group_started -> group_may_end [GROUP_ARGUMENT_LINE_MACHINE];

    group_may_end -> group_may_end [GROUP_ARGUMENT_LINE_MACHINE];
    group_may_end -> group_started [GROUP_START_MACHINE];
    group_may_end -> start [epsilon];
    group_may_end -> component_may_end [epsilon];


    # Components
    components -> components_args [COMPONENT_INSTANCE_WITH_ARGS_MACHINE];
    components -> components_may_end [COMPONENT_INSTANCE_NO_ARGS_MACHINE];

    components_args -> components_args_may_end [COMPONENT_ARGUMENT_MACHINE];

    components_args_may_end -> components_args_may_end [COMPONENT_ARGUMENT_MACHINE];
    components_args_may_end -> components_args [COMPONENT_INSTANCE_WITH_ARGS_MACHINE];
    components_args_may_end -> components_may_end [COMPONENT_INSTANCE_NO_ARGS_MACHINE];
    components_args_may_end -> start [epsilon];
    components_args_may_end -> component_may_end [epsilon];

    components_may_end -> components_args [COMPONENT_INSTANCE_WITH_ARGS_MACHINE];
    components_may_end -> components_may_end [COMPONENT_INSTANCE_NO_ARGS_MACHINE];
    components_may_end -> start [epsilon];
    components_may_end -> component_may_end [epsilon];


    # Needs
    needs -> needs_may_end [NEED_LINE_MACHINE];

    needs_may_end -> needs_may_end [NEED_LINE_MACHINE];
    needs_may_end -> component_may_end [epsilon];
    needs_may_end -> start [epsilon];


    # Goals
    goals -> goals_may_end [GOAL_MAIN_NO_SUBS_MACHINE];
    goals -> goals_subs [GOAL_MAIN_WITH_SUBS_MACHINE];

    goals_subs -> goals_subs_may_end [GOAL_SUB_CLAUSE_MACHINE];

    goals_subs_may_end -> goals_subs_may_end [GOAL_SUB_CLAUSE_MACHINE];
    goals_subs_may_end -> goals_may_end [GOAL_MAIN_NO_SUBS_MACHINE];
    goals_subs_may_end -> goals_subs [GOAL_MAIN_WITH_SUBS_MACHINE];
    goals_subs_may_end -> component_may_end [epsilon];
    goals_subs_may_end -> start [epsilon];

    goals_may_end -> goals_may_end [GOAL_MAIN_NO_SUBS_MACHINE];
    goals_may_end -> goals_subs [GOAL_MAIN_WITH_SUBS_MACHINE];
    goals_may_end -> component_may_end [epsilon];
    goals_may_end -> start [epsilon];


    # Transforms
    transforms -> transforms_may_end [TRANSFORM_MAIN_NO_SUBS_MACHINE];
    transforms -> transforms_subs [TRANSFORM_MAIN_WITH_SUBS_MACHINE];

    transforms_subs -> transforms_subs_may_end [TRANSFORM_SUB_CLAUSE_MACHINE];

    transforms_subs_may_end -> transforms_subs_may_end [TRANSFORM_SUB_CLAUSE_MACHINE];
    transforms_subs_may_end -> transforms_may_end [TRANSFORM_MAIN_NO_SUBS_MACHINE];
    transforms_subs_may_end -> transforms_subs [TRANSFORM_MAIN_WITH_SUBS_MACHINE];
    transforms_subs_may_end -> component_may_end [epsilon];
    transforms_subs_may_end -> start [epsilon];

    transforms_may_end -> transforms_may_end [TRANSFORM_MAIN_NO_SUBS_MACHINE];
    transforms_may_end -> transforms_subs [TRANSFORM_MAIN_WITH_SUBS_MACHINE];
    transforms_may_end -> component_may_end [epsilon];
    transforms_may_end -> start [epsilon];


    # Designs
    designs -> designs_may_end [DESIGN_NO_SUBS_MACHINE];
    designs -> designs_subs [DESIGN_WITH_SUBS_MACHINE];

    designs_subs -> designs_subs_may_end [DESIGN_SUB_CLAUSE_MACHINE];

    designs_subs_may_end -> designs_subs_may_end [DESIGN_SUB_CLAUSE_MACHINE];
    designs_subs_may_end -> designs_may_end [DESIGN_NO_SUBS_MACHINE];
    designs_subs_may_end -> designs_subs [DESIGN_WITH_SUBS_MACHINE];
    designs_subs_may_end -> component_may_end [epsilon];
    designs_subs_may_end -> start [epsilon];

    designs_may_end -> designs_may_end [DESIGN_NO_SUBS_MACHINE];
    designs_may_end -> designs_subs [DESIGN_WITH_SUBS_MACHINE];
    designs_may_end -> component_may_end [epsilon];
    designs_may_end -> start [epsilon];


    # Behavior
    behavior -> behavior_entry [BEHAVIOR_NAME_MACHINE];

    behavior_entry -> behavior_case [BEHAVIOR_CASE_MACHINE];

    behavior_case -> behavior_when [BEHAVIOR_WHEN_MACHINE];
    behavior_case -> behavior_otherwise [BEHAVIOR_WHEN_OTHERWISE_MACHINE];

    behavior_when -> behavior_when_cond [BEHAVIOR_WHEN_CONDITION_MACHINE];

    behavior_when_cond -> behavior_when_cond [BEHAVIOR_WHEN_CONDITION_MACHINE];
    behavior_when_cond -> behavior_then [BEHAVIOR_THEN_MACHINE];

    behavior_otherwise -> behavior_then [BEHAVIOR_THEN_MACHINE];

    behavior_then -> behavior_then_result [BEHAVIOR_THEN_RESULT_MACHINE];

    behavior_then_result -> behavior_then_result [BEHAVIOR_THEN_RESULT_MACHINE];
    behavior_then_result -> behavior_case [BEHAVIOR_CASE_MACHINE];
    behavior_then_result -> behavior_entry [BEHAVIOR_NAME_MACHINE];
    behavior_then_result -> component_may_end [epsilon];
    behavior_then_result -> start [epsilon];


    # Relations
    relations -> relations_arguments [RELATION_INSTANCE_MACHINE];

    relations_arguments -> relations_subs [RELATION_ARGUMENT_HEADER_MACHINE];

    relations_subs -> relations_may_end [RELATION_ARGUMENT_MACHINE];

    relations_may_end -> relations_may_end [RELATION_ARGUMENT_MACHINE];
    relations_may_end -> relations_arguments [RELATION_INSTANCE_MACHINE];
    relations_may_end -> relations_subs [RELATION_ARGUMENT_HEADER_MACHINE];
    relations_may_end -> component_may_end [epsilon];
    relations_may_end -> start [epsilon];


    # Comments
    comments -> comments_may_end [COMMENT_LINE_MACHINE];

    comments_may_end -> comments_may_end [COMMENT_LINE_MACHINE];
    comments_may_end -> component_may_end [epsilon];
    comments_may_end -> start [epsilon];
"""  # noqa
_BUILDER = machine_files.builder.StateMachineBuilder()
ESL_MACHINE = _BUILDER.create(_ESL_SPEC)
