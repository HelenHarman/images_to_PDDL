import os
import time

import cv2
import numpy as np

from action_graph import create_action_graph
from definitions import create_object_definitions, create_action_definitions, domain_definition, object_definitions, \
    grounded_state
from definitions.grounded_state import GroundedState
from generate_images import image_pairs, handle_data
from image_handling import parse_images_to_create_transitions_and_locations as image_parsing
from precreated_domain import object_and_state_generation
from problem import pddl_problem, fast_downward, plan_generator

domain_names={"toh"    : [{"blocks":2, "towers":3},{"blocks":3, "towers":3}, {"blocks":4, "towers":3}, {"blocks":5, "towers":3}],
              "lights" : [{"size":2}], #---,{"size":3}
              "spider" : [{"width":2,"height":2}],
              "mandrill" : [{"width":2,"height":2}],
              "digital" : [{"width":2,"height":2}]} #---,{"width":3,"height":3}
#,{"width":4,"height":4}{"width":2,"height":2},

#domain_names_with_option_for_precreating_action_defs={"toh"    : {"blocks":3, "towers":3},"lights" : {"size":3},"spider" : {"width":2,"height":2}}

domain_names_with_option_for_precreating_action_defs={ "digital" : {"create":{"width":2,"height":2}, "test":[{"width":2,"height":2},{"width":3,"height":3}], "domains":["spider","mandrill","digital"]}, #,{"width":4,"height":4}
                                                       "toh": {"create": {"blocks": 3, "towers": 3}, "test": [{"blocks": 4, "towers": 3}, {"blocks": 5, "towers": 3}]}, #{"blocks": 4, "towers": 3},{"blocks": 3, "towers": 3} {"blocks": 2, "towers": 3},
                                                       "lights" : {"create":{"size":3}, "test":[{"size":4},{"size":2}]}
                                                       }


#--large_state_spaces_with_missing = {"lights" : [{"size":3}, {"size":4}],}

#"spider": [{"width": 3, "height": 3}],
#"mandrill": [{"width": 3, "height": 3}]

#--domain_names={"spider" : [{"width":3,"height":3}]}

NUMBER_OF_RUNS = 5#5
GEN_ACTIONS_NUMBER_OF_RUNS = 5#5
NUMBER_OF_GOALS_AND_INITS = 100 # TODO increase to 100
MISSING_TRANSITIONS_NUMBER_OF_RUNS = 50

MISSING_TRANSITIONS = [0,10,20,30,40,50,60,70,80,90] #] #0,

#---------------------------------------------
# local test
"""
domain_names={"spider" : [{"width":3,"height":3}], "toh"    : [{"blocks":3, "towers":3}]} #,{"width":4,"height":4}{"width":2,"height":2},
#domain_names={"spider" : [{"width":3,"height":3}]}
domain_names={"digital" : [{"width":2,"height":2}]}
#domain_names={"mandrill" : [{"width":2,"height":2}]}
#domain_names={"toh"    : [{"blocks":4, "towers":3}]}
#domain_names={"toh" : [{"blocks":3,"towers":3}]}
domain_names_with_option_for_precreating_action_defs={ "spider" : {"create":{"width":2,"height":2}, "test":[{"width":3,"height":3}]}}
domain_names_with_option_for_precreating_action_defs={ "toh" : {"create":{"blocks":3, "towers":3}, "test":[{"blocks": 2, "towers": 3},{"blocks":4, "towers":3}]}}
domain_names_with_option_for_precreating_action_defs={ "digital" : {"create":{"width":2,"height":2}, "test":[{"width":3,"height":3}]}}
domain_names_with_option_for_precreating_action_defs={ "lights" : {"create":{"size":3}, "test":[{"size":4}]}} #,{"size":2}
#domain_names_with_option_for_precreating_action_defs={ "lights" : {"create":{"size":2} }}

large_state_spaces_with_missing = {"mandrill" : [{"width":3,"height":3}] }
large_state_spaces_with_missing = {"digital" : [{"width":3,"height":3}] }
large_state_spaces_with_missing = {"lights" : [{"size":3}] }

domain_names = {"digital" : [{"width":3,"height":3}] }
domain_names = {"toh" : [{"blocks": 2, "towers": 3}]}
#domain_names={"lights" : [{"size":3}]}

domain_names_with_option_for_precreating_action_defs={ "spider" : {"create":{"width":2,"height":2}, "test":[{"width":2,"height":2}], "domains":["digital"]}, #,"mandrill","digital"
                                                       }
domain_names={"digital" : [{"width":2,"height":2}]}
MISSING_TRANSITIONS = [0,80] #0,
MISSING_TRANSITIONS_NUMBER_OF_RUNS = 1
NUMBER_OF_RUNS = 1
GEN_ACTIONS_NUMBER_OF_RUNS = 1
NUMBER_OF_GOALS_AND_INITS = 1
# digital:
#v GAP:2
#h GAP:3
# spider:
#v GAP:2
#h GAP:2
"""
#---------------------------------------------

OUTPUT_DIR = "./experiment_output/"
OUTPUT_FILE_NAME = "output.txt"


def start_experiments():
    # all transitions
    #--start_experiments_with_all_transtions(domain_names) #<-- this is included within start_experiments_with_missing_transitions()

    #--start_experiments_with_precreated_action_definitions()

    start_experiments_with_missing_transitions()


    #--handle_data.update_missing_precentage_of_pre_images(90)
    #--start_experiments_with_all_transtions(large_state_spaces_with_missing)
    #--handle_data.update_missing_precentage_of_pre_images(0)
    #
    #
#===================================================================


def start_experiments_with_missing_transitions():
    for domain_name in domain_names:
        experiment_results_per_domain = []
        for option in domain_names[domain_name]:
            for percentage_of_missing_transitions in MISSING_TRANSITIONS:
                experiment_results = []
                for i in range(MISSING_TRANSITIONS_NUMBER_OF_RUNS):

                #if (not domain_names[domain_name]):
                #    experiment_result = run_experiment_for_domain(domain_name, None, percentage_of_missing_transitions)
                #    experiment_results.append(experiment_result)

                    experiment_result = run_experiment_for_domain(domain_name, option, percentage_of_missing_transitions, i)
                    experiment_results.append(experiment_result)
                experiment_results_per_domain.append(experiment_results)
        write_result_to_file(experiment_results_per_domain, "missing_transitions/" + domain_name + "/")

#===================================================================


def start_experiments_with_precreated_action_definitions():
    for domain_name in domain_names_with_option_for_precreating_action_defs:
        experiment_results = []
        #--for i in range(NUMBER_OF_RUNS):
        object_and_state_generation.clear_all_info()
        image_pairs_iter = image_pairs.ImagePairs(domain_name, True, domain_names_with_option_for_precreating_action_defs[domain_name]["create"])
        image_pairs_iter.set_percentage_of_missing_transitions(0)#percentage_of_missing_transitions)
        transitions, location_definitions, image_object_definitions, domain, create_objects_and_actions_times = create_objects_and_action_definitions(image_pairs_iter)
        static_atoms = GroundedState.static_atoms.copy()
        print ("created_objects_and_action_definitions")

        for option in domain_names_with_option_for_precreating_action_defs[domain_name]["test"]:
            #if (option == domain_names_with_option_for_precreating_action_defs[domain_name]):
            #    continue
            if ("domains" in domain_names_with_option_for_precreating_action_defs[domain_name]):
                for sub_domain_name in domain_names_with_option_for_precreating_action_defs[domain_name]["domains"]:
                    object_and_state_generation.clear_all_info()
                    experiment_result = run_experiments_with_precreated_domain(sub_domain_name, option, domain,location_definitions,image_object_definitions, static_atoms)
                    experiment_results.append(experiment_result)
            else:
                experiment_result = run_experiments_with_precreated_domain(domain_name, option, domain, location_definitions, image_object_definitions, static_atoms)
                experiment_results.append(experiment_result)
        #-- end for
        write_result_to_file(experiment_results, "precreated_action_definitions/" + domain_name + "/")

#------------------------------------------------------------------------------

def run_experiments_with_precreated_domain(domain_name, option, domain, precreated_location_definitions, precreated_image_object_definitions, precreated_static_atoms):
    experiment_results = []
    """
    location_definitions, image_object_definitions, image_pairs_iter  = object_and_state_generation.create_objects_and_static_atoms(domain, precreated_location_definitions, precreated_image_object_definitions,  domain_name, True, option)
    initial_state, goal_state = image_pairs_iter.get_init_and_goal_image(True)
    all_problem_generation_time_taken, all_planning_total_time, all_plan_to_images_time_taken, all_plan_length = run_problem_and_plan_generation(location_definitions, image_object_definitions, initial_state.image, goal_state.image, domain)
    result = {"init": initial_state.id, "goal": goal_state.id, "problem_gen_time": all_problem_generation_time_taken,
              "planning_time": all_planning_total_time, "plan_to_images_time": all_plan_to_images_time_taken,
              "plan_length": all_plan_length}

    print (result)
    return []
    """
    #image_pairs_iter = image_pairs.ImagePairs(domain_name, True, option)
    percentage_of_missing_transitions = 0
    #for percentage_of_missing_transitions in MISSING_TRANSITIONS:
    #image_pairs_iter.set_percentage_of_missing_transitions(percentage_of_missing_transitions)
    obj_creation_times = []
    #--for i in range(NUMBER_OF_RUNS):
    #--clear_all_info()
    for i in range(NUMBER_OF_RUNS):
        time_before_create_objects = time.time()
        print ("create_objects...")
        location_definitions, image_object_definitions, image_pairs_iter  = object_and_state_generation.create_objects_and_static_atoms(domain, precreated_location_definitions, precreated_image_object_definitions,  domain_name, True, option, precreated_static_atoms)

        #transitions, location_definitions, image_object_definitions = create_objects(image_pairs_iter)
        time_after_create_objects = time.time()
        obj_creation_times.append(time_after_create_objects - time_before_create_objects)
    # -- end of for
    result_per_goal = []
    print ("NUMBER_OF_GOALS_AND_INITS...")
    for i in range(NUMBER_OF_GOALS_AND_INITS):
        initial_state, goal_state = image_pairs_iter.get_init_and_goal_image(True)
        all_problem_generation_time_taken, all_planning_total_time, all_plan_to_images_time_taken, all_plan_length = run_problem_and_plan_generation(location_definitions, image_object_definitions, initial_state.image, goal_state.image, domain)

        result = {"init": initial_state.id, "goal": goal_state.id, "problem_gen_time": all_problem_generation_time_taken, "planning_time": all_planning_total_time, "plan_to_images_time": all_plan_to_images_time_taken, "plan_length": all_plan_length}
        result_per_goal.append(result)

    experiment_result = {"domain": domain_name, "option": option, "percentage_missing": percentage_of_missing_transitions, "obj_creation_time": obj_creation_times, "per_goal": result_per_goal, "num_action_definitions": len(domain.defined_actions), "num_image_objects":len(image_object_definitions), "num_locations":len(location_definitions)}
    #experiment_results.append(experiment_result)
    return experiment_result

#===================================================================

def start_experiments_with_all_transtions(test_map):
    for domain_name in test_map:
        print("start_experiments_with_all_transtions; domain = " + domain_name)
        experiment_results = []
        if (not test_map[domain_name]):
            experiment_result = run_experiment_for_domain(domain_name)
            experiment_results.append(experiment_result)
        for option in test_map[domain_name]:
            print("start_experiments_with_all_transtions; domain = " + domain_name + " option = " + str(option))
            experiment_result = run_experiment_for_domain(domain_name, option)
            experiment_results.append(experiment_result)
        write_result_to_file(experiment_results, "all_transitions/" + domain_name + "/")


#--------------------------------------------------------------
init_states = []
goal_states = []
def run_experiment_for_domain(domain_name, option=None, percentage_of_missing_transitions = 0, i = 0):
    if (percentage_of_missing_transitions == 0 and i == 0):
        init_states.clear()
        goal_states.clear()

    image_pairs_iter = image_pairs.ImagePairs(domain_name, True, option)
    image_pairs_iter.set_percentage_of_missing_transitions(percentage_of_missing_transitions)
    try:
        transitions, location_definitions, image_object_definitions, domain, create_objects_and_actions_times = create_objects_and_action_definitions(image_pairs_iter)
    except:
        experiment_result = {"domain": domain_name, "option": option, "percentage_missing": percentage_of_missing_transitions, "obj_and_action_def_creation_time": -1,
                             "per_goal": [], "num_transitions": -1, "num_action_definitions": -1, "num_image_objects": -1, "num_locations": -1}
        return experiment_result

    print("create_objects_and_actions_times=" + str(create_objects_and_actions_times[0]))
    result_per_goal = []
    for i in range(NUMBER_OF_GOALS_AND_INITS):
        if (percentage_of_missing_transitions == 0):
            initial_state, goal_state = image_pairs_iter.get_init_and_goal_image(True)
            if (not isinstance(goal_state, image_pairs.State)): # we have ran out of options.
                break
            init_states.append(initial_state)
            goal_states.append(goal_state)
        else:
            initial_state, goal_state = image_pairs_iter.init_and_goal_pre_made_translator(init_states[i], goal_states[i])
            #initial_state = init_states[i]
            #goal_state = goal_states[i]
        try:
            all_problem_generation_time_taken, all_planning_total_time, all_plan_to_images_time_taken, all_plan_length = run_problem_and_plan_generation(location_definitions, image_object_definitions, initial_state.image, goal_state.image, domain)

        #cv2.imshow('initial_state', np.uint8(initial_state.image.get_image()))
        #cv2.imshow('goal_states', np.uint8(goal_state.image.get_image()))
        #print("wait..")
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

            result = {"init":initial_state.id, "goal":goal_state.id, "problem_gen_time":all_problem_generation_time_taken, "planning_time":all_planning_total_time, "plan_to_images_time":all_plan_to_images_time_taken, "plan_length":all_plan_length}
        except:
            result = {"init":initial_state.id, "goal":goal_state.id, "problem_gen_time":[], "planning_time":[], "plan_to_images_time":[], "plan_length":[]}

        result_per_goal.append(result)

    experiment_result = {"domain":domain_name, "option":option, "percentage_missing":percentage_of_missing_transitions, "obj_and_action_def_creation_time": create_objects_and_actions_times, "per_goal":result_per_goal, "num_transitions":len(transitions), "num_action_definitions":len(domain.defined_actions), "num_image_objects":len(image_object_definitions), "num_locations":len(location_definitions)}
    return experiment_result

#--------------------------------------------------------------

def create_objects_and_action_definitions(image_pairs_iter):
    create_objects_and_actions_times = []
    for i in range(GEN_ACTIONS_NUMBER_OF_RUNS):
        image_pairs_iter.reset()
        object_and_state_generation.clear_all_info()
        create_action_definitions_start_time = time.time()
        transitions, location_definitions, image_object_definitions = create_objects(image_pairs_iter)
        domain = create_action_defintions(transitions, location_definitions, image_object_definitions)
        create_action_definitions_end_time = time.time()

        create_action_definitions_time_taken = create_action_definitions_end_time - create_action_definitions_start_time
        create_objects_and_actions_times.append(create_action_definitions_time_taken)
    return transitions, location_definitions, image_object_definitions, domain, create_objects_and_actions_times

#--------------------------------------------------------------

def run_problem_and_plan_generation(location_definitions, image_object_definitions, initial_state, goal_state, domain):
    all_problem_generation_time_taken = []
    all_planning_total_time = []
    all_plan_to_images_time_taken = []
    all_plan_length = []

    for i in range(NUMBER_OF_RUNS):
        problem_generation_start_time = time.time()
        problem = pddl_problem.Problem(location_definitions, image_object_definitions, initial_state.get_image(), goal_state.get_image())
        problem_generation_end_time = time.time()
        problem_generation_time_taken = problem_generation_end_time - problem_generation_start_time
        all_problem_generation_time_taken.append(problem_generation_time_taken)
        print("DONE: pddl_problem.Problem() in " + str(problem_generation_time_taken))

        plan_with_string_actions, planning_total_time = fast_downward.run_planner(domain, problem)
        all_planning_total_time.append(planning_total_time)
        all_plan_length.append(len(plan_with_string_actions))
        print(plan_with_string_actions)
        print("Found plan; Total time reported by planner = " + str(planning_total_time))

        # plan to images:
        plan_to_images_start_time = time.time()
        plan = plan_generator.Plan(domain, problem, plan_with_string_actions)
        plan.set_all_actions_definitions()
        plan.create_image_sequence()

        #plan_generator.debug_show_image_sequence(plan, problem)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        plan_to_images_end_time = time.time()
        plan_to_images_time_taken = plan_to_images_end_time - plan_to_images_start_time
        all_plan_to_images_time_taken.append(plan_to_images_time_taken)
        print("Converted plan; Total to convert images = " + str(plan_to_images_time_taken))

    return all_problem_generation_time_taken, all_planning_total_time, all_plan_to_images_time_taken, all_plan_length

#==============================================================================

def write_result_to_file(experiment_results, dir_exp_name): #"all_transitions/" + domain + "/"):
    full_directory = OUTPUT_DIR + dir_exp_name
    os.makedirs(full_directory, exist_ok=True)
    full_file_name = full_directory + OUTPUT_FILE_NAME
    f = open(full_file_name, "w")
    f.write(str(experiment_results))
    f.close()


#==============================================================================
"""
def clear_all_info():
    object_definitions.id_for_object_definition = 0
    grounded_state.GroundedState.static_atoms.clear()
    domain_definition.defined_predicates.clear()
    domain_definition.action_definition_id = 0
"""

def create_objects(image_pairs_iter):
    transitions, all_image_areas = image_parsing.parse_images(image_pairs_iter)  # image_directory)
    location_definitions, image_object_definitions = create_object_definitions.create_object_and_location_definitions(all_image_areas, transitions)
    return transitions, location_definitions, image_object_definitions

def create_action_defintions(transitions, location_definitions, image_object_definitions):
    action_nodes = create_action_graph.create_action_graph(transitions, location_definitions, image_object_definitions)
    action_definitions = create_action_definitions.create_action_definitions(action_nodes)
    domain = domain_definition.Domain(domain_definition.defined_predicates, action_definitions, location_definitions, image_object_definitions)
    return domain

