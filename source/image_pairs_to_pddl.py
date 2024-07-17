import time

import cv2
import numpy as np

import image_handling.parse_images_to_create_transitions_and_locations as image_parsing
import action_graph.create_action_graph  as create_action_graph
import run_ToH_test
import run_experiments
from definitions import create_action_definitions, create_object_definitions, domain_definition#create_definitions
from generate_images import image_pairs
from problem import pddl_problem, plan_generator

image_directory = "../generate_images/hanoi_generated_images/"
#image_directory = "../generate_images/spider_generated_images/"

def main():

   print("STARTING: image_handling.parse_images()...")
   #transitions, all_image_areas = image_parsing.parse_images(image_directory)
  # image_pairs_iter = image_pairs.ImagePairs("lights", True, {"size":2})#
   #--image_pairs_iter.set_percentage_of_missing_transitions(10)
   image_pairs_iter = image_pairs.ImagePairs("toh", True)#
   transitions, all_image_areas = image_parsing.parse_images(image_pairs_iter)

   print("DONE: image_handling.parse_images()")
   print("STARTING: create_location_definitions.create_object_and_location_definitions()...")
   location_definitions, image_object_definitions = create_object_definitions.create_object_and_location_definitions(all_image_areas, transitions)
   print("DONE: create_location_definitions.create_object_and_location_definitions()")
   print("STARTING: create_action_graph.create_action_graph()...")
   action_nodes = create_action_graph.create_action_graph(transitions, location_definitions, image_object_definitions)
   print("DONE: create_action_graph()")
   print("STARTING: create_action_definitions.create_action_definitions()...")
   action_definitions = create_action_definitions.create_action_definitions(action_nodes)
   print("DONE: create_action_definitions.create_action_definitions()")


   #all_objects = location_definitions.copy()
   #all_objects.extend(image_object_definitions)
   print("STARTING: domain_definition.create_pddl_domain_definition()")
   domain = domain_definition.Domain(domain_definition.defined_predicates, action_definitions, location_definitions, image_object_definitions)
   print("DONE: domain_definition.create_pddl_domain_definition()")


   print("STARTING: create pddl_problem.Problem()")
   #--problem = pddl_problem.Problem(location_definitions, image_object_definitions, image_directory+"init.png", image_directory+"goal.png")
   #--problem = pddl_problem.Problem(location_definitions, image_object_definitions, image_directory+"0_pre.png", image_directory+"239_pre.png")

   init, goal = image_pairs_iter.get_init_and_goal_image()
   problem = pddl_problem.Problem(location_definitions, image_object_definitions, init, goal)

   print("DONE: pddl_problem.Problem()")

   print("STARTING: plan_generator.generate_plan()")
   plan_generator.generate_plan(domain, problem)

   print("DONE: ALL")
   cv2.waitKey(0)
   cv2.destroyAllWindows()

def run_experiments_for_pair_paper():
   all_times = []
   image_pairs_iter = image_pairs.ImagePairs(image_directory, False)
   for i in range(5):#5):
      create_action_definitions_start_time = time.time()
      transitions, all_image_areas = image_parsing.parse_images(image_pairs_iter) #image_directory)
      print("DONE: image_handling.parse_images()")
      print("STARTING: create_location_definitions.create_object_and_location_definitions()...")
      location_definitions, image_object_definitions = create_object_definitions.create_object_and_location_definitions(all_image_areas, transitions)
      print("DONE: create_location_definitions.create_object_and_location_definitions()")
      print("STARTING: create_action_graph.create_action_graph()...")
      action_nodes = create_action_graph.create_action_graph(transitions, location_definitions, image_object_definitions)
      print("DONE: create_action_graph()")
      print("STARTING: create_action_definitions.create_action_definitions()...")
      action_definitions = create_action_definitions.create_action_definitions(action_nodes)
      print("DONE: create_action_definitions.create_action_definitions()")
      print("STARTING: domain_definition.create_pddl_domain_definition()")
      domain = domain_definition.Domain(domain_definition.defined_predicates, action_definitions, location_definitions, image_object_definitions)
      print("DONE: domain_definition.create_pddl_domain_definition()")

      create_action_definitions_end_time = time.time()

      create_action_definitions_time_taken = create_action_definitions_end_time - create_action_definitions_start_time
      all_times.append(create_action_definitions_time_taken)

   run_ToH_test.run_tests(location_definitions, image_object_definitions, domain, image_directory)

   print("============================================================")
   print("Generate action definitions time = " + str(np.mean(create_action_definitions_time_taken)))
   print("============================================================")



if __name__ == "__main__":
   #run_experiments()
   #main()
   run_experiments.start_experiments()











"""
exit(0)
action_nodes, all_objects = image_handling.parse_images()
print("DONE: image_handling.parse_images()")
operator_nodes = create_action_graph.create_action_graph(action_nodes, all_objects)
print("DONE: create_action_graph()")
action_nodes, defined_objects = create_definitions.create_definitions(action_nodes, all_objects)
print("DONE: create_definitions()")
# Each action has a list of links (that state the preconditions of the action)
# TODO use the action graph structure to reduce the number of links. e.g., for x to be cleared x and y must be clear and for x to be cleared x, y must be cleared. Therefore x doesn't have to depend on y
#  see: create_definitions.reduce_number_of_links(objects_to_links)


# TODO write action definitions:
create_action_definitions.create_action_definitions(action_nodes, defined_objects)
print("DONE: create_action_definitions()")

cv2.waitKey(0)
cv2.destroyAllWindows()

"""