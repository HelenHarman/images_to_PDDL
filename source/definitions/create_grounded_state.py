#---------------------------------------
import itertools

from definitions import domain_definition
from definitions.domain_definition import PredicateDefinition
from definitions.grounded_state import Atom, GroundedState
from definitions.object_definitions import LocationDefinition

#-------------------------------------------

def create_grounded_pre_and_suc_states(transition, location_definitions, image_object_definitions):
    pre_ground_state = GroundedState()
    suc_ground_state = GroundedState()

    transition_pre_image = transition.pre_image.get_image()
    transition_suc_image = transition.suc_image.get_image()

    locations_that_change = []
    #-----------
    # add the state for the locations (and thus objects) that change state:
    for changed_image_area in transition.changed_image_areas:
        location_definition = get_location_definition_for_image_area(changed_image_area, location_definitions)
        image_object_definition_pre = get_image_object_at_location(transition_pre_image, location_definition, image_object_definitions)
        image_object_definition_suc = get_image_object_at_location(transition_suc_image, location_definition, image_object_definitions)

        pre_ground_state = add_location_and_image_object_to_state(pre_ground_state, location_definition, image_object_definition_pre)
        suc_ground_state = add_location_and_image_object_to_state(suc_ground_state, location_definition, image_object_definition_suc)

        locations_that_change.append(location_definition)

        # location_definition currently only has the images it can be; therefore, here we add the ids of the objects it can be:
        #--location_definition.add_image_object_definition_change_from_to(image_object_definition_pre, image_object_definition_suc)

    add_changed_together_link_atom_to_states(locations_that_change, pre_ground_state)

    #-----------
    # for all locations that don't change add their atoms to the states:
    for location_definition in location_definitions:
        if location_definition in locations_that_change:
            continue
        image_object_definition = get_image_object_at_location(transition_pre_image, location_definition, image_object_definitions)

        pre_ground_state = add_location_and_image_object_to_state(pre_ground_state, location_definition, image_object_definition)
        suc_ground_state = add_location_and_image_object_to_state(suc_ground_state, location_definition, image_object_definition)

    #-----------
    # create the list of preconditions and effects:
    preconditions_known, preconditions_possible, effects = create_grounded_preconditions_and_effects_from_states(pre_ground_state, suc_ground_state, location_definitions, image_object_definitions)
    return pre_ground_state, suc_ground_state, preconditions_known, preconditions_possible, effects

#------------------------------------------------------

def get_location_definition_for_image_area(changed_image_area, location_definitions):
    for location_definition in location_definitions:
        if changed_image_area == location_definition.image_area:
            return location_definition
    return None

#------------------------------------------------------

def get_image_object_at_location(image, location_definition, image_object_definitions):
    for image_object_definition in image_object_definitions:
        if (image_object_definition.image_object_area.is_at_location_in_image(location_definition, image)):
            return image_object_definition
    return None

#------------------------------------------------------

def add_location_and_image_object_to_state(grounded_state, location_definition, image_object_definition):
    if ((image_object_definition == None) and (location_definition.get_defined_predicates())):
        grounded_state.add_atom(Atom(location_definition.get_defined_predicates()[0], [location_definition])) # i.e., is-clear
    else:
        grounded_state.add_atom(Atom(location_definition.get_defined_predicates()[0], [location_definition], True))  # True == is negated atom # i.e., (not (is-clear))
        grounded_state.add_atom(Atom(image_object_definition.get_defined_predicates()[0], [image_object_definition, location_definition])) # i.e., (at ?loc ?img)
    return grounded_state

#-------------------------------------------------

#===========================================================
# Methods for creating the preconditions_known, preconditions_possible, effects:

def create_grounded_preconditions_and_effects_from_states(pre_ground_state, suc_ground_state, location_definitions, image_object_definitions):
    preconditions_known, preconditions_possible, effects = [], [], []
    created_preconditions_known_and_effects_for_object_definitions(image_object_definitions, pre_ground_state, suc_ground_state, preconditions_known, effects)
    created_preconditions_known_and_effects_for_object_definitions(location_definitions, pre_ground_state, suc_ground_state, preconditions_known, effects)

    # add the static precondition:
    preconditions_known.extend(pre_ground_state.associated_static_atoms)

    # fill-in preconditions_possible with the remaining pre_ground_state atoms
    for pre_ground_atom in pre_ground_state.fluent_atoms:
        if (pre_ground_atom not in preconditions_known):
            preconditions_possible.append(pre_ground_atom)

    return preconditions_known, preconditions_possible, effects

#------------------------------------------------

def created_preconditions_known_and_effects_for_object_definitions(object_definitions, pre_ground_state, suc_ground_state, preconditions_known, effects):
    for image_object_definitions in object_definitions:
        pre_fluent_atoms_for_object = pre_ground_state.get_fluent_atoms_for_object(image_object_definitions)
        suc_fluent_atoms_for_object = suc_ground_state.get_fluent_atoms_for_object(image_object_definitions)

        to_be_inserted_preconditions_known = []
        to_be_inserted_effects = []
        for pre_fluent in pre_fluent_atoms_for_object:
            if pre_fluent not in suc_fluent_atoms_for_object:
                to_be_inserted_preconditions_known.append(pre_fluent)
        for suc_fluent in suc_fluent_atoms_for_object:
            if suc_fluent not in pre_fluent_atoms_for_object:
                to_be_inserted_effects.append(suc_fluent)


        #--if (pre_fluent_atoms_for_object and suc_fluent_atoms_for_object and (pre_fluent_atoms_for_object != suc_fluent_atoms_for_object)): # if both not empty
            #add_atoms_and_negated_atoms_to_lists(pre_fluent_atoms_for_object, preconditions_known, effects)
            #add_atoms_and_negated_atoms_to_lists(suc_fluent_atoms_for_object, effects, preconditions_known)
        if (to_be_inserted_preconditions_known):
            add_atoms_and_negated_atoms_to_lists(to_be_inserted_preconditions_known, preconditions_known, effects)
        if (to_be_inserted_effects):
            add_atoms_and_negated_atoms_to_lists(to_be_inserted_effects, effects, preconditions_known)
#------------------------------------------------

def add_atoms_and_negated_atoms_to_lists(atoms, positive_atoms, negated_atoms):
    for atom in atoms: # add both the negative preconditions and effects <-- only used for known preconditions and effects
        if (not atom.negated):
            if atom not in positive_atoms:
                positive_atoms.append(atom)
            negated_atom = Atom(atom.predicate, atom.defined_objects, True)
            if negated_atom not in negated_atoms:
                negated_atoms.append(negated_atom)

#---------------------------------------

#==================================================================
#   Create static atoms

#======------------------------------------------
# create linked together atoms (i.e., these two locations change state at the same time):

def add_changed_together_link_atom_to_states(location_definitions, grounded_state): # will be added to all states
    predicate = create_changed_together_link_predicate(location_definitions)
    location_definitions_perms = list(itertools.permutations(location_definitions))
    for location_definitions_perm in location_definitions_perms:
        location_definitions_perm[0].changed_together.append(location_definitions_perm[1:])
        atom = Atom(predicate, location_definitions_perm, False, True)
        grounded_state.add_atom(atom)
    return atom

#---------------------------------------

def create_changed_together_link_predicate(location_definitions):
    predicate_name = "changed_together_link_" + str(len(location_definitions)) #"changed_together_link"
    for predicate in domain_definition.defined_predicates:
        if (predicate.name == predicate_name): # and len(predicate.param_types) == len(location_definitions):
            return predicate
    lst = [LocationDefinition.type] * len(location_definitions)
    return PredicateDefinition(predicate_name, lst)

#======------------------------------------------
#  Create the "depends_on" predicate:

def create_depends_on_grounded_precondition(action_node, location_definition, state_of_location_definition, preconditions_to_link_to): #<-- only use this for locations
    defined_object_dependencies = location_definition.create_defined_object_dependencies_and_add_depends_on(preconditions_to_link_to, state_of_location_definition)
    create_depends_on_atom_and_add_to_preconditions_diff_permutations(location_definition, defined_object_dependencies, action_node)

    #defined_object_dependencies.insert(0, location_definition)
    #create_depends_on_atom_and_add_to_preconditions(defined_object_dependencies, action_node) #state_of_location_definition

#----------------------------

def create_depends_on_atom_and_add_to_preconditions_diff_permutations(object_definition, defined_object_dependencies, action_node): #<-- used for both locations and image_objects
    defined_object_dependencies_perms = list(itertools.permutations(defined_object_dependencies))
    for defined_object_dependencies_perm in defined_object_dependencies_perms:
        params = [object_definition]
        params.extend(defined_object_dependencies_perm)
        create_depends_on_atom_and_add_to_preconditions(params, action_node)

#----------------------------

def create_depends_on_atom_and_add_to_preconditions(defined_object_dependencies, action_node, state_id = -404):
    predicate = create_depends_on_predicate(defined_object_dependencies, state_id)
    # create atom from the predicate
    atom = Atom(predicate, defined_object_dependencies, False, True)  # predicate, defined_objects, negated = False, is_static = False
    #print("created dep atom: " + str(atom))

    action_node.pre_grounded_state.add_atom(atom) # add to pre_state of action, (is avaliable in all instances - i.e., is static)
    action_node.add_depends_on_preconditions(atom) # add to preconditions.  Note, we don't need to make more OR nodes, as we just add static atoms

#---------------------------------------

def create_depends_on_predicate(defined_object_dependencies, state_id):
    if (state_id != -404):
        predicate_name = "depends_on_"+ str(state_id) + "_"+str(len(defined_object_dependencies)) # <-- unused
    else:
        predicate_name = "depends_on_"+str(len(defined_object_dependencies))
    for predicate in domain_definition.defined_predicates:
        if (predicate.name == predicate_name):
            return predicate
    types = ["object"] * len(defined_object_dependencies) # object == any type
    return PredicateDefinition(predicate_name, types)


#=========================================================================================
#=========================================================================================
