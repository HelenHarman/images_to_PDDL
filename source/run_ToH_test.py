import os
import random
import time

import cv2
import numpy as np

from generate_images.image_pairs import State
from problem import pddl_problem, plan_generator, fast_downward
from problem.plan_generator import Plan

NUMBER_OF_TESTS = 10
RUNS_PER_TEST = 5

# USED FOR PAIR PAPER



def run_tests(location_definitions, image_object_definitions, domain, image_directory):
    states = []
    for file in os.listdir(image_directory):
        if "pre.png"  in file:
            image = cv2.imread(image_directory + file)
            if (image not in states):
                states.append(State(image, file))

    all_problem_generation_time_taken = []
    all_planning_total_time = []
    all_plan_to_images_time_taken = []
    all__plan_length = []
    selected_files_init = []
    selected_files_goal = []

    for i in range(NUMBER_OF_TESTS):
        initial_state = random.choice(states)
        states.remove(initial_state)
        selected_files_init.append(initial_state.id)

        goal_state = random.choice(states)
        states.remove(goal_state)
        selected_files_goal.append(goal_state.id)

        problem_generation_time_taken, planning_total_time, plan_to_images_time_taken, plan_length = run_test(location_definitions, image_object_definitions, initial_state.image, goal_state.image, domain)
        all_problem_generation_time_taken.append(problem_generation_time_taken)
        all_planning_total_time.append(planning_total_time)
        all_plan_to_images_time_taken.append(plan_to_images_time_taken)
        all__plan_length.append(plan_length)


    print("============================================================")
    print("Init files = " + str(selected_files_init))
    print("Goal files = " + str(selected_files_goal))
    print("Problem generation time = " + str(np.mean(all_problem_generation_time_taken)))
    print("Total time reported by planner = " + str(np.mean(all_planning_total_time)))
    print("Plan to images conversion time = " + str(np.mean(all_plan_to_images_time_taken)))
    print("Average plan length = " + str(np.mean(all__plan_length)))
    print("============================================================")


def run_test(location_definitions, image_object_definitions, initial_state, goal_state, domain):
    all_problem_generation_time_taken = []
    all_planning_total_time = []
    all_plan_to_images_time_taken = []
    all__plan_length = []

    for i in range(RUNS_PER_TEST):
        problem_generation_start_time = time.time()
        problem = pddl_problem.Problem(location_definitions, image_object_definitions, initial_state, goal_state)
        problem_generation_end_time = time.time()
        problem_generation_time_taken = problem_generation_end_time - problem_generation_start_time
        all_problem_generation_time_taken.append(problem_generation_time_taken)
        print("DONE: pddl_problem.Problem() in " + str(problem_generation_time_taken))



        plan_with_string_actions, planning_total_time = fast_downward.run_planner(domain, problem)
        all_planning_total_time.append(planning_total_time)
        all__plan_length.append(len(plan_with_string_actions))
        print(plan_with_string_actions)
        print("Found plan; Total time reported by planner = " + str(planning_total_time))


        # plan to images:
        plan_to_images_start_time = time.time()
        plan = Plan(domain, problem, plan_with_string_actions)
        plan.set_all_actions_definitions()
        plan.create_image_sequence()
        plan_to_images_end_time = time.time()
        plan_to_images_time_taken = plan_to_images_end_time - plan_to_images_start_time
        all_plan_to_images_time_taken.append(plan_to_images_time_taken)
        print("Converted plan; Total to convert images = " + str(plan_to_images_time_taken))

    return np.mean(all_problem_generation_time_taken), np.mean(all_planning_total_time), np.mean(all_plan_to_images_time_taken), np.mean(all__plan_length)