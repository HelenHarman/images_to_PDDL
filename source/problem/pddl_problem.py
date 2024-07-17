import cv2

from definitions import create_grounded_state, grounded_state

#----------------------------------------

class Problem:
    def __init__(self, location_definitions, image_object_definitions, initial_state_image_file, goal_state_image_file):
        self.location_definitions = location_definitions # STATIC
        self.image_object_definitions = image_object_definitions # STATIC

        if (isinstance(initial_state_image_file, str)):
            self.initial_image = cv2.imread(initial_state_image_file)
            self.goal_image = cv2.imread(goal_state_image_file)
        else:
            self.initial_image = initial_state_image_file
            self.goal_image = goal_state_image_file

        self.grounded_initial_state = None
        self.grounded_goal_state = None

        self.create_pddl_problem_definition(location_definitions, image_object_definitions)

    # ----------------------------------------

    def create_pddl_problem_definition(self, location_definitions, image_object_definitions):
        self.grounded_initial_state = self.create_grounded_state_for_image(self.initial_image, location_definitions, image_object_definitions)
        self.grounded_goal_state = self.create_grounded_state_for_image(self.goal_image, location_definitions, image_object_definitions)

    #----------------------------------------

    def create_grounded_state_for_image(self, image, location_definitions, image_object_definitions):
        state = grounded_state.GroundedState() # note, static atoms will be be automatically added
        for location_definition in location_definitions:
            image_object_definition = create_grounded_state.get_image_object_at_location(image, location_definition, image_object_definitions)
            create_grounded_state.add_location_and_image_object_to_state(state, location_definition, image_object_definition)
        return state

    #----------------------------------------

    def get_all_object_definitions(self):
        object_definitions = self.location_definitions.copy()
        object_definitions.extend(self.image_object_definitions)
        return object_definitions

    #----------------------------------------

    def __str__(self):
        problem_string = "(define (problem generated_problem)\n"
        problem_string = problem_string + "(:domain generated_domain) \n"
        # objects:
        problem_string = problem_string + " (:objects \n"
        for location_definition in self.location_definitions:
            problem_string = problem_string + location_definition.get_string_id()+ " - " + location_definition.get_type() + " \n  "
        for image_object_definition in self.image_object_definitions:
            problem_string = problem_string + image_object_definition.get_string_id()+ " - " + image_object_definition.get_type() + " \n  "
        #problem_string = problem_string + object_definitions.dummy_object_definition.get_string_id() + " - " + object_definitions.dummy_object_definition.get_type() + " \n  "


        problem_string = problem_string + ")\n" # end of objects
        # initial state:
        problem_string = problem_string + " (:init \n" + str(self.grounded_initial_state) + ")\n"
        # goal state:
        problem_string = problem_string + " (:goal (and \n" #+ str(self.grounded_goal_state) + ")\n"
        for atom in self.grounded_goal_state.fluent_atoms:
            problem_string = problem_string + str(atom) + "\n"
        problem_string = problem_string + ") )\n"# end of goal

        problem_string = problem_string + ")" # end of problem
        #print(problem_string)

        return problem_string


#=================================================================================
#=================================================================================