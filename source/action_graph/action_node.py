from action_graph.operator_node import Node, OAndNode, DepNode


class ActionNode(Node): # i.e., the grounded action
    def __init__(self, transition, pre_grounded_state, suc_grounded_state, preconditions_known, preconditions_possible, effects): #
        Node.__init__(self)
        self.transition = transition
        self.pre_grounded_state = pre_grounded_state # are these this needed?
        self.suc_grounded_state = suc_grounded_state

        self.preconditions_known = preconditions_known
        self.preconditions_possible = preconditions_possible
        self.effects = effects

        self.preconditions_missing_dep = []

        self.preconditions_depends_on = []

    #---------------------------------------

    def add_depends_on_preconditions(self, precondition):
        if precondition not in self.preconditions_depends_on:
            self.preconditions_depends_on.append(precondition)


    #---------------------------------------

    def modifies_object(self, object_definition):
        for effect in self.effects:
            if ((object_definition in effect.defined_objects)):  # and (effect.predicate in object_definition.get_defined_predicates())):
                return True
        return False
    #-------------------------

    def get_effect_for_object_definition(self, object_definition): # as location only has one positive effect --> i.e, is clear or an object is at that location
        for effect in self.effects:
            if ((object_definition in effect.defined_objects) and (not effect.negated)): #and (effect.predicate in object_definition.get_defined_predicates())):
                return effect
        return None

    #-------------------------

    def remove_possible_precondition(self, precondition):
        if (precondition in self.preconditions_possible):
            if (self.has_dependencies()):
                self.remove_or_node_for_precondition(precondition)
            else:
                self.preconditions_possible.remove(precondition)

    #-------------------------

    def remove_or_node_for_precondition(self, precondition):
        or_nodes = self.parents[0].children[0].children.copy()
        for or_node in or_nodes:
            if (precondition in or_node.preconditions):
                for or_node_precondition in or_node.preconditions:
                    if (or_node_precondition in self.preconditions_possible):
                        self.preconditions_possible.remove(or_node_precondition)
                or_node.remove_self_from_graph()

        if (precondition in self.preconditions_possible):
            self.preconditions_possible.remove(precondition)

    # ---------------------------------------

    ##############################
    # Used to create the action definitions:
    def get_parameters_with_their_preconditions_and_effects(self):
        parameters = {} # defined_object --> [precondtions that contain defined_object]
        for atom in self.preconditions_known:
            for defined_object in atom.defined_objects:
                if defined_object not in parameters:
                    parameters[defined_object] = (self.get_preconditions_for_object_definition(defined_object), self.get_all_effects_for_object_definition(defined_object))
        for atom in self.preconditions_possible:
            for defined_object in atom.defined_objects:
                if defined_object not in parameters:
                    parameters[defined_object] = (self.get_preconditions_for_object_definition(defined_object),self.get_all_effects_for_object_definition(defined_object))
        return parameters

    # ---------------------

    def get_preconditions_for_object_definition(self, object_definition):
        preconditions = []
        self.extend_atom_list_for_object_definition(object_definition, self.preconditions_known, preconditions)
        self.extend_atom_list_for_object_definition(object_definition, self.preconditions_possible, preconditions)
        self.extend_atom_list_for_object_definition(object_definition, self.preconditions_depends_on, preconditions)
        return preconditions
    #----------------------

    def extend_atom_list_for_object_definition(self, object_definition, preconditions_to_be_searched, preconditions_of_object_def):
        for precondition in preconditions_to_be_searched:
            if ((object_definition in precondition.defined_objects)):  # and (effect.predicate in object_definition.get_defined_predicates())):
                preconditions_of_object_def.append(precondition)

    #------------------------

    def get_all_effects_for_object_definition(self, object_definition):
        effects = []
        self.extend_atom_list_for_object_definition(object_definition, self.effects, effects)
        return effects

    # =============================================

    #######################################
    ##  Action Graph realated actions:

    def has_dependencies(self):
        return (len(self.parents) == 1 and isinstance(self.parents[0], DepNode))

    def get_dep_node_or_self(self):
        if (self.has_dependencies()):
            return self.parents[0]
        else:
            return self

    def get_or_nodes(self):
        if self.has_dependencies():
            return self.parents[0].children[0].children
        return []

    #---------------------------------------

    #######################################
    ## Overrides methods:
    def __eq__(self, other):
        return (isinstance(other, ActionNode) and self.preconditions_known == other.preconditions_known
                and self.preconditions_possible == other.preconditions_possible and self.effects == other.effects) #self.pre_grounded_state == other.pre_grounded_state and self.suc_grounded_state == other.suc_grounded_state)

    #---------------------------------------

    def __str__(self):
        return_str = "Grounded action: \n    preconditions:"
        for precondition in self.preconditions_known:
            return_str = return_str + "        " + str(precondition) + "\n"
        for precondition in self.preconditions_possible:
            return_str = return_str + "        " + str(precondition) + "\n"
        for precondition in self.preconditions_missing_dep:
            return_str = return_str + "        " + str(precondition) + "\n"
        return_str = return_str + "    effects:"
        for effect in self.effects:
            return_str = return_str + "        " + str(effect) + "\n"
        return return_str

    #---------------------------------------




    #==========================================
    # UNUSED:

    # unused variables:
        # self.common_preconditions = [] # any preconditions_possible not in this list should be removed
        # self.preconditions_to_be_removed = []
        # self.possible_preconditions_linked_to_known_precondition =[]
        # self.unchanged_objects = []
        # self.defined_changes = [] # contains tuples: (from_state_object, to_state_object)
        # self.linked_objects = []
        #self.defined_pre_state = None
        #self.defined_suc_state = None

        """
        self.image_pre = image_pre
        self.image_suc = image_suc
        self.image_objects_pre = image_objects_pre # the order of image_objects_pre and image_objects_suc should match
        self.image_objects_suc = image_objects_suc
        self.action_type = action_type
        """


    # UNUSED possible_preconditions METHODS
        # def add_common_preconditions(self, common_preconditions, location_definition, location_state):
        # common preconditions are the preconditions that should not be removed
        """
        for common_precondition in common_preconditions:
            if common_precondition not in self.common_preconditions:
                self.common_preconditions.append(common_precondition)
        """

    #    self.possible_preconditions_linked_to_known_precondition.append((common_preconditions, location_definition, location_state))

    """
     def get_all_preconditions(self):
         preconditions = self.preconditions_known.copy()
         preconditions.extend(self.preconditions_possible)
         return preconditions
     """
    """   
    def append_to_possible_preconditions(self, atom):
        if atom not in self.preconditions_possible:
            self.preconditions_possible.append(atom) 
    def get_objects_fluent_state_from_pre_grounded_state(self, object_definition):
        #atoms = []
        return self.pre_grounded_state.get_fluent_atoms_for_object(object_definition)
       # for effect in self.pre_grounded_state:
        #    if ((object_definition in effect.defined_objects)):  # and (effect.predicate in object_definition.get_defined_predicates())):
        #        atoms.append(effect)
        #return atoms
    def get_possible_preconditions_without_to_remove(self):
        return_possible_preconditions = []
        for precondition in self.preconditions_possible:
            if (precondition not in self.preconditions_to_be_removed):
                return_possible_preconditions.append(precondition)
        return return_possible_preconditions

    def get_or_nodes_without_to_remove(self):
        or_nodes = self.get_or_nodes()
        return_or_nodes = []
        for or_node in or_nodes:
            found = False
            for precondition in or_node.preconditions:
                if (precondition in self.preconditions_to_be_removed):
                    found = True
                    break
            if (not found):
                return_or_nodes.append(or_node)
        return return_or_nodes

    def add_precondition_to_be_removed(self, to_be_removed):
        if to_be_removed not in self.preconditions_to_be_removed:
            self.preconditions_to_be_removed.append(to_be_removed)
    def remove_preconditions_from_to_be_removed(self, never_rm_preconditions):
        for never_rm_precondition in never_rm_preconditions:
            self.remove_precondition_from_to_be_removed(never_rm_precondition)

    def remove_precondition_from_to_be_removed(self, precondition):
        if precondition in self.preconditions_to_be_removed:
            self.preconditions_to_be_removed.remove(precondition)
    def remove_preconditions_and_or_nodes_in_to_be_removed_list(self):
        original_preconditions_possible = self.preconditions_possible.copy()
        for precondition in original_preconditions_possible:
            if ((precondition in self.preconditions_possible ) and (precondition in self.preconditions_to_be_removed)):
                print ("remove original_preconditions_possible")
                if (self.has_dependencies()):
                    self.remove_or_node_for_precondition(precondition)
                else:
                    self.preconditions_possible.remove(precondition)
        self.preconditions_to_be_removed.clear()


    def add_known_precondition(self, precondition):
        if (precondition not in self.preconditions_known):
            self.preconditions_known.append(precondition)

        if (precondition in self.preconditions_possible):
            self.preconditions_possible.remove(precondition)

    def remove_preconditions_and_or_nodes_not_in_common_preconditions(self):
        original_preconditions_possible = self.preconditions_possible.copy()
        for precondition in original_preconditions_possible:
            if ((precondition in self.preconditions_possible ) and ((precondition not in self.common_preconditions) or (precondition in self.preconditions_to_be_removed))):
                print ("remove original_preconditions_possible")
                if (self.has_dependencies()):
                    self.remove_or_node_for_precondition(precondition)
                else:
                    self.preconditions_possible.remove(precondition)
        self.common_preconditions.clear()
        self.preconditions_to_be_removed.clear()
    """

    # UNUSED ACTION GRAPH METHODS:

    """ get_preceding_actions
        *=preceding_actions
                         dep
                        /  \
                       OR   self
                      /  \
                   dep     *
                 /   \      
              ...     *   
    """
    """
    def get_preceding_actions(self):
        preceding_actions = []
        if not self.has_dependencies():
            return preceding_actions
        preceding_nodes = self.parents[0].children[0].children  # i.e., the OR node's children
        for preceding_node in preceding_nodes:
            if isinstance(preceding_node, ActionNode):
                preceding_actions.append(preceding_node)
            elif isinstance(preceding_node, OAndNode): # could also be else statement
                preceding_actions.append(preceding_node.children[1])
        return preceding_actions
    """

    """ get_subsequent_actions
     *=subsequent_actions
              dep     dep
             /  \    /  \
            OR   *  OR   *
           /  \    /  \
        ...    dep     ...
              /   \      
           ...    self   
    """
    """
    def get_subsequent_actions(self):
        subsequent_actions = []
        parent_or_nodes = self.parents
        if self.has_dependencies():
            parent_or_nodes = self.parents[0].parents
        for parent in parent_or_nodes:
            parent_dep_nodes = parent.parents #<-- should be single dep node
            for parent_dep in parent_dep_nodes:
                if isinstance(parent_dep.children[1], ActionNode): # <-- should always be true
                    subsequent_actions.append(parent_dep.children[1])
        return subsequent_actions
    """
    #-----------------------------------------





#=====================================================================
#=====================================================================




""" from very first version of code:
from enum import Enum

import cv2
import numpy as np
#from definitions.defined_object import DefinedLoction, DefinedImage
#from definitions import grounded_state
from definitions.defined_state import DefinedImageState, DefinedLocationState
from image_handling import util
#from image_handling.image_area import ImageObject_Type

class ActionNode_Type(Enum):
    UNKNOWN = 0
    SWAP = 1



    def sort_preconditions(self):
        defined_image_changes = []
        for defined_change in self.defined_changes:
            if isinstance(defined_change[0], DefinedImageState):
                defined_image_changes.append(defined_change)
        defined_image_changes.sort(key=lambda x: x[0].get_location_id(), reverse=True)

        defined_location_changes = []
        for defined_change in self.defined_changes:
            if isinstance(defined_change[0], DefinedLocationState):
                defined_location_changes.append(defined_change)
        defined_location_changes.sort(key=lambda x: x[0].get_state(), reverse=True)

        defined_image_changes.extend(defined_location_changes)
        self.defined_changes = defined_image_changes

    #---------------------------------------

    def add_linked_objects(self, links):
        for link in links:
            if link not in self.linked_objects:
                self.linked_objects.append(link)

    #---------------------------------------

    def get_defined_objects_change(self, defined_object):
        for defined_change in self.defined_changes:
            if (((isinstance(defined_object, DefinedLoction) and isinstance(defined_change[0].get_definition(), DefinedLoction))
                    or (isinstance(defined_object, DefinedImage) and isinstance(defined_change[0].get_definition(), DefinedImage)))
                   and (defined_object.id == defined_change[0].get_definition().id)):
                return defined_change
        return None

    def does_action_contain_change(self, changed_from, changed_to):
        for defined_change in self.defined_changes:
            if (defined_change[0] == changed_from and defined_change[1] == changed_to):
            #if (((isinstance(changed_from.get_definition(), DefinedLoction) and isinstance(defined_change[0].get_definition(), DefinedLoction))
            #     or (isinstance(changed_from.get_definition(), DefinedImage) and isinstance(defined_change[0].get_definition(),DefinedImage)))
            #        and (changed_from.get_definition().id == defined_change[0].get_definition().id)):
                return True
        return False

    #---------------------------------------

    def order_params_locations_last(self):
        old_image_objects_pre = self.image_objects_pre.copy()
        self.image_objects_pre.clear()
        old_image_objects_suc = self.image_objects_cus.copy()
        self.image_objects_cus.clear()
        for i in range(len(old_image_objects_pre)):
            if old_image_objects_pre[i].imageObject.type != ImageObject_Type.LOCATION:
                self.image_objects_pre.insert(0, old_image_objects_pre[i])
                self.image_objects_suc.insert(0, old_image_objects_suc[i])
            else:
                self.image_objects_pre.append(old_image_objects_pre[i])
                self.image_objects_suc.append(old_image_objects_suc[i])

    #---------------------------------------

    def manipulates_same_objects(self, other):
        for changed_object in self.image_objects_pre:
            found_match = False
            for other_changed_object in other.image_objects_pre:
                if (changed_object.is_same_object(other_changed_object)):
                    found_match = True
                    break
            if not found_match:
                return False
        return True

    #---------------------------------------

    def manipulates_at_least_one_identical_object(self, other):
        for changed_object in self.image_objects_pre:
            for other_changed_object in other.image_objects_pre:
                if (changed_object.imageObject == other_changed_object.imageObject): #  changed_object.is_same_object(other_changed_object)): TODO: change back
                    return True
        return False

    #---------------------------------------

    def do_all_objects_have_types(self):
        for object in self.image_objects_pre:
            if object.imageObject.type == ImageObject_Type.UNKNOWN:
                return False

        for object in self.image_objects_suc:
            if object.imageObject.type == ImageObject_Type.UNKNOWN:
                return False
        return True

    #---------------------------------------

    def set_all_untyped_objects_to_object(self):
        for object in self.image_objects_pre:
            if object.imageObject.type == ImageObject_Type.UNKNOWN:
                object.imageObject.type = ImageObject_Type.OBJECT

        for object in self.image_objects_suc:
            if object.imageObject.type == ImageObject_Type.UNKNOWN:
                object.imageObject.type = ImageObject_Type.OBJECT

    #---------------------------------------

    def has_all_objects(self, all_objects):
        if (self.action_type == ActionNode_Type.SWAP):
            count = len(self.unchanged_objects)
            for object in self.image_objects_pre:
                if (object.imageObject.type == ImageObject_Type.OBJECT):
                    count = count + 1
            all_object_count = 0
            for object in all_objects:
                if (object.type == ImageObject_Type.OBJECT):
                    all_object_count = all_object_count + 1
            print ("count="+str(count) + ", all_object_count=" + str(all_object_count) )


            if (count > all_object_count):
                index = 0
                for object in self.image_objects_pre:
                    cv2.imshow('pre_object' + str(index), np.uint8(object.imageObject.image))
                    index = index + 1
                for object in self.unchanged_objects:
                    print ('unchanged_objects: x=' + str(object.min_x) + ", y=" +str(object.min_y))
                    cv2.imshow('unchanged_objects' + str(index), np.uint8(object.imageObject.image))
                    index = index + 1
                while cv2.getWindowProperty('pre_object0', 0) >= 0:
                    keyCode = cv2.waitKey(50)

            return count == all_object_count
        else:
            return ((len(self.unchanged_objects) + len(self.image_objects_pre))  == len(all_objects))

    #-----------------------------------------

    def does_action_override_object(self, image_object_with_pos):
        for changed_object in self.image_objects_suc:
            if (changed_object.imageObject.type == ImageObject_Type.UNKNOWN or changed_object.imageObject.type == ImageObject_Type.OBJECT):

                    if changed_object.is_same_object(image_object_with_pos):
                        continue ##return False #TODO ? for swap actions this will result in returning false. For other actions?
                    elif util.do_image_objects_with_positions_overlap(image_object_with_pos, changed_object):
                        print ("RETURN OBJECT")
                        return changed_object # TODO !!!! we don't want this object, we want its previous location!!! <-- this is the one which is the location.
            else:
                # TODO
                return None
        return None

    #---------------------------------------

    def for_one_object_is_this_actions_end_location_different_to_preceding_actions_start_location(self, preceding_action):
        if (self.action_type != ActionNode_Type.SWAP or preceding_action.action_type != ActionNode_Type.SWAP):
            return None # TODO
        for changed_object in self.image_objects_pre:
            for other_changed_object in preceding_action.image_objects_suc:
                if (changed_object.is_same_object(other_changed_object) and (not (changed_object.has_same_location(other_changed_object)) ) ):
                    return changed_object
        return None

    #---------------------------------------

"""
