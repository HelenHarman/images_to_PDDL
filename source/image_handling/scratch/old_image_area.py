

#




"""
def is_image_area_covered_by_overlapping_transitions(image_area, all_overlapping_transitions):
    contains_min_x, contains_max_x, contains_min_y, contains_max_y = False, False, False, False
    for overlapping_transitions in all_overlapping_transitions:
        if overlapping_transitions.overlap.is_overlapping(image_area):
            if image_area.min_x == overlapping_transitions.overlap.min_x:
                contains_min_x = True
            if image_area.max_x == overlapping_transitions.overlap.max_x:
                contains_max_x = True
            if image_area.min_y == overlapping_transitions.overlap.min_y:
                contains_min_x = True
            if image_area.max_y == overlapping_transitions.overlap.max_y:
                contains_max_y = True
        if (contains_min_x and contains_max_x and contains_min_y and contains_max_y):
            return True
    return False
"""
# ----------------------------------------------
# ----------------------------------------------

# all_created_overlapping_transitions = []
# original_overlap = ImageArea(self.overlap.min_x, self.overlap.min_y, self.overlap.max_x, self.overlap.max_y)
# original_transitions = self.transitions.copy()
# self.overlap.min_x = max(self.overlap.min_x, transition.changed_area.min_x)
# self.overlap.min_y = max(self.overlap.min_y, transition.changed_area.min_y)
# self.overlap.max_x = min(self.overlap.max_x, transition.changed_area.max_x)
# self.overlap.max_y = min(self.overlap.max_y, transition.changed_area.max_y)
"""
if create_overlapping_transactions:
    #--------------
    # As we are using rectangular areas, it may be that part of the cropped-area is unwanted as it does not contain any changes.
    # We check this for all transitions and, if it differs create, some new overlapping transitions objects
    image_areas = {}
    for self_transition in self.transitions:
        #print ("created_overlapping_transitions... " + str(len(self.transitions)))
        print ("overlap="+str(self.overlap))
        image_area = create_changed_image_area(self_transition.image_diff, self.overlap.min_x, self.overlap.min_y, self.overlap.max_x, self.overlap.max_y)
        if image_area not in image_areas and image_area.max_x != -1:
            image_areas[image_area] = [self_transition]
        elif image_area.max_x != -1:
            image_areas[image_area].append(self_transition)
    #if len(image_areas) == 1:
    #    self.overlap = image_areas.keys()[0]
    if len(image_areas) >= 1:
        self.overlap = list(image_areas.keys())[0]
        self.transitions = image_areas[self.overlap]
        for image_area in image_areas:
            if image_area == self.overlap:
                continue
            overlapping_transitions = OverlappingTransitions(image_area)
            overlapping_transitions.transitions = image_areas[image_area]
            all_created_overlapping_transitions.append(overlapping_transitions)
    else:
        print("ERROR: overlapping_image_area.OverlappingTransitions.update_overlapping_area()")
        exit(0)

    for created_overlapping_transitions in all_created_overlapping_transitions:
        found = False
        for overlapping_transitions in all_overlapping_transitions:
            if created_overlapping_transitions.overlap == overlapping_transitions.overlap:
                overlapping_transitions.transitions.extend(created_overlapping_transitions.transitions)
                found = True
                break
        if not found:
            all_overlapping_transitions.append(created_overlapping_transitions)

    # --------------
    # a single image could contain multiple overlapping areas, so don't just throw the original area away:
    if (not is_image_area_covered_by_overlapping_transitions(original_overlap, all_overlapping_transitions)):
        overlapping_transitions = OverlappingTransitions(original_overlap)
        overlapping_transitions.transitions = original_transitions
        all_overlapping_transitions.append(overlapping_transitions)       

return all_overlapping_transitions
"""
#def get_center_x_location(self):
#    return self.overlap.get_center_x_location()

#def get_center_y_location(self):
#   return self.overlap.get_center_y_location()








from enum import Enum

import cv2, sys
import numpy as np

# ====================================================






imageObjectId = 0
imageTypeId =0
class ObjectType:
    def __init__(self) :#, image_objects=[]):
        global imageTypeId
        self.image_objects = []#image_objects
        self.id = imageTypeId
        imageTypeId = imageTypeId + 1

#-------------------
class ImageObject_Type(Enum):
    UNKNOWN = 0
    OBJECT = 1 # <-- should have list of locations (i.e, states)?
    LOCATION = 2 # <-- should have list of images (i.e, states)?
# ImageObject will contain the things that will be true for all instances of that object.
class ImageObject:
    def __init__(self, image):
        global imageObjectId
        self.image = image #A cropped area, containing a single object, of an orginal image
        self.type = ImageObject_Type.UNKNOWN
        self.id = imageObjectId
        imageObjectId = imageObjectId + 1

    def isEquivalent(self, image):
        if (image.shape != self.image.shape):
            return False
        image_diff = self.image - image
        b, g, r = cv2.split(image_diff)
        return (cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0)

    def __eq__(self, obj):
        return isinstance(obj, ImageObject) and self.isEquivalent(obj.image)

#-------------------

# ImageObjectWithPosition is the objects location in the pre/suc image. (details specific to the pre/suc image)
class ImageObjectWithPosition:
    def __init__(self, imageObject, min_x, min_y):
        self.imageObject = imageObject
        self.min_x = min_x
        self.min_y = min_y

    def is_same_object(self, other): # same object but locations could be different; or same location with different objects.
        if (self.imageObject.type != other.imageObject.type):
            return False

        if ((self.imageObject.type == ImageObject_Type.UNKNOWN or self.imageObject.type == ImageObject_Type.OBJECT)
                and ( other.imageObject.type == ImageObject_Type.UNKNOWN or other.imageObject.type == ImageObject_Type.OBJECT)):
            return self.imageObject == other.imageObject
        else: # is location:
            return (self.min_x == other.min_x and self.min_y == other.min_y and self.imageObject.image.shape == other.imageObject.image.shape) # TODO <-- check is this ok

    def has_same_location(self, other):
        return ((self.min_x == other.min_x) and (self.min_y == other.min_y))


    def get_center_x_y_position(self):
        return ((self.min_x + (self.imageObject.image.shape[1]/2)), (self.min_y + (self.imageObject.image.shape[0]/2)))


    def get_center_x(self):
        return (float(self.min_x) + float(float(self.imageObject.image.shape[1])/2))

    def get_center_y(self):
        return (float(self.min_y) + float(float(self.imageObject.image.shape[0]) / 2))

    def get_max_x(self):
        return (self.min_x + (self.imageObject.image.shape[1]))


    def get_max_y(self):
        return (self.min_y + (self.imageObject.image.shape[0]))

    def __eq__(self, other):

        return (isinstance(other, ImageObjectWithPosition) and self.has_same_location(other) and self.is_same_object(other))

# ====================================================
#####################################################
#   To assist with finding the objects that have swapped locations:
class ImagePointForSwapActionRectangle:
    def __init__(self, x, y, is_max_x, is_max_y):
        self.x= x
        self.y =y
        self.is_max_x= is_max_x
        self.is_max_y= is_max_y

    def get_width_including_point(self, x, current_width):
        return self.get_length_including_point(x, self.x, current_width, self.is_max_x)

    def set_x_to_width_including_point(self, x):
        self.x = self.set_pos_to_width_including_point(x, self.x, self.is_max_x)

    def does_width_include_point(self, x, current_width):
        return self.does_length_include_point(x, self.x, current_width, self.is_max_x)

    def get_height_including_point(self, y, current_height):
        return self.get_length_including_point(y, self.y, current_height, self.is_max_y)

    def set_y_to_height_including_point(self, y):
        self.y = self.set_pos_to_width_including_point(y, self.y, self.is_max_y)

    def does_height_include_point(self, y, current_height):
        return self.does_length_include_point(y, self.y, current_height, self.is_max_y)

    def does_length_include_point(self, x, own_x, current_width, is_max):
        if (is_max):
            if (own_x < x or (x < (own_x - current_width) )):
                return False
        else:
            if (own_x > x or (x > (own_x + current_width))):
                return False
        return True

    def get_length_including_point(self, x, own_x, current_width, is_max):
        if (is_max):
            if (own_x >= x):
                return (own_x - x)
            else:
                return (current_width + (x - own_x))
        else:
            if (own_x <= x):
                return (x - own_x)
            else:
                return (current_width + (own_x - x))

    def set_pos_to_width_including_point(self, x, own_x, is_max):
        if (is_max):
            if (own_x < x):
                return x
        else:
            if (own_x > x):
                return x
        return own_x


    def is_point_in_rect_with_width_height(self, x, y, width, height):
        if (self.is_max_x): # by this point both the x,y should be the max if this point is the top right
            if ((x < (self.x - width)) or (y < (self.y - height))):
                return False
        else:
            if ((x > (self.x + width)) or (y > (self.y + height))):
                return False
        return True

    def __str__(self):
        return "(x:=" + str(self.x) + ", y:=" + str(self.y) + ")"


#======================================================

class ImageArea:
    def __init__(self, min_x=-1, min_y=-1, max_x=-1, max_y=-1, is_width_height=True):
        self.min_x = sys.maxsize #if min_x == -1 else self.min_x = min_x
        self.min_y = sys.maxsize
        self.max_x = 0
        self.max_y = 0
        if (is_width_height):
            self.add_position_values_from_width_height(min_x, min_y, max_x, max_y)
        else:
            self.set_position_values(min_x, min_y, max_x, max_y)

    def set_position_values(self, min_x, min_y, max_x, max_y):
        if min_x < max_x:
            self.min_x = min(self.min_x, min_x)
            self.max_x = max(self.max_x, max_x)
        else:
            self.min_x = min(self.min_x, max_x)
            self.max_x = max(self.max_x, min_x)
        if min_y < max_y:
            self.min_y = min(self.min_y, min_y)
            self.max_y = max(self.max_y, max_y)
        else:
            self.min_y = min(self.min_y, max_y)
            self.max_y = max(self.max_y, min_y)
        self.calculate_center()

    def add_position_values_from_width_height(self, x, y, w, h):
        self.min_x = min(self.min_x, x)
        self.min_y = min(self.min_y, y)
        self.max_x = max(self.max_x, x + w)
        self.max_y = max(self.max_y, y + h)
        self.calculate_center()

    def set_width_height_keep_center(self, w, h, image_width, image_height):
        print ("w:=" + str(self.get_width()) + ", h:=" + str(self.get_height()))
        width_difference = (self.max_x - self.min_x) - w
        self.min_x = self.min_x + (width_difference/2)
        if (self.min_x < 0):
            self.min_x = 0
        height_difference = (self.max_y - self.min_y) - h
        self.min_y = self.min_y + (height_difference/2)
        if (self.min_y < 0):
            self.min_y = 0
        self.max_x = self.min_x + w
        if (self.max_x+1 > image_width):
            self.min_x = self.min_x - (self.max_x+1 - image_width)
            self.max_x = self.min_x + w
        self.max_y = self.min_y + h
        if (self.max_y+1 > image_height):
            self.min_y = self.min_y - (self.max_y+1 - image_height)
            self.max_y = self.min_y + h

    def calculate_center(self):
        self.center_x = self.min_x + ((self.max_x-self.min_x)/2)
        self.center_y = self.min_y + ((self.max_y-self.min_y)/2)

    def get_size(self):
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)

    def get_width_height(self):
        return (self.get_width(), self.get_height())

    def get_width(self):
        return (self.max_x - self.min_x)

    def get_height(self):
        return (self.max_y - self.min_y)

    def get_distance_between_centers(self, x, y, w, h):
        return np.sqrt((self.center_x - (x + (w / 2))) ** 2 + (self.center_y - (y + (h / 2))) ** 2)

    def get_positions(self):
        return (int(self.min_x), int(self.min_y)), (int(self.max_x), int(self.max_y))

    def __str__(self):
        return "[lower: x:=" + str(self.min_x) + ", y:=" + str(self.min_y) + "; upper: x:=" + str(self.max_x) + ", y:="\
               + str(self.max_y) + "; size: w:=" + str(self.get_width()) + ", h:=" + str(self.get_height()) + "]"


#=======================================================================================================
#=======================================================================================================