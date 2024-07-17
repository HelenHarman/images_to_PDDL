import sys
import cv2
import numpy as np

from image_handling import image_area_of_transitions, image_object, util

DEBUG_TRANSITIONS = False#True

# ======================================================================

class ChangeImageObjectArea:
    # ImageObjectArea, ImageObjectArea
    def __init__(self, from_image_object, to_image_object):
        self.from_image_object = from_image_object
        self.to_image_object = to_image_object

# ======================================================================
class Transition:
    def __init__(self, pre_image, suc_image, image_diff):
        self.pre_image = pre_image
        self.suc_image = suc_image
        self.image_diff = image_diff #np.int32(pre_image) - np.int32(suc_image) # np.int32 makes sure negative and positive values are in image
        self.changed_area = self.create_changed_area()
        self.image_areas = []
        self.changed_object_image_areas = [] # cropped to the (potential) object. - will also contain the locations
        self.changed_image_areas = []
        #changed_image_area

    #--------------------------------------------------

    def does_change_overlapping(self, other):
        image_diff = self.image_diff.get_image()
        other_image_diff = other.image_diff.get_image()
        if self.changed_area.is_overlapping(other.changed_area):
            for x in range(self.changed_area.min_x, self.changed_area.max_x):
                for y in range(self.changed_area.min_y, self.changed_area.max_y):
                    #if self.image_diff[y, x][0] != 0 and other.image_diff[y, x][0] != 0:  # TODO rather than just using 0 we should check each image channel
                    if image_diff[y, x] != 0 and other_image_diff[y, x] != 0:  # TODO rather than just using 0 we should check each image channel
                        return True
        return False #return self.changed_area.is_overlapping(other.changed_area)

    #--------------------------------------------------
    """
    def add_image_area_of_overlap(self, image_area):
        self.image_areas.append(image_area)
        return True
        print(str(image_area))
        found_overlap_index = -1
        for i in range(len(self.image_areas)):
            if self.image_areas[i].is_overlapping(image_area):
                if found_overlap_index != -1:
                    print("don't add")
                    return False
                found_overlap_index = i
        if (found_overlap_index == -1):
            self.image_areas.append(image_area)
        elif (self.get_total_image_area() < self.get_total_image_area(self.image_areas[found_overlap_index], image_area)):
            self.image_areas[found_overlap_index] = image_area
        else:
            print("don't add")
        return True
    """

    def add_image_area_of_overlap_completed(self, image_area):
        found_overlap_index = -1
        for i in range(len(self.image_areas)):
            if self.image_areas[i].is_overlapping(image_area):
                if found_overlap_index != -1:
                    return False
                found_overlap_index = i
        if (found_overlap_index == -1):
            self.image_areas.append(image_area)
        elif (self.get_total_image_area() < self.get_total_image_area(self.image_areas[found_overlap_index], image_area)):
            self.image_areas[found_overlap_index] = image_area
        return True

    #--------------------------------------------------

    def get_total_image_area(self, replace=None, replacement=None):
        total_area = 0
        for image_area in self.image_areas:
            if ((replace != None) and (image_area == replace)):
                total_area = total_area + replacement.get_area()
            else:
                total_area = total_area + image_area.get_area()
        return total_area

    #--------------------------------------------------

    def create_changed_image_areas_list(self):
        for image_area in self.image_areas:
            cropped_image_area = self.create_changed_area(image_area.min_x, image_area.min_y, image_area.max_x, image_area.max_y)

            if cropped_image_area.max_x != -1:
                if (cropped_image_area.get_center() == image_area.get_center()):
                    from_image_area = image_object.ImageObjectArea(cropped_image_area.crop_image(self.pre_image.get_image()), cropped_image_area,  0,0, True)
                    to_image_area = image_object.ImageObjectArea(cropped_image_area.crop_image(self.suc_image.get_image()), cropped_image_area, 0, 0, True)
                else:
                    x_diff = image_area.min_x - cropped_image_area.min_x
                    y_diff = image_area.min_y - cropped_image_area.min_y
                    from_image_area = image_object.ImageObjectArea(cropped_image_area.crop_image(self.pre_image.get_image()), cropped_image_area, x_diff, y_diff, False)
                    to_image_area = image_object.ImageObjectArea(cropped_image_area.crop_image(self.suc_image.get_image()), cropped_image_area, x_diff, y_diff, False)

                self.changed_object_image_areas.append(ChangeImageObjectArea(from_image_area, to_image_area))#cropped_image_area)
                self.changed_image_areas.append(image_area)

    #-------------------

    def does_transition_modify_area(self, image_area):
        for changed_object_image_area in self.changed_object_image_areas:
            if image_area.is_overlapping(changed_object_image_area.from_image_object.changed_image_area_of_transition):
                return True

        if (not self.changed_object_image_areas):
            return util.has_non_zero_pixels(image_area.crop_image(self.image_diff.get_image()))

        return False

    #-------------------

    def create_changed_area(self, start_min_x=0, start_min_y=0, start_max_x=-1, start_max_y=-1, image_diff_other=None, use_image_diff_other=False): #image_diff

        image_diff = self.image_diff.get_image()
        if use_image_diff_other:
            image_diff_other_img = image_diff_other.get_image()
        min_x = (sys.maxsize, 0)
        min_y = (0, sys.maxsize)
        max_x = (-1, 0)
        max_y = (0, -1)
        if (start_max_x == -1 and start_max_y == -1):
            start_max_x = image_diff.shape[1]
            start_max_y = image_diff.shape[0]
        else:
            start_max_x = start_max_x + 1
            start_max_y = start_max_y + 1

        for x in range(start_min_x, start_max_x):
            for y in range(start_min_y, start_max_y):
                #if (self.image_diff[y, x][0] != 0 and ((not use_image_diff_other) or (image_diff_other[y, x][0] != 0))):  # TODO rather than just using 0 we should check each image channel
                if(image_diff[y, x] != 0 and ((not use_image_diff_other) or (image_diff_other_img[y, x] != 0))):  # TODO rather than just using 0 we should check each image channel
                    if (x < min_x[0]):
                        min_x = (x, y)
                    if (y < min_y[1]):
                        min_y = (x, y)
                    if (x > max_x[0]):
                        max_x = (x, y)
                    if (y > max_y[1]):
                        max_y = (x, y)

        return image_area_of_transitions.ImageArea(min_x, min_y, max_x, max_y)



#================================================
#=== DEBUG
def debug_show_all_image_areas_for_transition(transitions):
    if (not DEBUG_TRANSITIONS):
        return
    transition = transitions[0]
    image = transition.pre_image.get_image().copy()

    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            image[y, x] = 255#(255,255,255)

    for image_area in transition.image_areas:
        cv2.rectangle(image, (image_area.min_x, image_area.min_y), (image_area.max_x, image_area.max_y),  150,1) #(255, 0, 0),
    #--for changed_object_image_area in transition.changed_object_image_areas:
    #--    cv2.rectangle(image, (changed_object_image_area.from_image_object.changed_image_area_of_transition.min_x, changed_object_image_area.from_image_object.changed_image_area_of_transition.min_y), (changed_object_image_area.from_image_object.changed_image_area_of_transition.max_x, changed_object_image_area.from_image_object.changed_image_area_of_transition.max_y), (0, 255, 0), 1)
   # cv2.imshow('image transition', np.uint8(image))
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
#================================================

#===========================================================================================
#===========================================================================================

