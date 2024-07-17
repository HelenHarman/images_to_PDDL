# file contains: Domain, PredicateDefinition, ActionDefinition and DefinedAtom (i.e., none-grounded atom, which is pre/eff of an action definition)
from definitions.grounded_state import Atom


#================================================
# helper method(s)

def do_predicates_include_depends_on():
    for predicate in defined_predicates:
        if ("depends_on" in predicate.name): #and (len(predicate.param_types) == len(defined_object_dependencies)
            return True
    return False

#================================================

class Domain:
    def __init__(self, defined_predicates, defined_actions, location_definitions, image_object_definition):
        self.defined_predicates = defined_predicates.copy()
        self.defined_actions = defined_actions

        self.defined_object_types = []
        for object in location_definitions:
            if object.get_type() not in self.defined_object_types:
                self.defined_object_types.append(object.get_type())
        for object in image_object_definition:
            if object.get_type() not in self.defined_object_types:
                self.defined_object_types.append(object.get_type())

    #--------------------

    def __str__(self):
        domain_string = "(define (domain generated_domain) \n (:requirements :strips :typing )\n"

        domain_string = domain_string + "(:types "
        for type in self.defined_object_types:
            domain_string = domain_string + type + " " # end of types
        domain_string = domain_string + ")\n" # end of types

        domain_string = domain_string + "(:predicates "
        for defined_predicates in self.defined_predicates:
            domain_string = domain_string + str(defined_predicates) + "\n"
        domain_string = domain_string + ")\n" # end of predicates

        for action in self.defined_actions:
            domain_string = domain_string + str(action) + "\n"

        domain_string = domain_string + ")" # end of domain
        #print(domain_string)
        return domain_string

#================================================

defined_predicates = []
class PredicateDefinition:
    def __init__(self, name, param_types):
        global defined_predicates
        self.name = name
        self.param_types = param_types
        if self not in defined_predicates:
            defined_predicates.append(self)


    def __eq__(self, other):
        return (isinstance(other, PredicateDefinition) and self.name == other.name and self.param_types == other.param_types)

    def __str__(self):
        return_str = "(" + self.name
        for i in range(len(self.param_types)):
            return_str = return_str + " ?" + str(i) + " - " + self.param_types[i]
        return return_str + ")"

#================================================================

action_definition_id = 0
class ActionDefinition:
    def __init__(self):
        global action_definition_id
        self.id = action_definition_id
        action_definition_id = action_definition_id + 1
        self.param_types = []
        self.preconditions = []
        self.effects = []

        self.action_nodes = []

        #self.further_preconditions = [] # i.e., to prevent an action from being executed by an action that takes few preconditions - this also might be possible be editing the "link" precondition
        #self.changed_together_links = [] # TODO

        self.params_to_preconditions = {}
        self.params_to_effects = {}
        #if self not in defined_predicates:
        #    defined_predicates.append(self)

    #---------------------------------------------------

    def is_grounding_of_action(self, action_node):
        defined_objects_to_pre_and_eff = action_node.get_parameters_with_their_preconditions_and_effects()
        action_node_param_types = []
        objects_to_preconditions = {}
        objects_to_effects = {}
        if (len(defined_objects_to_pre_and_eff) != len(self.param_types)):
            return False
        for defined_object in defined_objects_to_pre_and_eff:
            action_node_param_types.append(defined_object.get_type())
            if (defined_objects_to_pre_and_eff[defined_object][0]):
                objects_to_preconditions[defined_object] = defined_objects_to_pre_and_eff[defined_object][0].copy()
            if (defined_objects_to_pre_and_eff[defined_object][1]):
                objects_to_effects[defined_object] = defined_objects_to_pre_and_eff[defined_object][1].copy()

        #--------------------------
        # Check that the parameters can match:
        for param_type in self.param_types:
            if param_type in action_node_param_types:
                action_node_param_types.remove(param_type) # only removes first instance
            else:
                return False
        #--------------------------
        #  check that the preconditions can match <-- can be done in same way as above? - i.e., same number of clear/not-clear locations then it is ok
        if (not self.does_objects_to_atoms_match_param_to_atoms(self.params_to_preconditions, objects_to_preconditions)):
            return False
        #--------------------------
        #  check that the effects can match <-- if preconditions match then this will also prob match (so prob not needed)
        if self.does_objects_to_atoms_match_param_to_atoms(self.params_to_effects, objects_to_effects):
            self.action_nodes.append(action_node)
            return True
        return False
        #--------------------------

    #-------------------------------------------------

    def does_objects_to_atoms_match_param_to_atoms(self, params_to_atoms, objects_to_atoms):
        # Performed by iterating over params_to_atoms to remove matches from objects_to_atoms, and then checking objects_to_atoms is empty.
        matches = {}  # param to objects_to_atoms
        for param_to_atoms in params_to_atoms:
            found = False
            matches[param_to_atoms] = []
            for object_to_atoms in objects_to_atoms:
                if (self.does_defined_atoms_match_grounded_atoms(params_to_atoms[param_to_atoms], objects_to_atoms[object_to_atoms], param_to_atoms, object_to_atoms)):
                    objects_to_atoms.pop(object_to_atoms)  # remove param_to_preconditions from objects_to_preconditions
                    found = True
                    break
            if (not found):
                return False

        if objects_to_atoms:  # not empty:
            return False
        return True

    # -------------------------------------------

    def does_defined_atoms_match_grounded_atoms(self, defined_preconditions, grounded_preconditions, defined_pre_param, grounded_pre_param):
        if (len(defined_preconditions) != len(grounded_preconditions)):
            return False
        for grounded_precondition in grounded_preconditions:
            if grounded_precondition not in defined_preconditions:
                return False
        #-------------------------------------------------------
        # to fix 2 blocks in ToH issues with an action definition going missing:
        dep_defined_preconditions = []
        dep_grounded_preconditions = []
        for grounded_precondition in grounded_preconditions:
            if ("depends_on_" in grounded_precondition.predicate.name and (grounded_precondition.defined_objects[0] == grounded_pre_param)):
                dep_grounded_preconditions.append(grounded_precondition)
        for defined_precondition in defined_preconditions:
            if ("depends_on_" in defined_precondition.predicate.name and (defined_precondition.defined_objects[0] == defined_pre_param)):
                dep_defined_preconditions.append(grounded_precondition)

        if (len(dep_defined_preconditions) != len(dep_grounded_preconditions)):
            return False
        # -------------------------------------------------------
        return True

    #========================================
    # setters(/add methods) and getters

    def add_precondition(self, defined_atom, i):
        if i in self.params_to_preconditions:
            self.params_to_preconditions[i].append(defined_atom)
        else:
            self.params_to_preconditions[i] = [defined_atom]
        if (defined_atom not in self.preconditions):
            self.preconditions.append(defined_atom)

    #---------------------------------------------------

    def add_effect(self, defined_atom, i):
        if i in self.params_to_effects:
            self.params_to_effects[i].append(defined_atom)
        else:
            self.params_to_effects[i] = [defined_atom]
        if (defined_atom not in self.effects):
            self.effects.append(defined_atom)

    #--------------------------------------------------

    def get_string_id(self):
        return "action_" + str(self.id)

    #--------------------------------------------------

    def __str__(self):
        return_str = "(:action " + self.get_string_id() + "\n"
        return_str = return_str + " :parameters ("
        for i in range(len(self.param_types)):
            return_str = return_str + " ?" + str(i) + " - " + self.param_types[i]
        return_str = return_str + ") \n"
        return_str = return_str + " :precondition (and "
        for pre in self.preconditions:
            return_str = return_str + str(pre) + "\n "
        return_str = return_str + ") \n" # end of precondition
        return_str = return_str + " :effect (and "
        for eff in self.effects:
            return_str = return_str + str(eff) + "\n "
        return_str = return_str + ") \n" # end of effects

        return_str = return_str + ") \n" # end of action
        return return_str


#===============================================================================


class DefinedAtom(Atom):
    def __init__(self, predicate, defined_objects, negated = False, is_static = False):
        Atom.__init__(self, predicate, defined_objects, negated, is_static)

    #-----------------

    def __eq__(self, other):
        if (isinstance(other, DefinedAtom)):
            return ((self.negated == other.negated) and (self.predicate == other.predicate) and (self.defined_objects == other.defined_objects))
        return (isinstance(other, Atom) and (self.negated == other.negated) and (self.predicate == other.predicate) and (len(self.defined_objects) == len(other.defined_objects)))

    #-----------------

    def __str__(self):
        return_str = "("
        if self.negated:
            return_str = return_str + " not ("
        return_str = return_str + self.predicate.name
        for defined_object in self.defined_objects:
            return_str = return_str + " ?" + str(defined_object)

        return_str = return_str + ")"
        if self.negated:
            return_str = return_str + ")"
        return return_str

# ===============================================================================
#===============================================================================