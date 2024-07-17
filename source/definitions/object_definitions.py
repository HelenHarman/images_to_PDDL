# file contains the following classes: ObjectDefinition, LocationDefinition and ImageObjectDefinition

from definitions.domain_definition import PredicateDefinition
from image_handling import util


#===================================================
# helper methods:

def find_object_definition(object_definitions, string_id):
    for object_definition in object_definitions:
        if object_definition.get_string_id() == string_id:
            return object_definition
    return None

#-------------------

def is_image_object_area_in_image_obj_def_list(image_object_area, obj_def_list):
    for obj_def in obj_def_list:
        if obj_def.image_object_area == image_object_area:
            return True
    return False

#dummy_object_definition = ObjectDefinition()
#dummy_object_definition.type = "object"

#===================================================

id_for_object_definition = 0
class ObjectDefinition:
    type = "unknown"
    def __init__(self):
        global id_for_object_definition
        self.id = id_for_object_definition
        id_for_object_definition = id_for_object_definition + 1

        self.value_to_actions_that_result_in_value_and_their_common_atoms = {} # e.g. -1 --> ([action1,], ["at..."])

    #-------------------------------------------

    def add_value_to_actions_and_common_atoms(self, result_value, actions_that_set_value, common_atoms):
        self.value_to_actions_that_result_in_value_and_their_common_atoms[result_value] = (actions_that_set_value, common_atoms)

    #-------------------------------------------
    # if self is a location then this will return the object that is at the location or none (as it is "clear")
    # otherwise self is a image_object and self is returned.
    def get_defined_image_obj_and_its_atom_from_state(self, grounded_state):
        object_state_atoms = grounded_state.get_fluent_atoms_for_object(self)
        for object_state_atom in object_state_atoms: #object_state_atom in atoms: #
            #if self in object_state_atom.defined_objects:
            if (((object_state_atom.predicate.name == "at")) and (not object_state_atom.negated)):
                return object_state_atom.defined_objects[0]
            elif ((object_state_atom.predicate.name == "clear") and (not object_state_atom.negated)):
                return None

    #-------------------------------------------
    # getters
    def get_string_id(self):
        return self.type + "_" + str(self.id)

    #-----------------

    def get_type(self):
        return self.type
    #-------------------------------------------

    def __eq__(self, other):
        return (isinstance(other, ObjectDefinition) and self.id == other.id and self.type == other.type)

    def __hash__(self):
        return self.id


#===================================================

class LocationDefinition(ObjectDefinition):
    type = "location"
    def __init__(self, image_area):
        ObjectDefinition.__init__(self)
        self.image_area = image_area

        self.image_states = [] # to check if location has a clear state;  only used prior to image_object_definitions having been determined.
        self.image_obj_def_to_image_state = {}

        self.always_from_or_to_clear = False
        self.clear_state = None

        #self.image_state_ids = {} # from state --> [to states]
        #self.possible_clear_states = []

        self.depends_on = []
        self.depends_on_preconditions = {}

        self.changed_together = []

    # -----------------------------------------------

    def does_change_together_with(self, other_location):
        for locations in self.changed_together:
            if other_location in locations:
                return True

    # -----------------------------------------------

    def insert_image_state(self, image_state):
        # image_states are used to check if the image transitions between a clear state and another state.
        # only used prior to image_object_definitions having been determined, then use image_obj_def_to_image_state
        for image in self.image_states:
            if util.are_images_equal(image, image_state):
                return
        self.image_states.append(image_state)
    # -----------------------------------------------

    def set_clear_state(self, clear_state):
        self.always_from_or_to_clear = True
        self.clear_state = clear_state

     # -----------------------------------------------

    def create_image_object_definition_to_image_state_map(self, image_object_definitions):
        inserted = []
        for image_object_definition in image_object_definitions:
            image_state_index = self.get_image_state_for_object_image_definition(image_object_definition, inserted)
            if (image_state_index != -1):
                inserted.append(image_state_index)
                self.image_obj_def_to_image_state[image_object_definition.id] = self.image_states[image_state_index]

    # -----------------------------------------------

    def get_image_state_for_object_image_definition(self, image_object_definition, inserted):
        for i in range(len(self.image_states)):
            image_state = self.image_states[i]
            if ((i in inserted) or ((image_object_definition.image_object_area.image.shape[1] > image_state.shape[1]) or (image_object_definition.image_object_area.image.shape[0] > image_state.shape[0]))):
                continue

            if (image_object_definition.image_object_area.center_matches):
                min_x = int((float(image_state.shape[1]) / 2.0) - (float(image_object_definition.image_object_area.image.shape[1]) / 2.0))  # arrays start from 0, so need -1
                min_y = int((float(image_state.shape[0]) / 2.0) - ( float(image_object_definition.image_object_area.image.shape[0]) / 2.0))
            else:
                min_x = 0 - image_object_definition.image_object_area.location_min_x_offset
                min_y = 0 - image_object_definition.image_object_area.location_min_y_offset

            max_x = min_x + image_object_definition.image_object_area.image.shape[1]
            max_y = min_y + image_object_definition.image_object_area.image.shape[0]

            cropped_image = image_state[min_y:max_y + 1, min_x:max_x + 1]
            if (util.are_images_equal(image_object_definition.image_object_area.image, cropped_image)):
                return i
        return -1

    #==================================================
    # predicate translation

    def get_defined_predicates(self):
        if (self.always_from_or_to_clear):
            return [PredicateDefinition("clear", [self.type])]
        else:
            return []

    # -----------------------------------------------

    def translate_atom_into_state_id(self, atom): # Used in discovering the location's dependencies
        if ((atom.predicate.name == "at") and (not atom.negated) and (atom.defined_objects[1] == self)):
            if self.always_from_or_to_clear:
                return 0
            else:
                return atom.defined_objects[0].id
        elif ((atom.predicate.name == "clear") and (not atom.negated) and (atom.defined_objects[0] == self)):
            return 0
        elif ((atom.predicate.name == "clear") and (atom.negated) and (atom.defined_objects[0] == self)):
            return -1
        else:
            return -404 #TODO

    #==================================================

    def create_defined_object_dependencies_and_add_depends_on(self, preconditions, state):
        dependencies = []
        defined_object_dependencies = []
        for precondition in preconditions:
            for defined_object in precondition.defined_objects:
                if ((defined_object.id not in dependencies) and (defined_object.id != self.id)):
                    dependencies.append(defined_object) #.id)
                    defined_object_dependencies.append(defined_object)
        if (state not in self.depends_on_preconditions):
            if (dependencies not in self.depends_on):
                self.depends_on.append(dependencies)
            self.depends_on_preconditions[state] = preconditions.copy()

        return defined_object_dependencies

    # -----------------------------------------------

    def get_location_state_for_object_image_definition(self, image_object_definition): # used to turn plan into images
        return self.image_obj_def_to_image_state[image_object_definition.id]

    # -----------------------------------------------
    """
    def add_image_object_definition_change_from_to(self, image_object_definition_pre, image_object_definition_suc):
        from_id = -1
        to_id = -1
        if image_object_definition_pre != None:
            from_id = image_object_definition_pre.id
        if image_object_definition_suc != None:
            to_id = image_object_definition_suc.id
        if from_id in self.image_state_ids:
            self.image_state_ids[from_id].append(to_id)
        else:
            self.image_state_ids[from_id] = [to_id]
    """

#===============================================

class ImageObjectDefinition(ObjectDefinition):
    type = "image"
    def __init__(self, image_object_area):
        ObjectDefinition.__init__(self)
        self.image_object_area = image_object_area
        self.image_object_area.set_not_belongs_to_transition()
        image_object_area.changed_image_area_of_transition = None

    # ----------------

    def get_defined_predicates(self):
        return [PredicateDefinition("at", [self.type, LocationDefinition.type])]


#==============================================================================
#==============================================================================