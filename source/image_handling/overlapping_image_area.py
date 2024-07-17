import cv2
import numpy as np

from image_handling import image_area_of_transitions

DEBUG_OVERLAPPING_IMAGE_AREA = False #True



#======================================================================

class OverlappingTransitions:
    def __init__(self, initial_overlap, transition=None):
        self.transitions = []
        self.overlap = image_area_of_transitions.ImageArea(initial_overlap.min_x, initial_overlap.min_y, initial_overlap.max_x, initial_overlap.max_y)
        if (transition != None):
            self.transitions.append(transition)

    #--------------------------------------------------

    def update_overlapping_area(self, transition): #, all_overlapping_transitions=[], create_overlapping_transactions=False):
        #if transition in self.transitions:
        #    return
        image_area = self.transitions[0].create_changed_area(self.overlap.min_x, self.overlap.min_y, self.overlap.max_x, self.overlap.max_y, transition.image_diff, True) #self.transitions[0].image_diff,
        self.overlap = image_area
        self.transitions.append(transition)

    #--------------------------------------------------

    def get_area(self):
        return self.overlap.get_area()

    def __eq__(self, other):
        if (isinstance(other, image_area_of_transitions.ImageArea)):
            return (self.overlap == other)
        else:
            return (isinstance(other, OverlappingTransitions) and (self.overlap == other.overlap))

    #--------------------------------------------------
#======================================================================
#===== DEBUG
def debug_show_overlap(overlapping_transitions):
    if (not DEBUG_OVERLAPPING_IMAGE_AREA):
        return
    index = 0
    for transition in overlapping_transitions.transitions:
        image = transition.pre_image.copy()
        cv2.rectangle(image, (overlapping_transitions.overlap.min_x, overlapping_transitions.overlap.min_y),
                      (overlapping_transitions.overlap.max_x, overlapping_transitions.overlap.max_y), 150, 1) #(255, 0, 0)
        cv2.imshow('image' + str(index), np.uint8(image))
        index = index + 1

#======================================================================
#======================================================================







