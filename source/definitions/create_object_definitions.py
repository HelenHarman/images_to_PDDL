import cv2
import numpy as np

from definitions import object_definitions
from definitions.object_definitions import LocationDefinition, ImageObjectDefinition
from image_handling import util

DEBUG_CREATE_OBJECT_DEFINITIONS = False #True

#-----------------------------

def create_object_and_location_definitions(image_areas, transitions):
    location_definitions = create_location_definitions(image_areas, transitions)
    image_object_definitions = create_image_definitions(transitions, location_definitions)

    print("Total number of location_definitions = " + str(len(location_definitions)))
    print("Total number of image_object_definitions = " + str(len(image_object_definitions)))
    debug_show_image_object_definitions(image_object_definitions)

    return location_definitions, image_object_definitions

#==========================================================================#
#               CREATE LOCATION DEFINITIONS

def create_location_definitions(image_areas, transitions):
    location_definitions = []
    for image_area in image_areas:
        location_definition = LocationDefinition(image_area)
        # add each state the location has in the transitions to the location_definition
        for transition in transitions:
            location_state = image_area.crop_image(transition.pre_image.get_image()) #transition.pre_image[image_area.min_y:image_area.max_y+1, image_area.min_x:image_area.max_x+1]  # img[y:y+h, x:x+w]
            location_definition.insert_image_state(location_state)
            location_state = image_area.crop_image(transition.suc_image.get_image()) #transition.suc_image[image_area.min_y:image_area.max_y+1, image_area.min_x:image_area.max_x+1]
            location_definition.insert_image_state(location_state)

        location_definitions.append(location_definition)
    location_definitions = initial_clear_state_for_locations(transitions, location_definitions)
    return location_definitions

#------------------------------------

def initial_clear_state_for_locations(transitions, location_definitions):
    clear_states = []
    for location_definition in location_definitions:
        progress = 0 # 0 = start; 1 = first transition that changes location found; 2 = state1 is matching; 3 = state2 is matching; 4 no state match
        state1 = None
        state2 = None
        for transition in transitions:
            if transition.does_transition_modify_area(location_definition.image_area):
                #print("true transition.does_transition_modify_area(location_definition.image_area)")
                if (progress == 0):
                    state1 = location_definition.image_area.crop_image(transition.pre_image.get_image()) #[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                    state2 = location_definition.image_area.crop_image(transition.suc_image.get_image()) #transition.suc_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                    progress = 1
                    #print("true progress =1")
                elif (progress >= 1):
                    other_state1 = location_definition.image_area.crop_image(transition.pre_image.get_image()) #transition.pre_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                    other_state2 = location_definition.image_area.crop_image(transition.suc_image.get_image()) #transition.suc_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
                    if ((progress == 1) and (util.are_images_equal(state1, other_state1) or util.are_images_equal(state1, other_state2))
                                        and (util.are_images_equal(state2, other_state1) or util.are_images_equal(state2, other_state2))):
                        progress = 1
                        #print("true progress =1")
                    elif ((progress == 1 or progress == 2) and (util.are_images_equal(state1, other_state1) or util.are_images_equal(state1, other_state2))):
                        progress = 2
                        #print("true progress =2")
                    elif ((progress == 1 or progress == 3) and (util.are_images_equal(state2, other_state1) or util.are_images_equal(state2, other_state2))):
                        progress = 3
                        #print("true progress =3")
                    else:
                        #print("true progress =4")
                        #cv2.imshow('other_state1 progress =4', np.uint8(other_state1))
                        #cv2.imshow('other_state2 progress =4', np.uint8(other_state2))
                        progress = 4
                        break
        if (progress == 2 ): # TODO what about progress == 1??
            location_definition.set_clear_state(state1)
           # print("location is clear")
            clear_states.append(state1)
        elif (progress == 3):
            location_definition.set_clear_state(state2)
            #print("location is clear")
            clear_states.append(state2)
       # else:
          #  print("location is NOT clear")

    #print("set missed: ")
    #-----------------
    # To handle, e.g., lights-out and top blocks in ToH, in which a location is in one of 2 states, we select one of these states as the clear state.
    for location_definition in location_definitions:
        #print("location_definition.always_from_or_to_clear= " + str(location_definition.always_from_or_to_clear) + "  location_definition.image_states = " + str(len(location_definition.image_states)))
        if ((not location_definition.always_from_or_to_clear) and (len(location_definition.image_states) == 2)):
            #print (location_definition.get_string_id())
            if (not clear_states):
                clear_states.append(location_definition.image_states[0])
                location_definition.set_clear_state(location_definition.image_states[0])
            else:
                for clear_state in clear_states:  # if we have already found a clear state we want the same clear state for all locations:
                    if util.are_mean_value_of_images_equal(clear_state, location_definition.image_states[0]): # TODO are_mean_value_of_images_equal shouldn't be used. i.e., perform a better comparison on different sized images. e.g., for noisy lights-out problem
                        location_definition.set_clear_state(location_definition.image_states[0])
                        #print("missed location is clear")
                        #cv2.imshow('image clear' + location_definition.get_string_id(), np.uint8(location_definition.image_states[0]))
                        break
                    elif util.are_mean_value_of_images_equal(clear_state, location_definition.image_states[1]):
                        location_definition.set_clear_state(location_definition.image_states[1])
                        #print("missed location is clear")
                       # cv2.imshow('image clear' + location_definition.get_string_id(), np.uint8(location_definition.image_states[1]))
                        break
    #----------------
    return location_definitions

#---------------------------------------------------

#==========================================================================#
#              CREATE IMAGE OBJECT DEFINITIONS

def create_image_definitions(transitions, location_definitions):
    image_object_definitions = []
    # Each transactions has a list of areas that have changed state, we want to transform each of those areas in to an image_object_definition.
    #   We don't add "clear" objects to list of image_objects.
    for transition in transitions:
        for changed_object_image_area in transition.changed_object_image_areas:
            # changed_object_image_area changed from:
            if ( (not object_definitions.is_image_object_area_in_image_obj_def_list(changed_object_image_area.from_image_object, image_object_definitions) )
                    and (not is_clear_state(location_definitions, changed_object_image_area.from_image_object, transition.pre_image.get_image()))):
                image_object_definitions.append(ImageObjectDefinition(changed_object_image_area.from_image_object))

            # changed_object_image_area changed too:
            if ((not object_definitions.is_image_object_area_in_image_obj_def_list(changed_object_image_area.to_image_object, image_object_definitions))
                    and (not is_clear_state(location_definitions, changed_object_image_area.to_image_object, transition.suc_image.get_image()))):
                image_object_definitions.append(ImageObjectDefinition(changed_object_image_area.to_image_object))

    image_object_definitions.sort(key= lambda x: x.image_object_area.get_area(), reverse=True) # Temp FIX: for ToH smallest object matching all occupied locations, so check from biggest to smallest

    # In some domains (e.g., ToH, puzzle- due to the cropping area changed pixels) the image_object definitions are
    #   smaller than the location, so we create a map from the object_definition to the location's full state when it has that object_definition:
    for location_definition in location_definitions:
        location_definition.create_image_object_definition_to_image_state_map(image_object_definitions)

    return image_object_definitions

#------------------------------------------

def is_clear_state(location_definitions, image_object_area, image):
    for location_definition in location_definitions:
        if (not location_definition.always_from_or_to_clear):
            continue
        if location_definition.image_area.is_overlapping(image_object_area.changed_image_area_of_transition):
            state1 = location_definition.image_area.crop_image(image) #image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1]
            if util.are_images_equal(state1, location_definition.clear_state):
                return True
            else:
                return False
    return False

    # -----------------------------------------------------------------------

#==========================
# debug methods:

def debug_show_image_object_definitions(image_object_definitions):
    if (not DEBUG_CREATE_OBJECT_DEFINITIONS):
        return
    index = 0
    for image_object_definition in image_object_definitions:
        cv2.imshow('image' + str(index), np.uint8(image_object_definition.image_object_area.image))
        index = index + 1
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# ==========================


#==========================================================================
# ==========================================================================


#--- scratch notes
    # : create action node with PDDL (before and after) - states that change. (we can get clear/unclear from the list of locations in the transaction)
#  do the build action graph and get state of previous objects (not needed for clear/unclear actions)
#  build state dependency graph : x dep on z and c, and x dep on c, so we don't need to know x dep on c
#       start with full state as precondition and remove unwanted states. (Don't forget to add links for locations that can change state at the same time - but for ToH this is unwanted)
    """
                  dep
         or              ActionNode  
child-per precondition 
"""