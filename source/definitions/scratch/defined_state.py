
from enum import Enum




class DefinedImageState:
    def __init__(self, defined_image, location = None, is_visible = True):
        self.defined_image = defined_image
        self.is_visible = is_visible
        self.set_is_at_location(location)
        self.is_on_object = None # <-- for when we allow occlusions, and other types of actions

    def set_is_at_location(self, location):
        self.is_at_location = location
        #--self.is_visible = True
        if (location != None):
            location.has_image = self
            location.set_is_clear(False)

    def __str__(self):
        return_str = ""
        if self.is_visible:
            return_str = return_str + "(is-visible image_" + str(self.defined_image.id) + ")\n"
        else:
            return_str = return_str + "(not (is-visible image_" + str(self.defined_image.id) + "))\n"
        if self.is_at_location != None:
            return_str = return_str + "(at image_" + str(self.defined_image.id) + " location_" + str(self.is_at_location.defined_location.id) +  ")\n"
        return return_str

    def __eq__(self, other):
        return ((isinstance(other, DefinedImageState) and self.is_visible == other.is_visible and self.defined_image.id == other.defined_image.id)
            and( (self.is_at_location == None and other.is_at_location == None)
                 or (self.is_at_location != None and other.is_at_location != None and self.is_at_location.defined_location.id == other.is_at_location.defined_location.id))
            and ((self.is_on_object == None and other.is_on_object == None)
                 or ( self.is_on_object != None and other.is_on_object != None and self.is_on_object.defined_image.id == other.is_on_object.defined_image.id)))


    def get_definition(self):
        return self.defined_image

    def get_type_as_string(self):
        return "image"

    def get_predicates_for_action_def(self):
        return_str = ("at", [self.defined_image.id, self.is_at_location.defined_location.id], True) #"(at <" + str(self.defined_image.id) + "> <" + str(self.is_at_location.defined_location.id) + ">)\n"
        return [return_str]

    def get_location_id(self):
        if self.is_at_location != None:
            return self.is_at_location.defined_location.id
        else:
            return -1

class DefinedLocationState:
    def __init__(self, defined_location): # TODO fix equivalent_locations
        self.defined_location = defined_location
        self.equivalent_locations = []
        self.set_is_clear(True) # if clear is true this location is one of its images; # TODO this should be a list of states <--scratch the image of has_image has an id, which can be used as the state
        #self.has_image = None
        self.set_has_image(None) # i.e., a DefinedImageState; <-- if stacked then this is the bottom image
    """
    def __init__(self, defined_location, image, is_clear, equivalent_locations): # TODO fix equivalent_locations
        self.defined_location = defined_location
        self.equivalent_locations = equivalent_locations
        self.set_is_clear(is_clear) # if clear is true this location is one of the images; otherwise it
        self.set_has_image(image) # i.e., a DefinedImageState; <-- if stacked then this is the bottom image
    """
    def set_is_clear(self, is_clear, change_equivalent = True):
        self.is_clear = is_clear
        if (change_equivalent):
            for equivalent_location in self.equivalent_locations:
                equivalent_location.is_clear = is_clear
               # if ( not is_clear) :
                equivalent_location.has_image = self.has_image

    def is_equivalent_location(self, equivalent_location):
        for this_equivalent_location in self.equivalent_locations:
            if this_equivalent_location.defined_location.id == equivalent_location.defined_location.id:
                return True
        return False

    def set_has_image(self, image):
        self.has_image = image
        if image != None:
            self.set_is_clear(False)
            image.is_at_location = self
            image.is_visible = True
        else:
            self.set_is_clear(True)

    def __str__(self):
        return_str = ""
        if self.is_clear:
            return_str = return_str + "(is-clear location_" + str(self.defined_location.id) + ")\n"
        else:
            return_str = return_str + "(not (is-clear location_" + str(self.defined_location.id) + "))\n"

        #if self.has_image:
         #   return_str = return_str + "(has-image image_" + str(self.has_image.defined_image.id) + " location_" + str(self.defined_location.id) + "))\n"

        #for equivalent_location in self.equivalent_locations:
         #   return_str = return_str + " eq=" + str(equivalent_location.defined_location.id)
        #return_str = return_str + "\n"
        return return_str

    def get_state(self):
        if (self.is_clear):
            return -1
        else:
            return self.has_image.defined_image.id

    def __eq__(self, other):
        if (isinstance(other, DefinedLocationState) and self.defined_location.id == other.defined_location.id):
            if (other.defined_location.always_from_or_to_clear and self.defined_location.always_from_or_to_clear):
                if (other.get_state() == -1):
                    return (self.get_state() == -1)
                elif (other.get_state() != -1): # could be else statement
                    return (self.get_state() != -1)
                return False # this line should never be hit
            else:
                return ((other.get_state() == self.get_state()) and (other.get_state() == self.get_state()))
        return False
        """
        return ((isinstance(other, DefinedLocationState) and (
                 (self.get_state() == -1 and )
        
        return ((isinstance(other, DefinedLocationState) and self.is_clear == other.is_clear)
                and ((self.has_image == None and other.has_image == None)
                     or (self.has_image != None and other.has_image != None and self.has_image.defined_image.id == other.has_image.defined_image.id)))
        """

    def get_definition(self):
        return self.defined_location

    def get_type_as_string(self):
        return "location"


    def get_predicates_for_action_def(self):
        return_str = ("is-clear", [self.defined_location.id], self.is_clear)
        """
        if self.is_clear:
            return_str = ("is-clear", [self.defined_location.id], True) #return_str + "(is-clear <" + str(self.defined_location.id) + ">)\n"
        else:
            return_str = ("is-clear", [self.defined_location.id], False) #return_str + "(not (is-clear <" + str(self.defined_location.id) + ">))\n"
        """
        return [return_str]
class State:
    def __init__(self):
        self.defined_image_states = []#defined_image_states
        self.defined_location_states = []#defined_location_states


    def is_defined_object_in_state_use_ids(self, defined_object):
        for defined_image_state in self.defined_image_states:
            if defined_image_state.defined_image.id == defined_object.id:
                return True
        for defined_location_state in self.defined_location_states:
            if defined_location_state.defined_location.id == defined_object.id:
                return True
        return False

    def is_defined_object_in_state(self, defined_object):
        for defined_image_state in self.defined_image_states:
            if defined_image_state.defined_image == defined_object:
                return True
        for defined_location_state in self.defined_location_states:
            if defined_location_state.defined_location == defined_object:
                return True
        return False

    def add_defined_state(self, defined_state):
        if (isinstance(defined_state, DefinedLocationState)):
            self.defined_location_states.append(defined_state)
        else:
            self.defined_image_states.append(defined_state)


    def __str__(self):
        return_str = ""
        for defined_image_state in self.defined_image_states:
            return_str = return_str + str(defined_image_state)
        for defined_location_state in self.defined_location_states:
            return_str = return_str + str(defined_location_state)
        return return_str

    def __contains__(self, item):
        return ((isinstance(item, DefinedLocationState) and (item in self.defined_location_states))
                or (isinstance(item, DefinedImageState) and (item in self.defined_image_states)))


#---------------------------------------------------------------------------

class Link_Type(Enum):
    CHANGED_VALUE_AT_SAME_TIME = 0 # N objects whose value has changed at the same time
    VALUE_CHANGE_IS_STATE_DEPENDENT = 1 # i.e., for the first linked object to change from z to x the seciond linked object must have state q0

link_counter = 0
class Link: # i.e., a generated predicate to be used within the actoions' preconditions
    def __init__(self, link_type):
        global link_counter
        self.id = link_counter
        link_counter = link_counter + 1
        self.identical_linkings = []
        self.link_type = link_type

    def can_add_linked_objects(self, linked_objects, link_type):
        if link_type != self.link_type:
            return False

        if not self.identical_linkings: # if empty
            return True

        if (self.link_type == Link_Type.CHANGED_VALUE_AT_SAME_TIME):
            #return ((linked_objects.objects[1].object_state_from.get_state() == self.identical_linkings[0].object_state_from.objects[1].get_state())
             #   or ((linked_objects.objects[1].object_state_from.get_state() == self.identical_linkings[0].object_state_from.objects[1].get_state()) )
            return len(linked_objects.objects) == len(self.identical_linkings[0].objects)   # what states they change between should be handled by other action preconditions
        elif (self.link_type == Link_Type.VALUE_CHANGE_IS_STATE_DEPENDENT): # this type of link always has two objects
            if (isinstance(linked_objects.objects[0].object_state_from, DefinedLocationState) and isinstance(self.identical_linkings[0].objects[0].object_state_from, DefinedLocationState)):# TODO: to handle lights-out (with missing transactions) this should be ignored if it doesn't hold true for the different permitations of linked CHANGED_VALUE_AT_SAME_TIME
                return (linked_objects.objects[1].have_same_states(self.identical_linkings[0].objects[1])) #linked_objects.objects[0].have_same_states(self.identical_linkings[0].objects[0]) and
            else: # TODO objects linked?:
                return linked_objects.objects[1].object_state_from.get_state() == self.identical_linkings[0].object_state_from.objects[1].get_state()


    def add_linked_objects(self, linked_objects):
        linked_objects.id = self.id
        if linked_objects not in self.identical_linkings:# should always happen for CHANGED_VALUE_AT_SAME_TIME:
            self.identical_linkings.append(linked_objects)

    def __eq__(self, other):
        return self.id == other.id


class LinkedObjects:
    def __init__(self, action_node):
        self.objects = []
        self.action_node = action_node
        self.id = -1

    def create_changed_value_at_same_time_linked_locations_from_action(self):
        for defined_change in self.action_node.defined_changes:
            if (isinstance(defined_change[0], DefinedLocationState)):
                self.objects.append(LinkedObject(defined_change[0], defined_change[1]))


    def set_linked_objects(self, linked_object1, linked_object2):
        self.objects = [linked_object1, linked_object2]


    def have_same_locations_and_states(self, other):
        for i in range(len(self.objects)):
            if (not self.objects[i].are_same_locations_and_states(other.objects[i])):
                return False
        return True

    def __eq__(self, other):
        if len(self.objects) != len(other.objects) and self.action_node == other.action_node:
            return False
        for i in range(len(self.objects)):
            if (self.objects[i] != other.objects[i]): #not ( (isinstance(self.objects[i].object_state_from, DefinedLocationState) and isinstance(other.objects[i].object_state_from, DefinedLocationState))
                #or (isinstance(self.objects[i].object_state_from, DefinedImageState) and isinstance( other.objects[i].object_state_from, DefinedImageState)) and (self.objects[i].object_state_from.get_definition().id == other.objects[i].object_state_from.get_definition().id) ) ):
                return False
        return True



    def __contains__(self, item):
        if (isinstance(item, DefinedLoction)):
            for linked_obj in self.objects:
                if ((isinstance(linked_obj.object_state_from.get_definition(), DefinedLoction)) and (linked_obj.object_state_from.get_definition().id == item.id)):
                    return True
        return False

    def __str__(self):
        return_str = "("
        for linked_obj in self.objects:
            return_str = return_str + "from: " + str(linked_obj.object_state_from) + " "
            if linked_obj.object_state_to != None:
                return_str = return_str + "to: " + str(linked_obj.object_state_to) + " "
            return_str = return_str + "; "
        return return_str + ")"


    def get_predicates_for_action_def(self):
        if self.id != -1: # i.e., both these locations can change value at the same time.
            object_ids = []
            for object in self.objects:
                object_ids.append(object.object_state_from.get_definition().id)
            return[("link-" + str(self.id), object_ids, True)]
        else:
            return self.objects[1].object_state_from.get_predicates_for_action_def()

    def get_object_ids_and_types(self):
        ids_and_types = []
        for object in self.objects:
            ids_and_types.append((object.object_state_from.get_definition().id, object.object_state_from.get_type_as_string()))
        return ids_and_types




class LinkedObject:
    def __init__(self, object_state_from, object_state_to = None):
        self.object_state_from = object_state_from # what that state is will be defined within a different predicate specific to an action
        self.object_state_to = object_state_to

    def __eq__(self, other): # we might also need to check object_state_to in the same way?
                # FROM:
        return (( ( (isinstance(self.object_state_from, DefinedLocationState) and isinstance( other.object_state_from, DefinedLocationState))
                 or (isinstance(self.object_state_from, DefinedImageState) and isinstance(other.object_state_from, DefinedImageState)) )
            and (self.object_state_from.get_definition().id == other.object_state_from.get_definition().id)  )
                # TO:
            and (( self.object_state_to == None and other.object_state_to == None) or ((self.object_state_to == None) or (other.object_state_to == None))
                or ( ( (isinstance(self.object_state_to, DefinedLocationState) and isinstance( other.object_state_to, DefinedLocationState))
                 or (isinstance(self.object_state_to, DefinedImageState) and isinstance(other.object_state_to, DefinedImageState)) )
            and (self.object_state_to.get_definition().id == other.object_state_to.get_definition().id)))    )

    def are_same_locations_and_states(self, other):
        if ( (self != other) or (self.object_state_to == None) or (other.object_state_to == None)): # i.e., are different objects
            return False

        if (other.object_state_from.get_definition().always_from_or_to_clear and self.object_state_from.get_definition().always_from_or_to_clear):
            if (other.object_state_from.get_state() == -1):
                return (self.object_state_from.get_state() == -1)
            elif (other.object_state_to.get_state() == -1):
                return (self.object_state_to.get_state() == -1)
            return False # this line should never be hit
        else:
            return ((other.object_state_from.get_state() == self.object_state_from.get_state()) and (other.object_state_to.get_state() == self.object_state_to.get_state()))


    def have_same_states(self, other):
        if ((self.object_state_to != None) and (other.object_state_to != None)):
            if (other.object_state_from.get_definition().always_from_or_to_clear and self.object_state_from.get_definition().always_from_or_to_clear):
                if (other.object_state_from.get_state() == -1):
                    return (self.object_state_from.get_state() == -1)
                elif (other.object_state_to.get_state() == -1):
                    return (self.object_state_to.get_state() == -1)
                return False # this line should never be hit
            else:
                return ((other.object_state_from.get_state() == self.object_state_from.get_state()) and (other.object_state_to.get_state() == self.object_state_to.get_state()))
        elif ((self.object_state_to == None) and (other.object_state_to == None)):
            if (other.object_state_to.get_definition().always_from_or_to_clear and self.object_state_to.get_definition().always_from_or_to_clear):
                if (other.object_state_to.get_state() == -1):
                    return (self.object_state_to.get_state() == -1)
                else:
                    return (self.object_state_to.get_state() != -1)
            else:
                return (other.object_state_from.get_state() == self.object_state_from.get_state())

    def __hash__(self): # TODO double check uniqueness
        if self.object_state_to == None:
            string = str(self.object_state_from.get_definition().id) + "--" + str(self.object_state_from.get_state())
            return string.__hash__()
        else:
            string = str(self.object_state_from.get_definition().id) + "--" + str(self.object_state_from.get_state()) + "   " + str(self.object_state_to.get_definition().id) + "--" + str(self.object_state_to.get_state())
            return string.__hash__()

