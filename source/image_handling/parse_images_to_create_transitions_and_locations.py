
import cv2, os
import numpy as np

import image_handling
from generate_images import image_pairs
from image_handling import overlapping_image_area as oImgA, image_area_of_transitions
from image_handling.transition import Transition

#--------------------------------------------

def parse_images(image_pairs_iter, return_all_areas = False): #, create_images=False
    transitions = create_transactions(image_pairs_iter)
   # if create_images:
   # else:
    #    transitions = read_in_transactions(image_directory)
    transitions, all_image_areas = find_all_locations(transitions, return_all_areas)


    image_handling.transition.debug_show_all_image_areas_for_transition(transitions)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return transitions, all_image_areas

#===================================================================================
# Parse images using the overlapping image areas:

def create_transactions(image_pairs_iter): # does the same as read_in_transactions, but creates images, rather than reading them from file.
    transitions = []
    while image_pairs_iter.has_next():
        pre_image, suc_image = image_pairs_iter.get_next()
        image_diff = image_pairs.ImageState("diff"+ pre_image.key + suc_image.key, np.int32(pre_image.get_image()) - np.int32(suc_image.get_image()))
        transition = Transition(pre_image, suc_image, image_diff)
        transitions.append(transition)
        """
        cv2.imshow("transition pre", np.uint8(transition.pre_image.get_image()))
        cv2.imshow("transition suc", np.uint8(transition.suc_image.get_image()))
        image_diff = transition.image_diff.get_image().copy()
        for y in range(image_diff.shape[0]):
            for x in range(image_diff.shape[1]):
                if (image_diff[y, x] < 0):
                    image_diff[y, x] = 50
                elif (image_diff[y, x] != 0):
                    image_diff[y, x] = 150
                else:
                    image_diff[y, x] = 255
        cv2.imshow("image_diff " , np.uint8(image_diff))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        """
        """
        cv2.imshow("pre_image " , np.uint8(pre_image))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        """
    print("Number of provided transitions = " +  str(len(transitions)))
    return transitions

#--------------------------------------------

def get_transitions_that_modify_different_areas(transitions):
    modify_diff_area = []
    for transition in transitions:
        if (not modify_diff_area):
            modify_diff_area.append(transition)
        else:
            transition_image = transition.image_diff.get_image()
            matches = True
            for mod in modify_diff_area:
                matches = True
                mod_transition_image = mod.image_diff.get_image()
                for x in range(transition_image.shape[1]):
                    for y in range(transition_image.shape[0]):
                        if (((transition_image[y, x] != 0) and (mod_transition_image[y, x] == 0)) or ((transition_image[y, x] == 0) and (mod_transition_image[y, x] != 0))):
                            matches = False
                if (matches):
                    break
            if (not matches):
                modify_diff_area.append(transition)
    return modify_diff_area

def find_all_locations(transitions, return_all_areas = False):
    #all_image_areas = []
    transitions_that_mod_diff_area = get_transitions_that_modify_different_areas(transitions)
    print("transitions_that_mod_diff_area=" + str(len(transitions_that_mod_diff_area)))
    overlapping_image_areas = []
    transitions_changed_area_overlap = []

    for transition in transitions_that_mod_diff_area: # TODO speed this up!
        for overlapping in overlapping_image_areas:
            if (overlapping.overlap.is_overlapping(transition.changed_area)):
                overlapping_transitions = oImgA.OverlappingTransitions(transition.changed_area, transition)
                for transition2 in overlapping.transitions:
                    before_area = overlapping_transitions.overlap
                    before_transitions = overlapping_transitions.transitions.copy()
                    overlapping_transitions.update_overlapping_area(transition2)
                    if (overlapping_transitions.overlap.max_x == -1):
                        overlapping_transitions = oImgA.OverlappingTransitions(before_area)
                        overlapping_transitions.transitions = before_transitions
                        break
                if (overlapping_transitions.overlap.max_x != -1):
                    if (overlapping_transitions not in overlapping_image_areas):
                        overlapping_image_areas.append(overlapping_transitions)
                    else: #print (overlapping_transitions.overlap)
                        overlapping_image_areas[overlapping_image_areas.index(overlapping_transitions)].transitions.append(transition)
        #print(len(overlapping_image_areas))

        #found = image_area_of_transitions.find_image_area_using_pos(transitions_changed_area_overlap, transition.changed_area)
        #if (found == None): #<-- commented out lines where added to optimise code, but they risk making the code fail for some problems, so removed.... clear areas are too small on ToH with this code
        overlapping_image_areas.append(oImgA.OverlappingTransitions(transition.changed_area, transition))
            #transitions_changed_area_overlap.append(transition.changed_area)

    if (return_all_areas):
        image_areas = []
        for overlapping_image_area in overlapping_image_areas:
            image_areas.append(overlapping_image_area.overlap)
        return transitions, image_areas

    # When there are missing transitions, some images changed areas will not be cropped to the objects.
    #   Therefore, we loop over all image areas (i.e., locations) and remove the overlaps (but keep the largest non-overlapping images)
    #print(len(all_image_areas))
    #black_image = np.zeros((transitions[0].pre_image.shape[0], transitions[0].pre_image.shape[1], 3), np.uint8)
    image = transitions[0].pre_image.get_image()
    black_image = np.zeros((image.shape[0], image.shape[1]), np.uint8)
    #white_image = np.full((transitions[0].pre_image.shape[0], transitions[0].pre_image.shape[1], 3), (255,255,255), np.uint8)
    white_image = np.full((image.shape[0], image.shape[1]), 255, np.uint8)
    image_diff = image_pairs.ImageState("diff", black_image - white_image, True)
    dummy_transition = Transition(white_image, black_image, image_diff)
    #all_image_areas\
    overlapping_image_areas.sort(key=lambda x: x.overlap.get_area())
    #print("dummy_transition.add_image_area_of_overlap")
    for overlapping_image_area in overlapping_image_areas:
       # print(overlapping_image_area.overlap)
        dummy_transition.add_image_area_of_overlap_completed(overlapping_image_area.overlap)
    all_image_areas = dummy_transition.image_areas
    #print(len(all_image_areas))
    #for image_area in all_image_areas:
     #   print (image_area)

    # label transactions with locations.
    for transaction in transitions:
        transaction.image_areas = all_image_areas
        transaction.create_changed_image_areas_list()

    return transitions, all_image_areas

#------------------------------------------------------------------
#------------------------------------------------------------------

def read_in_transactions(image_directory): # unused - as we new use generate_images/image_pairs.py
    transitions = []
    for file in os.listdir(image_directory):
        if "pre.png" not in file: # if "suc.png" in file :
            continue
        pre_image_file = image_directory + file
        suc_image_file = image_directory + file.replace("pre.png", "suc.png")

        pre_image = cv2.imread(pre_image_file)
        suc_image = cv2.imread(suc_image_file)

        transition = Transition(pre_image, suc_image)

        """
        image_diff = transition.image_diff.copy()
        if "235_pre.png" == file or "7_pre.png" == file or "0_pre.png" == file or "222_pre.png" == file:
            for y in range(image_diff.shape[0]):
                for x in range(image_diff.shape[1]):
                    if (image_diff[y, x][0] < 0):
                        image_diff[y, x] = (50, 50, 255)
                    elif (image_diff[y, x][0] != 0):
                        image_diff[y, x] = (50, 255, 50)
                    else:
                        image_diff[y, x] = (255, 255, 255)
            cv2.imshow("image_diff " + file, np.uint8(image_diff))
        """
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()


        transitions.append(transition)

    print("Number of provided transitions = " +  str(len(transitions)))
    return transitions
""" PAIR version:
def find_all_locations(transitions):
    all_image_areas = []

    for transition in transitions: # TODO speed this up!
        overlapping_transitions_for_transition = []
        for transition2 in transitions:
            if (transition.does_change_overlapping(transition2) and transition != transition2):
               
                overlapping_transitions = overlapping_image_area.OverlappingTransitions(transition.changed_area, transition)
                overlapping_transitions.update_overlapping_area(transition2)
                overlapping_transitions_for_transition.append(overlapping_transitions)

        overlapping_transitions_for_transition.sort(key=lambda x: x.get_area())
        for overlapping_transitions in overlapping_transitions_for_transition:
            transition.add_image_area_of_overlap(overlapping_transitions.overlap)

        for image_area in transition.image_areas:
            if image_area not in all_image_areas:
                all_image_areas.append(image_area)

        #print("overlapping_transitions_for_transition=" + str(len(overlapping_transitions_for_transition)))
        #print("transition.image_areas=" + str(len(transition.image_areas)))

    # When there are missing transitions, some images changed areas will not be cropped to the objects.
    #   Therefore, we loop over all image areas (i.e., locations) and remove the overlaps (but keep the largest non-overlapping images)
    #print(len(all_image_areas))
    black_image = np.zeros((transitions[0].pre_image.shape[0], transitions[0].pre_image.shape[1], 3), np.uint8)
    white_image = np.full((transitions[0].pre_image.shape[0], transitions[0].pre_image.shape[1], 3), (255,255,255), np.uint8)
    dummy_transition = Transition(white_image, black_image)
    all_image_areas.sort(key=lambda x: x.get_area())
    print("dummy_transition.add_image_area_of_overlap")
    for image_area in all_image_areas:
        #print (image_area)
        dummy_transition.add_image_area_of_overlap_completed(image_area)
    all_image_areas = dummy_transition.image_areas
    #print(len(all_image_areas))
    #for image_area in all_image_areas:
    #    print (image_area)


    # label transactions with locations.
    for transaction in transitions:
        transaction.image_areas = all_image_areas
        transaction.create_changed_image_areas_list()

    return transitions, all_image_areas
"""
#===================================================================================
#===================================================================================


