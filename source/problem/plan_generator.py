import cv2
import numpy as np

from definitions import object_definitions, grounded_state
from problem import fast_downward

DEBUG_PLAN_GENERATION = True#False

# --------------------------------------------

def generate_plan(domain, problem):
    plan_with_string_actions, time = fast_downward.run_planner(domain, problem)
    print("Plan: " + str(plan_with_string_actions))
    plan = Plan(domain, problem, plan_with_string_actions)
    plan.set_all_actions_definitions()
    plan.create_image_sequence()

    debug_show_image_sequence(plan, problem)


#======================================================

class Plan:
    def __init__(self, domain, problem, plan_with_string_actions):
        self.plan = []
        self.parse_plan(plan_with_string_actions)

        self.domain = domain
        self.problem = problem

    #--------------------------------

    def parse_plan(self, plan_with_string_actions):
        for action_string in plan_with_string_actions:
            self.plan.append(PlannedAction(action_string))

    #--------------------------------

    def set_all_actions_definitions(self):
        for planned_action in self.plan:
            planned_action.find_and_set_definitions(self.domain.defined_actions, self.problem.get_all_object_definitions())

    #--------------------------------

    def create_image_sequence(self):
        pre_image = self.problem.initial_image
        for planned_action in self.plan:
            planned_action.create_and_set_images(pre_image)
            pre_image = planned_action.suc_image

#======================================================

class PlannedAction:
    def __init__(self, action_string):
        action_parts = action_string.strip("()").split()
        self.name = action_parts[0]
        self.params = action_parts[1:]

        self.action_definition = None
        self.param_definitions = []

        self.pre_image = None
        self.suc_image = None

    #--------------------------------------------

    def find_and_set_definitions(self, defined_actions, all_object_definitions):
        self.find_and_set_action_definition(defined_actions)
        self.find_and_set_object_definitions(all_object_definitions)

    #--------------------------------------------

    def find_and_set_action_definition(self, action_definitions):
        for action_definition in action_definitions:
            if action_definition.get_string_id() == self.name:
                self.action_definition = action_definition
                break

    #--------------------------------------------

    def find_and_set_object_definitions(self, all_object_definitions):
        for param in self.params:
            self.param_definitions.append(object_definitions.find_object_definition(all_object_definitions, param))

    #--------------------------------------------

    def create_and_set_images(self, pre_image):
        self.pre_image = pre_image
        self.suc_image = pre_image.copy()
        for effect in self.action_definition.effects: #  apply each effect to self.pre_image to create self.suc_image:
            defined_objects_for_effect = []
            for defined_object_index in effect.defined_objects:
                defined_objects_for_effect.append(self.param_definitions[defined_object_index]) # we used this index when creating the action, so should be ok to use it here

            atom = grounded_state.Atom(effect.predicate, defined_objects_for_effect, effect.negated)
            self.apply_atom_to_suc_image(atom)
            
    #-------------------------------------------

    def apply_atom_to_suc_image(self, atom):
        if ((atom.predicate.name == "at") and (not atom.negated)):
            image_object_definition = atom.defined_objects[0]
            location_definition = atom.defined_objects[1]
            #image_state = location_definition.get_location_state_for_object_image_definition(image_object_definition)

            if (image_object_definition.image_object_area.center_matches):
                min_x = int(location_definition.image_area.get_center_x_location() - (float(image_object_definition.image_object_area.image.shape[1]) / 2.0))   # arrays start from 0, so need -1
                min_y = int(location_definition.image_area.get_center_y_location() - (float(image_object_definition.image_object_area.image.shape[0]) / 2.0))
            else:
                min_x = location_definition.image_area.min_x - image_object_definition.image_object_area.location_min_x_offset
                min_y = location_definition.image_area.min_y - image_object_definition.image_object_area.location_min_y_offset

            max_x = min_x + image_object_definition.image_object_area.image.shape[1]
            max_y = min_y + image_object_definition.image_object_area.image.shape[0]

            #  remove this line:
            #self.suc_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1] = location_definition.clear_state #image_state

            self.suc_image[min_y:max_y, min_x:max_x] = image_object_definition.image_object_area.image # uses image.shape, so +1 is not needed.???
        elif ((atom.predicate.name == "clear") and (not atom.negated)):
            location_definition = atom.defined_objects[0]
            self.suc_image[location_definition.image_area.min_y:location_definition.image_area.max_y+1, location_definition.image_area.min_x:location_definition.image_area.max_x+1] = location_definition.clear_state
       # else:
           # print("atom is false")


#======================================================


#------------------------------
# debug methods:

def debug_show_image_sequence(plan, problem):
    if (not DEBUG_PLAN_GENERATION):
        return
    index = 0
    for action in plan.plan:
        cv2.imshow('PLANNED STATE '+str(index), np.uint8(action.suc_image))
        index = index + 1

    cv2.imshow('INITIAL STATE ', np.uint8(problem.initial_image))
    cv2.imshow('GOAL STATE ', np.uint8(problem.goal_image))


#==================================================================
#==================================================================

