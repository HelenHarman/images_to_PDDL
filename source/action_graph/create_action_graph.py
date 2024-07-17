import cv2
import numpy as np

import util_images_to_pddl
from action_graph.action_node import ActionNode
from action_graph.operator_node import OrNode, AndNode, DepNode
from definitions import create_grounded_state, grounded_state, domain_definition

DEBUG_CREATE_ACTION_GRAPH = False #True #

def create_action_graph(transitions, location_definitions, image_object_definitions): #all_objects,
    #----------
    # create action graph:
    #is_only_one_clear_location_in_all_states = True #<-- this is returned by the function call
    action_nodes, is_only_one_clear_location_in_all_states = create_action_nodes(transitions, location_definitions, image_object_definitions) #, is_only_one_clear_location_in_all_states)
    create_operator_initial_graph(action_nodes)

    #--- debug:
    debug_print_grounded_actions(action_nodes, True)

    #---------
    # make/remove precondtions:
    create_depends_on_atoms_and_remove_unrequired_preconditions(action_nodes, location_definitions, image_object_definitions, is_only_one_clear_location_in_all_states)

    # --- debug:
    debug_print_action_states(action_nodes)
    debug_show_object_id(action_nodes, location_definitions)
    debug_print_grounded_actions(action_nodes)
    return action_nodes

#=====================================================
#    CREATE INITIAL ACTION GRAPH:

def create_action_nodes(transitions, location_definitions, image_object_definitions): #, is_only_one_clear_location_in_all_states = True):
    action_nodes = []
    is_only_one_clear_location_in_all_states = True
    for transition in transitions:
        pre_grounded_state, suc_grounded_state, preconditions_known, preconditions_possible, effects = create_grounded_state.create_grounded_pre_and_suc_states(transition, location_definitions, image_object_definitions)
        if (is_only_one_clear_location_in_all_states): #
            is_only_one_clear_location_in_all_states = (pre_grounded_state.has_one_clear_location() and suc_grounded_state.has_one_clear_location())
        action_nodes.append(ActionNode(transition, pre_grounded_state, suc_grounded_state, preconditions_known, preconditions_possible, effects)) #

    return action_nodes, is_only_one_clear_location_in_all_states

#---------------------------------------------------------

def create_operator_initial_graph(action_nodes):
    for action_node in action_nodes:
        or_nodes = []
        create_or_node_for_each_precondition(action_node.preconditions_known, action_nodes, True, or_nodes)
        action_node.preconditions_missing_dep = create_or_node_for_each_precondition(action_node.preconditions_possible, action_nodes, False, or_nodes)

        # create and_node with the or_nodes as chrildren (constructor also sets the chidlren's parent)
        and_node = AndNode(or_nodes)
        # Create DEP node (and if needed move action_node's parents to be the DEP node's parents):
        parents = action_node.parents.copy()
        dep_node = DepNode([and_node, action_node])
        for parent in parents:
            parent.replace_child(action_node, dep_node)
    preconditions_to_or_node.clear() # clean-up
#--------------------------------------------------
preconditions_to_or_node = {}
def create_or_node_for_each_precondition(preconditions, action_nodes, are_known_preconditions, or_nodes):
    global preconditions_to_or_node
    preconditions_missing_dep = []
    for precondition in preconditions:
        if precondition.is_static:
            continue
        if (precondition in preconditions_to_or_node):
            if (isinstance(preconditions_to_or_node[precondition], OrNode)):
                or_node = OrNode(preconditions_to_or_node[precondition].children.copy(), precondition, are_known_preconditions)
            else:
                or_node = None
            #or_node = preconditions_to_or_node[precondition]
        else:
            or_node = create_or_node_for_precondition(precondition, action_nodes, are_known_preconditions)
            preconditions_to_or_node[precondition] = or_node
        if (or_node == None):
            preconditions_missing_dep.append(precondition)
        else: #  if another or_node's chrildren are the or_node's chrildren: add the precondition to its preconditions; otherwise: just add the or node to the list:
            found = False
            for listed_or_node in or_nodes:
                if or_node.do_children_match(listed_or_node):
                    listed_or_node.preconditions.append(precondition)
                    #util_images_to_pddl.debug_print("or - pre=" + str(len(listed_or_node.preconditions)))
                    found = True
                    break
            if (not found):
                or_nodes.append(or_node)
    return preconditions_missing_dep

#--------------------------------------------------

def create_or_node_for_precondition(precondition, action_nodes, is_known_precondition):
    actions_for_precondition = get_actions_that_set_precondition(precondition, action_nodes)
    if (not actions_for_precondition):
        return None
    else: # create OR node:
        children = []
        for action in actions_for_precondition:
            children.append(action.get_dep_node_or_self())
        return OrNode(children, precondition, is_known_precondition)

#--------------------------------------------------

def get_actions_that_set_precondition(precondition, action_nodes):
    actions_for_precondition = []
    for action_node in action_nodes:
        for effect in action_node.effects:
            if precondition == effect:
                actions_for_precondition.append(action_node)
                break
    return actions_for_precondition

#--------------------------------------------------

#==========================================================================================
# CREATE DEPENDS-ON ATOMS AND REMOVE PRECONDITIONS THAT THE CHANGED OBJECTS DON'T DEPEND-ON:
def create_depends_on_atoms_and_remove_unrequired_preconditions(action_nodes, location_definitions, image_object_definitions, is_only_one_clear_location_in_all_states): #reduce_number_of_preconditions
    #print ("create_depends_on_atoms_and_remove_unrequired_preconditions")
    #remove_possible_preconditions_without_dependencies(action_nodes)
    #return
    # TODO!!! does lights-out and ToH still work with this line:?????
    remove_non_clear_locations_from_preconditions(action_nodes, is_only_one_clear_location_in_all_states, image_object_definitions)

    #-------------
    # Discover location's dependencies (a location can depend on objects as well as locations):
    #   everytime a location_definition changes state what are the common states; e.g. loc2 is always clear; loc8 is always not clear; image_object5 is always at loc3; loc3 is always not-clear
    find_actions_that_modify_location_and_their_common_atoms(action_nodes, location_definitions)
    determine_which_objects_each_location_depends_on(location_definitions)

   # print ("done location dep")
    # -------------
    # Discover image_object's dependencies (an image_object can only depend on other image objects <-- the location has already been fixed bu the location's dependencies)
    create_object_dependency_atoms(action_nodes, image_object_definitions, location_definitions)
   # print("done object dep")
    # -------------
    # Remove preconditions that the objects that change state do not depend on
    remove_possible_preconditions_without_dependencies(action_nodes)
   # print("done rm")


# ================--------------------------------------------------------------
# REDUCE OR NODES: is_only_one_clear_location_in_all_states remove all none-clear locations from the preconditions
# WE USE THIS AGAIN: so that missing transitions works. # NO-LONGER USED # no-longer required (as these won't depend on anything, they will be removed any way):
def remove_non_clear_locations_from_preconditions(action_nodes, is_only_one_clear_location_in_all_states, image_object_definitions):
    if ((is_only_one_clear_location_in_all_states)): # or (len(image_object_definitions) == 1)): # if there is only one image object then we know the all states without the image object are clear.
        for action_node in action_nodes:
            known_has_clear_location = False
            for pre_atom in action_node.preconditions_known:
                if (pre_atom.predicate.name == "clear" and (not pre_atom.negated)):
                    known_has_clear_location = True
                    break
            if (known_has_clear_location):
                for pre_atom in action_node.preconditions_possible:
                    if (pre_atom.predicate.name == "clear" and pre_atom.negated):
                        action_node.preconditions_possible.remove(pre_atom)# .add_precondition_to_be_removed(pre_atom)


# ================--------------------------------------------------------------
# Discover location's dependencies
def find_actions_that_modify_location_and_their_common_atoms(action_nodes, location_definitions): #remove_precondition_if_not_true_each_time_change_is_observed
    for location_definition in location_definitions:
        resulting_states_to_actions = get_actions_that_modify_location(location_definition, action_nodes)
        for resulting_value_of_location in resulting_states_to_actions:
            actions = resulting_states_to_actions[resulting_value_of_location]
            common_preconditions = actions[0].preconditions_possible.copy()
            for action in actions:
                common_preconditions = grounded_state.get_common_atoms(action.preconditions_possible, common_preconditions)
            location_definition.add_value_to_actions_and_common_atoms(resulting_value_of_location, actions, common_preconditions)

#-----------------------------------------------

def get_actions_that_modify_location(location_definition, action_nodes):
    resulting_states_to_actions = {} # e.g. 0 --> [action_node,], -1 --> [action_node,]
    for action_node in action_nodes:
        effect = action_node.get_effect_for_object_definition(location_definition)
        if (effect != None):
            state_id = location_definition.translate_atom_into_state_id(effect)
            if state_id in resulting_states_to_actions:
                resulting_states_to_actions[state_id].append(action_node)
            else:
                resulting_states_to_actions[state_id] = [action_node]
    return resulting_states_to_actions


# ================--------------------------------------------------------------
# Determine locations' dependencies
def determine_which_objects_each_location_depends_on(location_definitions):#remove_preconditions_that_are_preconditions_of_preconditions
    for location_definition in location_definitions:
        for resulting_value in location_definition.value_to_actions_that_result_in_value_and_their_common_atoms:
            actions = location_definition.value_to_actions_that_result_in_value_and_their_common_atoms[resulting_value][0]
            states_to_be_modified = location_definition.value_to_actions_that_result_in_value_and_their_common_atoms[resulting_value][1]  # group together the states relating to the same known precondition

            action_node = actions[0] # any action could have been picked
            max_number_of_removed_preconditions = 0
            preconditions_of_remove = [] # i.e., the preconditions we must keep
            for or_node in action_node.get_or_nodes():
                # ------------------------
                # initialise common_state:
                common_state = []  # action_node.preconditions_possible.copy()
                for atom in states_to_be_modified:
                    if ((atom in action_node.preconditions_possible) and (not atom.is_static)):  # .get_possible_preconditions_without_to_remove()
                        common_state.append(atom)
                if (or_node.preconditions[0] not in common_state):  # if this or-node belongs to other location:
                    continue
                for precondition in or_node.preconditions:  # shouldn't remove itself from the action's precondtions
                    common_state.remove(precondition)

                # ------------------------
                # get state common to the or_nodes resulting state :
                or_action_nodes = or_node.get_action_nodes()
                for or_action_node in or_action_nodes:
                    common_state = grounded_state.get_common_atoms(common_state, or_action_node.suc_grounded_state.fluent_atoms)#.suc_grounded_state.fluent_atoms)

                # -----------------------
                # we want to remove as many preconditions as possible, so keep track of the equally largest ones (we should double check if this works for all domains):
                if ((common_state) and (max_number_of_removed_preconditions < len(common_state))):
                    max_number_of_removed_preconditions = len(common_state)
                    preconditions_of_remove = or_node.preconditions.copy()
                elif ((max_number_of_removed_preconditions != 0) and (max_number_of_removed_preconditions == len(common_state))):
                    preconditions_of_remove.extend(or_node.preconditions)

            # ---------------------
            # Add the location's depends-on atom:
            if (preconditions_of_remove):
                for action_node in actions:
                    create_grounded_state.create_depends_on_grounded_precondition(action_node, location_definition, resulting_value, preconditions_of_remove.copy())  # change the line below to this line!


# ================--------------------------------------------------------------
# Create image_objects' depends-on atoms
def create_object_dependency_atoms(action_nodes, image_object_definitions, location_definitions):
    if ((len(image_object_definitions) <=1) or (not domain_definition.do_predicates_include_depends_on())): # optimisation
        return
    for image_object_definition in image_object_definitions:
        actions_that_mod_image_object = get_actions_that_modify_image_object(image_object_definition, action_nodes)
        for action in actions_that_mod_image_object:
            defined_object_dependencies = [] #image_object_definition
            for modified_location_definition in location_definitions:
                inserted_dep = False
                if action.modifies_object(modified_location_definition):
                    # for each object the location depends on, add what image_object is at that location (or the image_object itself) to the list of objects the image_object_definition depends on
                    for location_definition_dep_list in modified_location_definition.depends_on:
                        for object_definition in location_definition_dep_list:
                            dependency = object_definition.get_defined_image_obj_and_its_atom_from_state(action.pre_grounded_state)
                            if ((dependency != None) and (dependency not in defined_object_dependencies)): #TODO should the "(dependency not in defined_object_dependencies)" part be included?
                                inserted_dep = True
                                defined_object_dependencies.append(dependency)
                    if ((not inserted_dep) and (modified_location_definition not in defined_object_dependencies)):
                        defined_object_dependencies.append(modified_location_definition)
            # create the depends-on atom:
            create_grounded_state.create_depends_on_atom_and_add_to_preconditions_diff_permutations(image_object_definition, defined_object_dependencies,action)  # create_depends_on_atom_and_add_to_preconditions(defined_object_dependencies, action)

#----------------------------------------

def get_actions_that_modify_image_object(image_object_definition, action_nodes):
    resulting_actions = []
    for action_node in action_nodes:
        effect = action_node.get_effect_for_object_definition(image_object_definition)
        if (effect != None):
            resulting_actions.append(action_node)
    return resulting_actions


# ================--------------------------------------------------------------
#  Remove the atoms that none of the changed objects depend on
def remove_possible_preconditions_without_dependencies(action_nodes):
    for action_node in action_nodes:
        possible_preconditions_original = action_node.preconditions_possible.copy()
        for precondition in possible_preconditions_original:
            is_dependency = False
            for dep_precondition in action_node.preconditions_depends_on:
                for object_definition in precondition.defined_objects:
                    if object_definition in dep_precondition.defined_objects:
                        is_dependency = True
                        break
                if (is_dependency):
                    break
            if (not is_dependency):
                action_node.remove_possible_precondition(precondition) #preconditions_possible.remove(precondition)

#==============================================================================
#==============================================================================

# Debug methods, followed by unused methods:

#=================================================================
###################################################################

def debug_print_action_states(action_nodes):
    if (not DEBUG_CREATE_ACTION_GRAPH):
        return
    index = 0
    for action_node in action_nodes:
        if index > 10:
            break
        print("-----------------------------------------")
        print("action_node " + str(index))
        print ("pre state:")
        print (action_node.pre_grounded_state)
        print ("suc state:")
        print (action_node.suc_grounded_state)
        index = index +1

#--------

def debug_print_grounded_actions(action_nodes, initial=False):
    if (not DEBUG_CREATE_ACTION_GRAPH):
        return
    if (initial):
        print("initial preconditions:")
    index = 0
    for action_node in action_nodes:
        if index > 10:
            break
        print("-----------------------------------------")
        print("action_node " + str(index))
        print (action_node)
        index = index +1

#--------

def debug_show_object_id(action_nodes, location_definitions):
    if (not DEBUG_CREATE_ACTION_GRAPH):
        return
    action_node = action_nodes[0]
    #for action_node in action_nodes:
    image = action_node.transition.pre_image.copy()
    for location_definition in location_definitions:
        cv2.rectangle(image, (location_definition.image_area.min_x, location_definition.image_area.min_y), (location_definition.image_area.max_x, location_definition.image_area.max_y),
                      150, 1) #
        #cv2.putText(image, str(location_definition.id), (location_definition.image_area.min_x, location_definition.image_area.max_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
    location_defs = location_definitions.copy()
    location_defs.sort(key=lambda x: x.image_area.min_x)
    print ("location_definition IDs:")
    for location_definition in location_defs:
        print (str(location_definition.id) + " = " + str(location_definition.image_area))

    cv2.imshow('image locations', np.uint8(image))

#========================================================






#==============================================================================
#==============================================================================



""" def remove_preconditions_that_are_preconditions_of_preconditions(action_nodes, location_definitions):
    for action_node in action_nodes:
        never_rm = []
        for possible_preconditions_linked_to_known_precondition in action_node.possible_preconditions_linked_to_known_precondition: #(common_preconditions, location_definition, location_state)
            states_to_be_modified = possible_preconditions_linked_to_known_precondition[0] # group together the states relating to the same known precondition
            location_definition = possible_preconditions_linked_to_known_precondition[1]
            location_definitions_state = possible_preconditions_linked_to_known_precondition[2]

            # -------------------------------
            # OPTIMISATION: once a location has been processed it doesn't need to be reprocessed:
            if (location_definitions_state in location_definition.depends_on_preconditions):
                preconditions_of_remove = location_definition.depends_on_preconditions[location_definitions_state].copy()
                if (len(preconditions_of_remove) == 0): # should never been reached
                    exit("FAILED: preconditions_of_remove is empty")
                # add the location's depends-on atom:
                create_grounded_state.create_depends_on_grounded_precondition(action_node, location_definition,location_definitions_state ,preconditions_of_remove.copy())  # change the line below to this line!
                never_rm.extend(preconditions_of_remove)
                # Tell the action which atoms should be removed:
                for atom in states_to_be_modified:
                    if ((atom not in never_rm) and ( not atom.is_static)):  # and (atom not in preconditions_of_remove) and (atom in action_node.get_possible_preconditions_without_to_remove())):
                        action_node.add_precondition_to_be_removed(atom)
                continue
            # -------------------------------

            #-------------------------------
            # We want to remove as many preconditions as possible, so keep track of the equally largest ones;
            #   and we must keep the preconditions that are the removed preconditions belong too.
            never_rm_for_this_link = []
            rm_for_this_link = []
            inserted_to_be_removed = True
            while (inserted_to_be_removed): # while we can remove atoms, keep removing atoms:
                equal_states_that_could_be_removed = []
                preconditions_of_remove = []
                for or_node in action_node.get_or_nodes():
                    #if (or_node.is_known_precondition):#    continue <-- double check this is not needed

                    #------------------------
                    # initialise common_state:
                    common_state = [] #action_node.preconditions_possible.copy()
                    for atom in states_to_be_modified:
                        if ((atom in action_node.preconditions_possible) and (not atom.is_static) and (not atom in rm_for_this_link) and (atom not in never_rm_for_this_link)): # .get_possible_preconditions_without_to_remove()
                            common_state.append(atom)
                    if (or_node.preconditions[0] not in common_state): # if this or-node belongs to other location:
                        continue
                    for precondition in or_node.preconditions: # shouldn't remove itself from the action's precondtions
                        common_state.remove(precondition)

                    #------------------------
                    # get state common to the or_nodes resulting state :
                    or_action_nodes = or_node.get_action_nodes()
                    for or_action_node in or_action_nodes:
                        common_state = grounded_state.get_common_atoms(common_state, or_action_node.suc_grounded_state.fluent_atoms)

                    #-----------------------
                    # we want to remove as many preconditions as possible, so keep track of the equally largest ones:
                    if ((common_state) and ( (not equal_states_that_could_be_removed) or (len(equal_states_that_could_be_removed[0]) < len(common_state))) ):
                        equal_states_that_could_be_removed.clear()
                        preconditions_of_remove = or_node.preconditions.copy()
                        equal_states_that_could_be_removed.append(common_state)
                    elif (equal_states_that_could_be_removed and (len(equal_states_that_could_be_removed[0]) == len(common_state))):
                        equal_states_that_could_be_removed.append(common_state)
                        preconditions_of_remove.extend(or_node.preconditions)

                # ---------------------
                # Add the location's depends-on atom:
                if (preconditions_of_remove):
                    create_grounded_state.create_depends_on_grounded_precondition(action_node, location_definition, location_definitions_state, preconditions_of_remove.copy())  # change the line below to this line!

                #--------------------------
                # Tell the action which atoms should be removed:
                inserted_to_be_removed = False
                for states_that_could_be_removed1 in equal_states_that_could_be_removed:
                    for atom in states_that_could_be_removed1:
                        if (atom not in never_rm and atom not in preconditions_of_remove  and (not atom.is_static)):
                            action_node.add_precondition_to_be_removed(atom)
                            rm_for_this_link.append(atom)
                            inserted_to_be_removed = True
                never_rm.extend(preconditions_of_remove)
                never_rm_for_this_link.extend(preconditions_of_remove)

    #for action_node in action_nodes:
    #    action_node.remove_preconditions_and_or_nodes_in_to_be_removed_list()
"""







## Scratched methods:
###################################################################


""" old version of modify OR: create_object_dependency_atoms()
processed_deps_of = [] # there are multiple permutations of the "depends_on" precondition we only want the first perm
for precondition in preconditions:
    if (("depends_on" in precondition.predicate.name ) ): #and (precondition.negated)
        if ((not isinstance(precondition.defined_objects[0], LocationDefinition)) or (precondition.defined_objects[0] in processed_deps_of)):
            continue
        processed_deps_of.append(precondition.defined_objects[0])
        inserted_dep = False
        for i in range(1, len(precondition.defined_objects)): # i.e., skip the first one
            location_definition = precondition.defined_objects[i]
            object_state_atoms = action.get_objects_fluent_state_from_pre_grounded_state(location_definition)
            for object_state_atom in object_state_atoms:
                if (((object_state_atom.predicate.name == "at")) and (not object_state_atom.negated)):
                    inserted_dep = True
                    defined_object_dependencies.append(object_state_atom.defined_objects[0]) #= [image_object_definition, object_state_atom.defined_objects[0]]
                    action.append_to_possible_preconditions(object_state_atom)
                    break
                elif ((object_state_atom.predicate.name == "clear") and (not object_state_atom.negated)):
                    action.append_to_possible_preconditions(object_state_atom)
                    break
        if ((not inserted_dep) and (precondition.defined_objects[0] not in defined_object_dependencies)):
            defined_object_dependencies.append(precondition.defined_objects[0])
create_grounded_state.create_depends_on_atom_and_add_to_preconditions_diff_permutations(image_object_definition, defined_object_dependencies, action)#create_depends_on_atom_and_add_to_preconditions(defined_object_dependencies, action)
defined_object_dependencies.clear()
"""


#==============================================================================
#: this isn't working:
"""
def remove_preconditions_that_are_preconditions_of_preconditions_rm_me(action_nodes):
    for action_node in action_nodes:
        for precondition in action_node.preconditions_possible:
            for or_node in action_node.get_or_nodes():
                if (or_node.is_known_precondition):
                    if (do_all_or_nodes_children_have_precondition(or_node, precondition)):
                        action_node.add_precondition_to_be_removed(precondition)
                    # TODO recursive <-- prob not.. yes, the first one doesn't need to but the others will.
                else:
                    continue

def do_all_or_nodes_children_have_precondition(or_node, precondition):
    action_nodes = or_node.get_action_nodes()
    for action_node in action_nodes:
        #if precondition not in action_node.preconditions_known:
            # todo not (is precondition an effect of an action that sets one of the  action_node.preconditions_known)
        if not is_precondition_an_effect_of_a_known_dependecy(precondition, action_node):
            print ("precondition not in action_node.preconditions_possible")
            return False
    return True



def is_precondition_an_effect_of_a_known_dependecy(precondition, action_node):
    or_nodes = action_node.get_or_nodes()
    for or_node in or_nodes:
       if (or_node.is_known_precondition):
            action_nodes = or_node.get_action_nodes()
            for action in action_nodes:
                if precondition not in action.effects:
                    return False
            return True

"""

#=================================================================
"""
def show_object_locations_for_debugging(action_nodes):
    index = 0
    for action_node in action_nodes:
        if index > 10:
            break
       # if index % 5 != 0:
       #     continue
        #image = action_node.image_pre #.copy()
        print ("action_node.unchanged_objects= " + str(len(action_node.unchanged_objects)))
        image = action_node.image_pre.copy()
        for object in action_node.unchanged_objects:
            print ("action_node.unchanged_objects: x=" + str(object.min_x) + ", y=" + str(object.min_y) + " width=" + str(object.imageObject.image.shape[1]) + " height=" + str(object.imageObject.image.shape[0]) )
            cv2.rectangle(image, (object.min_x, object.min_y), (object.min_x + object.imageObject.image.shape[1] , object.min_y + object.imageObject.image.shape[0]), (255, 0, 0), 1)
        for object in action_node.image_objects_pre:
            print ("action_node.unchanged_objects: x=" + str(object.min_x) + ", y=" + str(object.min_y) + " width=" + str(object.imageObject.image.shape[1]) + " height=" + str(object.imageObject.image.shape[0]) )
            cv2.rectangle(image, (object.min_x, object.min_y), (object.min_x + object.imageObject.image.shape[1] , object.min_y + object.imageObject.image.shape[0]), (0, 255, 0), 1)
        cv2.imshow('image' + str(index), np.uint8(image))
        index = index +1


#------------------------------------------------

######################################################
##       BUILD THE ACTION GRAPH

def build_action_graph(action_nodes):
    operator_nodes = []
    for action_node in action_nodes:
        dependencies = discover_dependencies(action_node, action_nodes)
        if dependencies:
            operator_nodes.extend(connect_action_to_dependencies(action_node, dependencies))
    return operator_nodes
"""
#--------------------------------------------------

#def discover_dependencies(action_node, action_nodes): #_and_check_if_objects_are_locations
    #has_not_object = "no"
    #dependencies = []
    #for possible_dependency in action_nodes:
    #    if (action_node == possible_dependency):
     #       continue
        # check for dependencies:
     #   if util.are_images_equal(action_node.image_pre, possible_dependency.image_suc):
    #        print("add dependencies")
     #       dependencies.append(possible_dependency)
""" This doesn't work well enough, i.e., if there are not two actions made on an object from the same state then this fails.
    # check_if_objects_are_locations:
    elif util.are_images_equal(action_node.image_pre, possible_dependency.image_pre) and action_node.action_type == ActionNode_Type.SWAP:
        matching_object_start_loc = None
        non_matching_object_start_loc = None
        print("search...")
        for object_of_action_node in action_node.image_objects_pre:
            if ((not object_of_action_node.imageObject.is_object) or (matching_object_start_loc != None and non_matching_object_start_loc != None) ):
                has_not_object = "yes"
                break
            for object_of_possible_dependecy in possible_dependency.image_objects_pre:
                if object_of_action_node.is_same_object(object_of_possible_dependecy):
                    if object_of_action_node.has_same_location(object_of_possible_dependecy):
                        matching_object_start_loc = object_of_action_node
                        print("has matching_object_start_loc")
                    else:
                        non_matching_object_start_loc = object_of_action_node
                        print("has non_matching_object_start_loc")
        if (matching_object_start_loc != None and non_matching_object_start_loc != None):
            non_matching_object_start_loc.imageObject.is_object = False  # i.e., object is a location
            has_not_object = "yes"
print (has_not_object)
if (has_not_object == "no"):
    cv2.imshow('acton_node' , np.uint8(action_node.image_pre))
    cv2.imshow('acton_node-suc' , np.uint8(action_node.image_suc))
    index = 0
    for possible_dependency in action_nodes:
        if util.are_images_equal(action_node.image_pre, possible_dependency.image_pre) and action_node.action_type == ActionNode_Type.SWAP:
            cv2.imshow('possible_dependency-suc' + str(index), np.uint8(possible_dependency.image_suc))
            index = index + 1

    while cv2.getWindowProperty('non_matching_object_start_loc', 0) >= 0:
        keyCode = cv2.waitKey(50)
"""
    #return dependencies

#------------------------------------------------
"""
def connect_action_to_dependencies(action_node, dependencies):
    # Create OR node:
    dependencies_nodes = []
    for dependency in dependencies:
        if dependency.has_dependencies():
            dependencies_nodes.append(dependency.parents[0])
        else:
            dependencies_nodes.append(dependency)
    or_node = OrNode(dependencies_nodes)

    # Create DEP node (and if needed move action_node's parents to be the DEP node's parents):
    parents = action_node.parents.copy()
    print(len(parents))
    dep_node = OAndNode([or_node, action_node])
    print(len(parents))
    for parent in parents:
        parent.replace_child(action_node, dep_node)
    return [or_node, dep_node]

#------------------------------------------------

###############################################################
##  DISCOVER IF OBJECTS ARE LOCATIONS OR OBJECTS(items)

#  if an action's object no-longer exists after one of its possible preceding actions (and its not in the preceding's changed objects) that  object is a location
def set_object_types(action_nodes, all_objects): # i.e., are the objects objects or locations
    for action_node in action_nodes:
        preceding_actions = action_node.get_preceding_actions()
        if (set_object_types_recursive(action_node, preceding_actions, visited=[action_node])):
            all_objects_have_types = True
            for object in all_objects:
                if (object.type == ImageObject_Type.UNKNOWN):
                    all_objects_have_types = False
            if all_objects_have_types:
                break
    for object in all_objects:
        print (object.type)
        if (object.type == ImageObject_Type.UNKNOWN):
            object.type = ImageObject_Type.OBJECT
"""
#------------------------------------

#def set_object_types_recursive(action_node, preceding_actions, visited=[]):
#    print("do_preceding_actions_make_objects_locations" + str(len(visited)))
#    do_preceding_actions_make_objects_locations(action_node, preceding_actions)
 #   if (action_node.do_all_objects_have_types()):
 #       return True
""" # maybe for now we should assume that if none of the directly proceding actions set the object as a location then it is an object (as we are looping over al lactions should still be ok to miss transactions)
else: # TODO test this!!! # the preceding preceding (etc.) actions should also be checked... but only if the preceding action doesn't changed the object's state
    preceding_preceding_actions = []
    for preceding_action in preceding_actions:
        visited.append(preceding_action)
        if preceding_action.manipulates_at_least_one_identical_object(action_node):
            continue # TODO it would be better to check each object independently
        preceding_actions_of_pre = preceding_action.get_preceding_actions()
        for preceding_action_of_pre in preceding_actions_of_pre:
            if (not (preceding_action_of_pre in visited) and not preceding_action_of_pre.manipulates_at_least_one_identical_object(preceding_action)): # TODO this should all actions in path
                preceding_preceding_actions.append(preceding_action_of_pre)

    if preceding_preceding_actions:
        print ("RECURSE preceding_preceding_actions")
        set_object_types_recursive(action_node, preceding_preceding_actions, visited)
    else:
        action_node.set_all_untyped_objects_to_object()
"""
#------------------------------------
"""
def do_preceding_actions_make_objects_locations(action_node, preceding_actions): # TODO: the "swap" tile of the puzzle might be labelled as a location. <-- this is prob ok, as the tiles being swapped are always position relative

    made_location = False
    for preceding_action in preceding_actions:
        if (action_node.do_all_objects_have_types()):
            return True
        #made_object = False
        # if preceding_action has same objects but for one of those objects the start location is different from the end location that object is a location
        # TODO if both have different start locations then both are objects (e.g., two robots) <--might be handled in the below iteration but needs to be checked.
        if (action_node.manipulates_same_objects(preceding_action)):
            #print("manipulates_same_objects... checking for_one_object_is_this_actions_end_location_different_to_preceding_actions_start_location")
            changed_object = action_node.for_one_object_is_this_actions_end_location_different_to_preceding_actions_start_location(preceding_action)
            if (changed_object != None):
                print("manipulates_same_objects")
                changed_object.imageObject.type = ImageObject_Type.LOCATION
                #made_location = True
                if (action_node.action_type == ActionNode_Type.SWAP): # and ( made_location or made_object)):  # if action is a swap action we know that the other object must be an object - optimisation
                    for action_image_objects_known in action_node.image_objects_suc:
                        if action_image_objects_known.imageObject.type != ImageObject_Type.LOCATION:
                            action_image_objects_known.imageObject.type = ImageObject_Type.OBJECT
                            return True
        else: #     does this action override an object from a preceding action's effects - if so the the object overridden is a location, and the object doing the overridding is an object
            # if action_node overrides one preceding_action's objects both objects are locations
            made_location_for_preceding_action = False
            for action_image_object in preceding_action.image_objects_suc:
                overridding_object = action_node.does_action_override_object(action_image_object)
                if (overridding_object != None):#action_node.does_action_override_object(action_image_objects) ):
                    print("does_action_override_object")
                    action_image_object.imageObject.type = ImageObject_Type.LOCATION
                    overridding_object.imageObject.type = ImageObject_Type.OBJECT
                    made_location_for_preceding_action = True
                    made_location = True
                    break

            # optimisation:
            if (preceding_action.action_type == ActionNode_Type.SWAP and (made_location_for_preceding_action )):  # if action is a swap action we know that the other object must be an object - optimisation
                for action_image_objects_known in preceding_action.image_objects_suc:
                    if action_image_objects_known.imageObject.type != ImageObject_Type.LOCATION:
                        action_image_objects_known.imageObject.type = ImageObject_Type.OBJECT
                        break
        # in ToH domain if one object is a location the other is an object (this would also be true for other domains - in other domains both might be objects and both might be locations but hopefully this is handled):
    if (action_node.action_type == ActionNode_Type.SWAP and made_location):  # if action is a swap action we know that the other object must be an object - optimisation
        for action_image_objects_known in action_node.image_objects_suc:
            if action_image_objects_known.imageObject.type != ImageObject_Type.OBJECT:
                action_image_objects_known.imageObject.type = ImageObject_Type.LOCATION
                break
        return True
    return False

#-----------------------------------------------------------

##########################################################
###   set_all_objects_locations_for_all_actions

def set_all_objects_locations_for_all_actions(action_nodes, all_objects):
    # for all actions: for all objects aren't locations: discover the objects location (by find the prior time that object changed location); if we come across an action that adds rather than swaps then the object won't be present
    #   if object not changed by prior then also same for current image
    index = 0
    for action_node in action_nodes:
        if action_node.has_dependencies():
            print ("processing action..." + str(index))
            set_all_objects_locations_for_actions_breadth_first(action_node, all_objects)
            index = index + 1
        print (action_node.has_all_objects(all_objects))
        if not action_node.has_all_objects(all_objects):
            exit(0)
    print("finished processing all actions")
#-----------------------------------------

def set_all_objects_locations_for_actions_breadth_first(action_node, all_objects): # if an object hasn't changed state/location it is still in the same location, and thus can be added to the list of objects
    bfs_queue = queue.Queue()
    changed_objects =  [] #action_node.image_objects_pre.copy()
             # previous actions (i.e., the OR node's children     # , and changed objects
    bfs_queue.put((action_node.parents[0].children[0], changed_objects))
    visited = [action_node.parents[0].children[0], action_node.parents[0], action_node]
    while (not bfs_queue.empty() and not action_node.has_all_objects(all_objects)):
        print (bfs_queue.qsize())
        current_node, changed_objects = bfs_queue.get()
        print (len( current_node.children))

        if (isinstance(current_node, OrNode)):
            for object in current_node.parents[0].children[1].image_objects_pre:
                if object not in changed_objects:
                    changed_objects.append(object)
            # changed_objects.extend(child.parents[0].children[1].image_objects_pre.copy())
            print("extended changed_object" + str(len(changed_objects)))

        for child in current_node.children:
            if child in visited:
                continue
            visited.append(child)

            if (isinstance(child, ActionNode) and child.action_type == ActionNode_Type.SWAP):
                print("is action node " + str(child.has_dependencies()))
                add_objects_from_indirect_dep_to_action_node(child, action_node, changed_objects)
            elif (not isinstance(child, ActionNode) ): #and (not (isinstance(child, OAndNode) and child.children[1].unchanged_objects))):# i.e., if the node is DEP and its right child's objects have already been identified then don't add child to queue
                print ("add child ")
                bfs_queue.put((child, changed_objects))

#---------------------------------------------------

def add_objects_from_indirect_dep_to_action_node (dependecy, action_node, changed_objects):
    add_objects_in_list_to_action_node(dependecy.image_objects_suc, action_node, changed_objects)
    add_objects_in_list_to_action_node(dependecy.unchanged_objects, action_node, changed_objects)

#---------------------------------------------------

def add_objects_in_list_to_action_node (objects, action_node, changed_objects):

    for object in objects:
        if object in action_node.unchanged_objects or object.imageObject.type != ImageObject_Type.OBJECT:
            continue
        print (object.imageObject.type)
        add_object = True
        for changed_object in changed_objects:
            if object.is_same_object(changed_object):
                add_object = False
                break
        #for action_node_object in action_node.image_objects_pre: # only objects that change value should be in image_objects_pre; therefore action_node_object will also not be in image_objects_suc
        #    if object.is_same_object(action_node_object):
        #        add_object = False
         #       break
        if add_object:
            print ("ADD OBJECT")
            action_node.unchanged_objects.append(object)

#---------------------------------------------------
"""
# action preconditions: each time a swap action happens on the two objects, is their distance the same (relative to their width/height)
                # unless it has been discovered that one of the objects is actually a position (see object_conditions) - in which case the first object is swapped to this location... but the position could be relative to an object

#============================================================================================================================================
#============================================================================================================================================
