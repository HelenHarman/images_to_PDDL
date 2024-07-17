from definitions.domain_definition import ActionDefinition, DefinedAtom

DEBUG_CREATE_ACTION_DEFINITIONS = False #True

#--------------------------------------------------

def create_action_definitions(action_nodes):
    action_definitions = []
    for action_node in action_nodes:
        create_definition_for_action(action_node, action_definitions)

    print("total number of action_definitions= " + str(len(action_definitions)))
    #-- debug:
    debug_print_action_defs(action_definitions)

    return action_definitions

#--------------------------------------------------

def create_definition_for_action(action_node, action_definitions):
    for action_definition in action_definitions:
        if action_definition.is_grounding_of_action(action_node):
            return # action definition for action_node already exists, so we don't need to make one.

    action_definition = ActionDefinition()
    defined_objects_to_pre_and_eff = action_node.get_parameters_with_their_preconditions_and_effects()
    defined_objects_for_action = list(defined_objects_to_pre_and_eff.keys()) # these will be used as the action_definitions parameters.
    for i in range(len(defined_objects_for_action)): #defined_object
        action_definition.param_types.append(defined_objects_for_action[i].get_type())
        # create action definitions preconditions:
        for precondition in defined_objects_to_pre_and_eff[defined_objects_for_action[i]][0]:
            defined_atom = transform_grounded_atom_into_atom_definition(precondition, defined_objects_for_action)
            action_definition.add_precondition(defined_atom, i)

        # create action definitions effects:
        for effect in defined_objects_to_pre_and_eff[defined_objects_for_action[i]][1]:
            defined_atom = transform_grounded_atom_into_atom_definition(effect, defined_objects_for_action)
            action_definition.add_effect(defined_atom, i)

    action_definitions.append(action_definition)

#---------------

def transform_grounded_atom_into_atom_definition(atom, defined_objects_for_action):
    defined_atom_objects = []
    for defined_object in atom.defined_objects:
        defined_atom_objects.append(defined_objects_for_action.index(defined_object)) #
    defined_atom = DefinedAtom(atom.predicate, defined_atom_objects, atom.negated, atom.is_static)
    return defined_atom


#================================================================
#------------------------------------------------
def debug_print_action_defs(action_definitions):
    if (not DEBUG_CREATE_ACTION_DEFINITIONS):
        return
    index = 0
    for action_definition in action_definitions:
        if (index > 12):
            break
        print(action_definition)
        index = index + 1
#------------------------------------------------


#================================================================
#================================================================

"""


def create_action_definitions(all_actions, defined_objects):
    action_definitions = []
    for action in all_actions:
        defined_params, defined_preconditions, defined_effects = defined_actions.create_action_definition(action)
        added_action_def = False
        for action_def in action_definitions:
            if (action_def.add_action_node(action, defined_params, defined_preconditions, defined_effects)):
                added_action_def = True
                break
        if (not added_action_def):
            def_action = DefinedAction()
            def_action.params = defined_params
            def_action.preconditions = defined_preconditions
            def_action.effects = defined_effects
            action_definitions.append(def_action)
    print_debug(action_definitions, all_actions)

    return action_definitions

def print_debug(action_definitions, all_actions):
    print ("------------------------------------------")
    print ("all_actions=" + str(len(all_actions)))
    print ("action_definitions=" + str(len(action_definitions)))

    for action_definition in action_definitions:
        print(action_definition)

    print ("------------------------------------------")


"""