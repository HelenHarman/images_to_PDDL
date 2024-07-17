

# for all objects of type location are there are common features - can we cluster the locations into N groups
# for all objects of type object are there are common features
from enum import Enum

from action_graph.action_node import ActionNode, ActionNode_Type
from image_handling import util
from image_handling.image_area_of_transitions import ImageObject_Type


class EDGE_DISTANCE_TYPE(Enum):
    NONE = 0 # objects do not overlap horizontally or vertically. Find distance between there nearest points
    ABOVE = 1 # horizontally overlap # vertical distance between edges. and horizontal distance between center points
    BELOW = 2
    #ABOVE_ALIGNED = 3
    RIGHT = 3 # vertically overlap # horizontal distance between edges. and vertical distance between center points
    LEFT = 4
    #BELOW__ALIGNED =6
    #ALIGNED_RIGHT = 7
    #ALIGNED_LEFT = 8
    #ALIGNED__ALIGNED = 9

class ObjectRelativePositions:
    def __init__(self, object_with_position):
        self.object_with_position = object_with_position
                # distances are from/to edges of objects; first item in each list is the edge of the image
        #self.objects_above = {} # object/edge -> distance_x, distance_y
        #self.objects_below = {}
        #self.objects_left = {}
        #self.objects_right = {}

        self.objects_edge_distance = {} # object/edge -> distance_x, distance_y, EDGE_DISTANCE_TYPE, distance between center locations ; is_above=the object in this map is above the object_with_position object
        self.objects_edge_distance_to_params = {}
        #self.objectWithPositionOrImageEdge = objectWithPositionOrImageEdge
        #self.imageEdge = imageEdge # array of boolean values of equal length to objectWithPositionOrImageEdge
        self.add_object(None, is_edge=True)

    def add_object(self, object, is_edge =False, is_param =False):
        if (is_edge):
            self.objects_edge_distance["top"] = (self.object_with_position.get_center_x, self.object_with_position.get_max_y(), EDGE_DISTANCE_TYPE.ABOVE, -1)
            self.objects_edge_distance["bottom"] = (self.object_with_position.get_center_x, self.object_with_position.min_y, EDGE_DISTANCE_TYPE.BELOW, -1)
            self.objects_edge_distance["right"] = (self.object_with_position.get_max_x(), self.object_with_position.get_center_y, EDGE_DISTANCE_TYPE.RIGHT, -1)
            self.objects_edge_distance["left"] = (self.object_with_position.min_x, self.object_with_position.get_center_y, EDGE_DISTANCE_TYPE.LEFT, -1)
        else:
            to_be_inserted = None
            x1 = self.object_with_position.get_center_x()
            y1 = self.object_with_position.get_center_y()
            x2 = object.get_center_x()
            y2 = object.get_center_y()
            distance = util.get_distance(x1, y1, x2, y2)
            # object.min_x must be between self.object_with_position.min_x and self.object_with_position.get_max_x() - or object.get_max_x() must be between  self.object_with_position.min_x and self.object_with_position.get_max_x()
            if ((object.min_x > self.object_with_position.min_x and object.min_x < self.object_with_position.get_max_x())
                or (object.get_max_x() > self.object_with_position.min_x and object.get_max_x() < self.object_with_position.get_max_x())):  # object is above or below
                x_difference = self.object_with_position.get_center_x() - object.get_center_x()
                if (object.min_y > self.object_with_position.get_max_y()): # object is above
                    y_difference = object.min_y - self.object_with_position.get_max_y()
                    to_be_inserted = (x_difference, y_difference, EDGE_DISTANCE_TYPE.ABOVE, distance)
                elif (object.get_max_y() <  self.object_with_position.min_y): # object is below
                    y_difference = object.get_max_y() - self.object_with_position.min_y
                    to_be_inserted = (x_difference, y_difference, EDGE_DISTANCE_TYPE.BELOW, distance)

            elif ((object.min_y > self.object_with_position.min_y and object.min_y < self.object_with_position.get_max_y())
                or (object.get_max_y() > self.object_with_position.min_y and object.get_max_y() < self.object_with_position.get_max_y())):  # object is to the right or left
                y_difference = self.object_with_position.get_center_y() - object.get_center_y()
                if (object.min_x > self.object_with_position.get_max_x()): # object is right
                    x_difference = object.min_x - self.object_with_position.get_max_x()
                    to_be_inserted = (x_difference, y_difference, EDGE_DISTANCE_TYPE.RIGHT, distance)
                elif (object.get_max_x() <  self.object_with_position.min_x): # object is left
                    x_difference = object.get_max_x() - self.object_with_position.min_x
                    to_be_inserted = (x_difference, y_difference, EDGE_DISTANCE_TYPE.LEFT, distance)

            if (is_param):
                self.objects_edge_distance_to_params[object] = to_be_inserted
            else:
                self.objects_edge_distance[object] = to_be_inserted
            # TODO handle overlapping objects.



class ActionObjectsWithFeatures:
    def __init__(self, action_node):
        self.action_node
        #self.pre_relative_positions_to_other_params = []
        self.pre_relative_positions = []# for every object in the list of pre-objects what are there relative positions to all other objects in the image (including image edges)
        self.add_relative_positions()
    def add_relative_positions(self):
        for object_pre in self.action_node.image_objects_pre:
            object_pre_rel = ObjectRelativePositions(object_pre)
            for object in self.action_node.image_objects_pre:
                if object == object_pre:
                    continue
                object_pre_rel.add_object(object)
            for object in self.action_node.unchanged_objects:
                object_pre_rel.add_object(object)
            self.pre_relative_positions.append(object_pre_rel)



class ObjectActions:
    #        ImageObject (without position)
    def __init__(self, object):
        self.object = object

    # if swap action are objects always relative to each other. or relative to other objects

    # if two actions take the same number of parameters and they are of the same type; they could be the same action <-- aim to get smallest set of actions without allowing invalid actions.

    # action common params
    #

    # each time an object is acted on what are the common features. i.e., its relative position to the other params and its position related to other objects.

class ActionGroup():
    def __init__(self, initial_action):
        self.actions_with_features = []
        self.preconditions = []
        self.effects = []
        self.add_action(initial_action)

    def init_preconditions(self):
        if (self.actions_with_features[0].actin_type == ActionNode_Type.SWAP):
            have_same_image = True
            #for


            if (self.actions_with_features[0].image_objects_pre[0].objectImage.type == ImageObject_Type.OBJECT and self.actions_with_features[0].image_objects_pre[1].objectImage.type == ImageObject_Type.LOCATION):
                self.preconditions.append("(is-clear " + str(self.actions_with_features[0].image_objects_pre[1].get_center_x()) + "_" + str(self.actions_with_features[0].image_objects_pre[1].get_center_y()) + ")")
                self.preconditions.append("(not (is-clear " + str(self.actions_with_features[0].image_objects_pre[0].get_center_x()) + "_" + str(self.actions_with_features[0].image_objects_pre[0].get_center_y()) + "))")
                self.effects.append("(not (is-clear " + str(self.actions_with_features[0].image_objects_pre[1].get_center_x()) + "_" + str(self.actions_with_features[0].image_objects_pre[1].get_center_y()) + "))")
                self.effects.append("(is-clear " + str(self.actions_with_features[0].image_objects_pre[0].get_center_x()) + "_" + str(self.actions_with_features[0].image_objects_pre[0].get_center_y()) + ")")


                self.effects.append("(not (at obj" + str(self.actions_with_features[0].image_objects_pre[0].imageObject.id) +  " " + str(self.actions_with_features[0].image_objects_pre[0].get_center_x()) + "_" + str(self.actions_with_features[0].image_objects_pre[0].get_center_y()) + "))")
                self.effects.append("(at obj" + str(self.actions_with_features[0].image_objects_pre[0].imageObject.id) + " " + str(self.actions_with_features[0].image_objects_pre[1].get_center_x()) + "_" + str(self.actions_with_features[0].image_objects_pre[1].get_center_y()) + ")")





    def do_params_fully_match(self, action):
        return (self.actions_with_features[0].manipulates_same_objects(action) and self.actions_with_features[0].action_type == action.action_type)




    def add_action(self, action):
        self.actions_with_features.append(action)
        action.order_params_locations_last()



    def calc_matching_features(self):



        self.params_distances_equal = False#[False] * len(self.actions_with_features[0].image_objects_pre)


   # def __eq__(self, other):
   #     if (isinstance(other, ActionNode)):
    #        return self.do_params_fully_match(other)
    #    else:
    #        return False





def get_matching_actions_preconditions(all_actions):
    action_groups = []
    actions_with_features = []
    for action in all_actions:
        actions_with_features.append(ActionObjectsWithFeatures(action))
        for action_group in action_groups:
            if action_group.do_params_fully_match(action):
                action_group.add_action(action)
            else:
                action_groups.append(ActionGroup(action))





def location_check(all_objects, all_actions):
    pass
    # locations with the same size (do all these have something in common - is it the same for all sets)
    # locations with the same center location (do all these have something in common - is it the same for all sets)













#!!!! if two actions have the same pre-image and the same objects are swapped but 1 of there resulting locations is not the same; then the object from the first image's different location is not an object.
    #                       it is a location relative to another object (or the edge of the image)

# Detecting all objects in all other images:
#       if action1 is before action2 and different object's state is changed we know the state of the objects from the previous image

# Detecting objects in the initial and goal states:
#       if all objects are in all images and don't overlap in the initial state we know this is also true. If two object always overlap they must also overlap in the intial state.



# if an object appears multiple times then it is a state and the location is the object (no so, what if there are multiple robot's who have locations.... the locations could still be treated as objects)
# other actions : crop image around the (multiple) changed locations.
#   Discover objects: For every transition if pixel1 changes state what other pixels change state (i.e., pixels in common) - (if pixel1 changes by value x in two images then if the pixel belongs to the object it will also change by the same amount if it belongs to the same object. <-- only if object has two states if object has multiple states then multiple values could be possible)
#                   if that pattern of pixels is repeated then those are the objects (locations)



#(do locations that never change state have a common attribute e.g. colour?)



# each time the Objects appear in the image what are its common features, i.e, how is it rediscovered.




# if action is attached to OR branch


# in ToH white object can be in more than one place at the same time

