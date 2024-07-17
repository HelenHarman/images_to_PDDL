from enum import Enum

import cv2
import numpy as np

from action_graph import create_action_graph
from definitions import create_object_definitions, create_grounded_state, object_definitions, domain_definition, \
    grounded_state
from definitions.grounded_state import GroundedState
from definitions.object_definitions import ImageObjectDefinition
from generate_images import image_pairs
from image_handling import parse_images_to_create_transitions_and_locations, image_area_of_transitions, util, \
    image_object
from image_handling import parse_images_to_create_transitions_and_locations as image_parsing

# Detect pattern and thus bypass slow stuff... if no pattern then fallback to slow stuff
#   To detect pattern: Are all locations of the same size, and the gaps between closest vertically aligned and horizontally aligned locations the same?
#   If so: Read-in all transitions possible from a single state and find the overlapping image-area(s) (note, make sure the big area doesn't delete the smallest area).
#          Use these locations to determine all locations and thus image-objects the clear state
#          Use features of original "linked" static atoms to determine the linkings for these new locations.

#==========================================================================
# main method
def create_objects_and_static_atoms(precreated_domain, precreated_locations, precreated_objects,  domain_name, create_images, domain_config, precreated_static_atoms):
    original_static_atoms = precreated_static_atoms.copy()
    #GroundedState.static_atoms.clear()

    common_features = CommonFeatures(precreated_locations, precreated_objects, original_static_atoms) #, static_atoms)
    #common_features.generate_location_object_feature_list()
    #if (len(common_features.location_common_heights) == 1 and len(common_features.location_common_widths) == 1 and (common_features.discover_adjacent_locations() != None) and common_features.adjacent_locations_are_linked): #len(common_features.vertical_gaps) == 1 and len(common_features.horizontal_gaps) == 1):
    if (common_features.is_speed_up_version_possible()): # fast method
        print ("quick method")
        image_pairs_iter = image_pairs.ImagePairs(domain_name, create_images, domain_config, False)
        transformer = TransitionToObjectsAndStaticAtoms(image_pairs_iter, precreated_domain, common_features)
        location_definitions, image_object_definitions, grounded_state = transformer.find_object_definitions(precreated_locations[0].clear_state)
    else:# slow method
         print ("slow method")
         clear_all_info()
         image_pairs_iter = image_pairs.ImagePairs(domain_name, create_images, domain_config, True)
         transitions, all_image_areas = image_parsing.parse_images(image_pairs_iter)  # image_directory)
         location_definitions, image_object_definitions = create_object_definitions.create_object_and_location_definitions(all_image_areas, transitions)
         create_action_graph.create_action_graph(transitions, location_definitions, image_object_definitions)

    return location_definitions, image_object_definitions, image_pairs_iter

#==========================================================================
# helper methods

def clear_all_info(): #  this should be moved to "run_experiments.py"
    object_definitions.id_for_object_definition = 0
    grounded_state.GroundedState.static_atoms.clear()
    domain_definition.defined_predicates.clear()
    domain_definition.action_definition_id = 0


def create_location_grid(precreated_locations):
    #print("create_location_grid")
    precreated_locations.sort(key=lambda x: x.image_area.min_x)
    locations_grid = []
    locations = []
    for location in precreated_locations:
        if ((locations) and (location.image_area.min_x != locations[0].image_area.min_x)):
            locations.sort(key=lambda x: x.image_area.min_y)
            locations_grid.append(locations.copy())
            locations.clear()
        locations.append(location)
    locations.sort(key=lambda x: x.image_area.min_y)
    locations_grid.append(locations.copy())
    #print("done create_location_grid")
    return locations_grid

#==========================================================================

class TransitionToObjectsAndStaticAtoms:
    def __init__(self, image_pairs_iter, precreated_domain, common_features):
        self.transitions, self.initial_image_areas = parse_images_to_create_transitions_and_locations.parse_images(image_pairs_iter, True)
        self.domain = precreated_domain
        self.common_features = common_features #CommonFeatures(precreated_locations, precreated_objects, static_atoms)

    #----------------------------------------------------------------

    def find_object_definitions(self, original_clear_state):
        self.find_image_areas(self.transitions[0].pre_image.get_image())

        self.location_definitions = create_object_definitions.create_location_definitions(self.image_areas, self.transitions)
        self.discover_and_set_clear_state(original_clear_state)
        self.create_image_object_definitions(self.transitions[0].pre_image.get_image())

        #self.location_definitions, self.image_object_definitions = create_object_definitions.create_object_and_location_definitions(self.image_areas, self.transitions)
        print("Number of locations = " + str(len(self.location_definitions)))
        print("Number of image objects = " + str(len(self.image_object_definitions)))

        # create static atoms:
        grounded_state = GroundedState()
        locations_grid = create_location_grid(self.location_definitions)

        #for locations in locations_grid:
        #    for location in locations:
        #        print(str(location.get_string_id()))
        if (self.common_features.is_single_object_linked()):
            self.link_to_single_adjacent_node(locations_grid, grounded_state)
        else:
            self.link_to_all_adjacent_nodes(locations_grid, grounded_state)

        return self.location_definitions, self.image_object_definitions, grounded_state

    # ---------------------------------------------------------
    # link locations together:

    def link_to_single_adjacent_node(self, locations_grid, grounded_state):
        for i in range(len(locations_grid[0])):  #for each row:
            for j in range(len(locations_grid)):
                print (locations_grid[j][i].get_string_id() + " " + str(locations_grid[j][i].image_area) + "i="+ str(i) + "j="+ str(j))

        for i in range(len(locations_grid[0])):  #for each row:
            for j in range(len(locations_grid)):
                if (i != (len(locations_grid[0])-1)):
                    location_definitions = [locations_grid[j][i], locations_grid[j][i+1]]
                    create_grounded_state.add_changed_together_link_atom_to_states(location_definitions, grounded_state)
                if (j != (len(locations_grid)-1)):
                    location_definitions = [locations_grid[j][i], locations_grid[j+1][i]]
                    create_grounded_state.add_changed_together_link_atom_to_states(location_definitions, grounded_state)

    #----------------------------

    def link_to_all_adjacent_nodes(self, locations_grid, grounded_state):
        for i in range(len(locations_grid[0])):  #for each row:
            for j in range(len(locations_grid)):
                location_definitions = [locations_grid[j][i]]
                if (i != 0):
                    location_definitions.append(locations_grid[j][i-1])
                if (i != (len(locations_grid[0])-1)):
                    location_definitions.append(locations_grid[j][i+1])
                if (j != 0):
                    location_definitions.append(locations_grid[j-1][i])
                if (j != (len(locations_grid)-1)):
                    location_definitions.append(locations_grid[j+1][i])

                create_grounded_state.add_changed_together_link_atom_to_states(location_definitions, grounded_state)

    # ---------------------------------------------------------

    def discover_and_set_clear_state(self, original_clear_state):
        clear_state = None
        found_clear = False
        for location_definition in self.location_definitions:
            progress = 0  # 0 = start; 1 = first transition that changes location found; 2 = state1 is matching; 3 = state2 is matching; 4 no state match
            state1 = None
            state2 = None
            for transition in self.transitions:
                if transition.does_transition_modify_area(location_definition.image_area):
                    if (progress == 0):
                        state1 = location_definition.image_area.crop_image(transition.pre_image.get_image())  # [location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                        state2 = location_definition.image_area.crop_image(transition.suc_image.get_image())  # transition.suc_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                        progress = 1
                        if (util.are_images_equal(original_clear_state, state1)):
                            clear_state = state1
                            found_clear = True
                            break
                        elif (util.are_images_equal(original_clear_state, state2)):
                            clear_state = state2
                            found_clear = True
                            break
                    elif (progress >= 1):
                        other_state1 = location_definition.image_area.crop_image(transition.pre_image.get_image())  # transition.pre_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                        other_state2 = location_definition.image_area.crop_image(transition.suc_image.get_image())  # transition.suc_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                        if ((progress == 1) and (util.are_images_equal(state1, other_state1) or util.are_images_equal(state1,other_state2)) and (util.are_images_equal(state2, other_state1) or util.are_images_equal(state2, other_state2))):
                            progress = 1
                        elif ((progress == 1 or progress == 2) and (util.are_images_equal(state1, other_state1) or util.are_images_equal(state1, other_state2))):
                            clear_state = state1
                            found_clear = True
                            break
                        elif ((progress == 1 or progress == 3) and (util.are_images_equal(state2, other_state1) or util.are_images_equal(state2,other_state2))):
                            clear_state = state2
                            found_clear = True
                            break
                        #else: progress = 4 break
            if (found_clear):
                break
        for location_definition in self.location_definitions:
            location_definition.set_clear_state(clear_state)

    # ---------------------------------------------------------

    def create_image_object_definitions(self, image):
        self.image_object_definitions = []
        image_object_areas = []
        #image_edit = image.copy()
        for location_definition in self.location_definitions:
            #--print(location_definition.get_string_id() + " " + str(location_definition.image_area) )
            cropped_image = location_definition.image_area.crop_image(image)
            image_object_area = image_object.ImageObjectArea(cropped_image, location_definition.image_area, 0, 0, True)
            if (not util.are_images_equal(cropped_image, location_definition.clear_state) and (image_object_area not in image_object_areas)):
                image_object_areas.append(image_object_area)
                self.image_object_definitions.append(ImageObjectDefinition(image_object_area))

    # ---------------------------------------------------------

    def find_image_areas(self, image):
        image_area = self.get_smallest_image_area()
        self.set_vertical_and_horizontal_gaps(image_area)
        #print ("init image area = " + str(image_area))
        #print ("image = " + str(image.shape[1])+", " + str(image.shape[0]))
        self.image_areas = []
        # negative y direction

        #print ("v GAP:" + str(self.vertical_gap))
        #print ("h GAP:" + str(self.horizontal_gap))

        #print("find image areas negative y " )
        current_min_y = image_area.min_y  #
        while current_min_y >= 0: #(image_area.get_height() + self.common_features.vertical_gap):
            self.find_image_area_x_iter(image, current_min_y, image_area)
            current_min_y = current_min_y - (image_area.get_height() + self.vertical_gap)

        # positive y direction
        #print("find image areas positive y ")
        current_min_y = image_area.min_y + image_area.get_height() + self.vertical_gap  # skip initial square
        while current_min_y <= (image.shape[0] - image_area.get_height()) :# + self.common_features.vertical_gap): #image.shape[0] <= (current_min_y + image_area.get_height() + self.common_features.vertical_gap):
            self.find_image_area_x_iter(image, current_min_y, image_area)
            current_min_y = current_min_y + (image_area.get_height() + self.vertical_gap)

    #-----------------------------------

    def get_smallest_image_area(self):
        smallest = None
        size_of_smallest = -1
        for img_area in self.initial_image_areas :
            area = img_area.get_area()
            if((smallest == None) or (size_of_smallest > area)):
                smallest = img_area
                size_of_smallest = area
        return smallest

    # --------------------------
    def set_vertical_and_horizontal_gaps(self, smallest_image_area): # i.e., Fix for gap between objects issue:
        if (self.common_features.object_same_size_as_gaps):
            # print("same size")
            self.vertical_gap = self.common_features.vertical_gap
            self.horizontal_gap = self.common_features.horizontal_gap
        else:
            self.vertical_gap = 0
            self.horizontal_gap = 0
            max_count = self.common_features.get_max_num_linked_objects()

            for img_area in self.initial_image_areas:
                if (img_area.get_height() >= (smallest_image_area.get_height() * 2) and img_area.min_x == smallest_image_area.min_x):
                    count = 1
                    self.vertical_gap = img_area.get_height()
                    while (self.vertical_gap > smallest_image_area.get_height() and count < max_count):
                        count = count + 1
                        self.vertical_gap = (img_area.get_height() - (smallest_image_area.get_height() * count))
                    self.vertical_gap = int(self.vertical_gap / (count - 1))
                    # print ("self.vertical_gap" + str(self.vertical_gap) + " " + str(count))

                if (img_area.get_width() >= (smallest_image_area.get_width() * 2) and img_area.min_y == smallest_image_area.min_y):
                    count = 1
                    self.horizontal_gap = img_area.get_width()
                    while (self.horizontal_gap > smallest_image_area.get_width() and count < max_count):
                        count = count + 1
                        self.horizontal_gap = (img_area.get_width() - (smallest_image_area.get_width() * count))
                    self.horizontal_gap = int(self.horizontal_gap / (count - 1))
                    # print ("self.horizontal_gap" + str(self.horizontal_gap) + " " + str(count))
            """
                if (img_area.get_width() == smallest.get_width() and img_area.min_x == img_area.min_x and img_area.get_height() != smallest.get_height()):
                    self.common_features.vertical_gap = img_area.get_height() - (smallest.get_height() * 2)
                if (img_area.get_height() == smallest.get_height() and img_area.min_y == img_area.min_y and img_area.get_width() != smallest.get_width()):
                    self.common_features.horizontal_gap = img_area.get_width() - (smallest.get_width() * 2)
            """
    # ---------------------------------

    def find_image_area_x_iter(self, image, current_min_y, image_area):
        # negative x direction
        #print("find image areas negative x ")
        current_min_x = image_area.min_x
        while current_min_x >= 0:#(image_area.get_width() + self.common_features.horizontal_gap):
            max_x = current_min_x + image_area.get_width()
            max_y = current_min_y + image_area.get_height()
            self.image_areas.append(image_area_of_transitions.ImageArea(current_min_x, current_min_y, max_x, max_y))
            current_min_x = current_min_x - (image_area.get_width() + self.horizontal_gap)

        # positive x direction
        #print("find image areas positive x ")
        current_min_x = image_area.min_x + image_area.get_width() + self.horizontal_gap #skip initial square
        while current_min_x <= (image.shape[1] - image_area.get_width()):# + self.common_features.horizontal_gap): # <= (current_min_x + image_area.get_width() + self.common_features.horizontal_gap):
            max_x = current_min_x + image_area.get_width()
            max_y = current_min_y + image_area.get_height()
            self.image_areas.append(image_area_of_transitions.ImageArea(current_min_x, current_min_y, max_x, max_y))
            current_min_x = current_min_x + (image_area.get_width() + self.horizontal_gap)

    # ---------------------------------------------------------

#=========================================================

class CommonFeatures:
    def __init__(self, precreated_locations, precreated_objects, static_atoms):
        self.precreated_locations = precreated_locations
        self.precreated_objects = precreated_objects

        self.static_atoms = static_atoms
        self.vertical_gap = -1
        self.horizontal_gap = -1
        self.object_same_size_as_gaps = False

        self.adjacent_locations_are_linked = True

    def is_single_object_linked(self):
        for linked_atom in self.static_atoms:
            if (("changed_together_link_" in linked_atom.predicate.name) and (len(linked_atom.defined_objects) > 2) ):
                return False
        return True

    #---------------------------------------

    def get_max_num_linked_objects(self):
        max_num = 0
        for linked_atom in self.static_atoms:
            if (("changed_together_link_" in linked_atom.predicate.name) and (len(linked_atom.defined_objects) > max_num) ):
                max_num = len(linked_atom.defined_objects)
        return max_num

    #---------------------------------------

    def is_speed_up_version_possible(self):
        self.generate_location_object_feature_list()
        return ((len(self.location_common_heights) == 1) and (len(self.location_common_widths) == 1)
                and (self.discover_adjacent_locations() != None) and self.adjacent_locations_are_linked)

    #---------------------------------------

    def generate_location_object_feature_list(self):
        self.location_common_widths = {}
        self.location_common_heights = {}
        for location_object in self.precreated_locations:
            feature = location_object.image_area.get_width() #Feature(FeatureType.WIDTH, location_object.image_area.get_width())
            if feature in self.location_common_widths:
                self.location_common_widths[feature].append(location_object)
            else:
                self.location_common_widths[feature] = [location_object]

            feature = location_object.image_area.get_height() #Feature(FeatureType.HEIGHT, location_object.image_area.get_height())
            if feature in self.location_common_heights:
                self.location_common_heights[feature].append(location_object)
            else:
                self.location_common_heights[feature] = [location_object]

    #---------------------------------------

    def discover_adjacent_locations(self):
        self.locations_grid = create_location_grid(self.precreated_locations)
        #print (str(self.locations_grid))
        horizontal_gap = -1
        for i in range(len(self.locations_grid[0])):  #for each row:
            for j in range(len(self.locations_grid)-1):
                #print(len(self.locations_grid))
                #print (j)
                if (not self.locations_grid[j+1][i].does_change_together_with(self.locations_grid[j][i])):
                    self.adjacent_locations_are_linked = False

                gap = self.locations_grid[j+1][i].image_area.min_x - (self.locations_grid[j][i].image_area.min_x + self.locations_grid[j][i].image_area.get_width())
                if (horizontal_gap == -1):
                    horizontal_gap = gap
                elif (horizontal_gap != gap):
                    return None

        vertical_gap = -1
        for i in range(len(self.locations_grid)):  # for each row:
            for j in range(len(self.locations_grid[0]) - 1):

                if (not self.locations_grid[i][j+1].does_change_together_with(self.locations_grid[i][j])):
                    self.adjacent_locations_are_linked = False

                gap = self.locations_grid[i][j+1].image_area.min_y - (self.locations_grid[i][j].image_area.min_y + self.locations_grid[i][j].image_area.get_height())
                if (vertical_gap == -1):
                    vertical_gap = gap
                elif (vertical_gap != gap):
                    return None

        self.vertical_gap = vertical_gap
        self.horizontal_gap = horizontal_gap

        #print ("setting ... vG=" + str(self.vertical_gap) + "h=" + str(self.precreated_locations[0].image_area.get_height()))
        #print("setting ... hG=" + str(self.horizontal_gap) + "w=" + str(self.precreated_locations[0].image_area.get_width()))
        self.object_same_size_as_gaps = (self.vertical_gap == self.precreated_locations[0].image_area.get_height()+1 and self.horizontal_gap == self.precreated_locations[0].image_area.get_width()+1)

        return (self.horizontal_gap, self.vertical_gap)
    #---------------------------------------

#=============================================================================
# =============================================================================




# scratch:

    """
    
    def generate_static_atom_feature_list(self):
        self.linked_features = [] # loc_depends_on_precondtions = {}
        for linked_atom in self.static_atoms:
            if ("changed_together_link_" in linked_atom.predicate.name):
                processed = []
                features = []
                for object in linked_atom.predicate.defined_objects:
                    processed.append(object)
                    for object2 in linked_atom.predicate.defined_objects:
                        if (object in processed):
                            continue
                        if (self.are_locations_vertically_aligned(object, object2)):
                            diff = self.get_edge_distance_vertically_aligned(object, object2)
                            features.append(Feature(FeatureType.VERTICALLY_ALIGNED), diff)
                        elif (self.are_locations_horizontally_aligned(object, object2)):
                            diff = self.get_edge_distance_horizontally_aligned(object, object2)
                            features.append(Feature(FeatureType.HORIZONTALLY_ALIGNED), diff)
                if (features not in self.linked_features):
                    self.linked_features.append(features)

    def are_locations_vertically_aligned(self, location1, location2):
        return location1.image_area.get_center_x_location() == location2.image_area.get_center_x_location()

    def are_locations_horizontally_aligned(self, location1, location2):
        return location1.image_area.get_center_y_location() == location2.image_area.get_center_y_location()


    def get_edge_distance_vertically_aligned(self, location1, location2):
        diff = abs(location1.image_area.get_center_y_location() - location2.image_area.get_center_y_location())
        return (diff - ( (float(location1.image_area.get_height())/2.0) + (float(location2.image_area.get_height())/2.0) )) # edge diff

    def get_edge_distance_horizontally_aligned(self, location1, location2):
        diff = abs(location1.image_area.get_center_x_location() - location2.image_area.get_center_x_location())
        return (diff - ( (float(location1.image_area.get_width())/2.0) + (float(location2.image_area.get_width())/2.0) )) # edge diff
    """
"""
class Feature:
    def __init__(self, feature_type, param):
        self.feature_type = feature_type
        self.param = param

    def __hash__(self):
        string_id = str(self.feature_type) + "_" + str(self.param)
        return string_id.__hash__()

    def __eq__(self, other):
        return (isinstance(other, Feature) and self.feature_type == other.feature_type and self.param == other.param)

class FeatureType(Enum):
    WIDTH = 0 # fluent objects
    HEIGHT = 1 # fluent objects
    VERTICALLY_ALIGNED = 2 # static atoms + objects
    HORIZONTALLY_ALIGNED = 3 # static atoms + objects
    DISTANCE_NEAREST_EDGES = 4 # static atoms + objects
    WIDTH_DIFFERENCE = 5 # static atoms + objects
    HEIGHT_DIFFERENCE = 6 # static atoms + objects

"""