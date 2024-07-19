#! /usr/bin/env python

import numpy as np

domains = ["digital", "mandrill", "spider", "lights", "toh"]
puzzle_domains = ["digital", "mandrill", "spider"]

all_transitions_files = []
missing_transitions_files = []
for domain in domains:
	all_transitions_files.append("./images_to_pddl_output/100_goals/all_transitions/" + domain + "/output.txt")
	missing_transitions_files.append("./images_to_pddl_output/100_goals/missing_transitions/" + domain + "/output.txt")
	#missing_transitions_files.append("./images_to_pddl_output/100_goals/high_num_missing/missing_transitions/" + domain + "/output.txt")

precreated_domain_files = []
for domain in ["digital", "lights", "toh"]: #
	precreated_domain_files.append("./images_to_pddl_output/100_goals/precreated_action_definitions/" + domain + "/output.txt")


MISSING_TRANSITIONS = [0,10,20,30,40,50,60] 
#MISSING_TRANSITIONS = [0,70,80,90]
#===============================================
# methods required for all data printing
def read_in_data(file_name):
	f = open(file_name, 'r')
	content = eval(f.read())
	f.close()
	return content

def sTi(num):
	return  '{0:.2f}'.format(round(num, 2)) #str(round(num, 2))

def configToStr(config):
	if "width" in config:
		return str(config["width"]) + " by " + str(config["height"])
	if "size" in config:
		return str(config["size"]) + " by " + str(config["size"])
	if "towers" in config:
		return str(config["blocks"]) + " discs" #str(config["towers"]) + " towers, " + 

#===============================================


puzzle_correct_number_of_action_definitions = {}
puzzle_correct_number_of_image_objects = {}
puzzle_correct_number_of_locations = {}
puzzle_created_plan = {}
puzzle_correct_plan_lengths = {}
puzzle_correct_plan_diff = {}
for i in MISSING_TRANSITIONS:
	puzzle_correct_number_of_action_definitions[i] = [] 
	puzzle_correct_number_of_image_objects[i] = [] 
	puzzle_correct_number_of_locations[i] = [] 
	puzzle_created_plan[i] = [] 
	puzzle_correct_plan_lengths[i] = [] 
	puzzle_correct_plan_diff[i] = [] 


def process_missing_transtions_results():
	for missing_transitions_file in missing_transitions_files:
		#if "toh" not in missing_transitions_file:
		#	continue
		results = read_in_data(missing_transitions_file)
		configs = get_all_configs(results)
		
		for config in configs:
			baseline_number_of_locations, baseline_number_of_image_objects, baseline_number_of_action_definitions, baseline_plan_lengths = get_all_transtions_base_result(results, config)
			for missing in MISSING_TRANSITIONS:	
				correct_number_of_locations = [] 
				correct_number_of_image_objects = []  
				correct_number_of_action_definitions = []  
				action_definition_diff = [] 
				created_plan = []
				correct_plan_lengths = [] 
				correct_plan_diff = [] 

				problem_gen_time = []
				planning_time = []
				plan_to_images_time = []
				obj_and_action_def_creation_times = []		
			
				for result1 in results:	
					for result in result1:					

						if (result["percentage_missing"] != missing or (config != configToStr(result["option"])) or ("width" in result["option"] and result["option"]["width"] >= 3)or ("size" in result["option"] and result["option"]["size"] >= 3)):
							continue
						#print(missing)

						#if(missing == 0):
						#	print result["num_locations"]
						#	print baseline_number_of_locations
						correct_number_of_locations.append(int(result["num_locations"] == baseline_number_of_locations))
						correct_number_of_image_objects.append(int(result["num_image_objects"] == baseline_number_of_image_objects))
						correct_number_of_action_definitions.append(int(result["num_action_definitions"] == baseline_number_of_action_definitions))

						action_definition_diff.append(result["num_locations"] - baseline_number_of_locations)
				
						if (isinstance(result["obj_and_action_def_creation_time"], int)):
							print("obj creation failed " + str(missing))
							for baseline_plan_length in baseline_plan_lengths:
								created_plan.append(0)
						else:
							obj_and_action_def_creation_times.extend(result["obj_and_action_def_creation_time"])
						#print(result["domain"] + configToStr(result["option"])  )
						#print(result["num_action_definitions"] )
						for plan_gen_result in result["per_goal"]:
							if ((plan_gen_result["init"], plan_gen_result["goal"]) in baseline_plan_lengths):
								if (not plan_gen_result["plan_length"] or (plan_gen_result["plan_length"][0]==0 and baseline_plan_lengths[(plan_gen_result["init"], plan_gen_result["goal"])]!=0) ):
									created_plan.append(0)
								else:
									created_plan.append(1)
									correct_plan_lengths.append(int(baseline_plan_lengths[(plan_gen_result["init"], plan_gen_result["goal"])] == plan_gen_result["plan_length"][0]))
									problem_gen_time.extend(plan_gen_result["problem_gen_time"])
									planning_time.extend(plan_gen_result["planning_time"])
									plan_to_images_time.extend(plan_gen_result["plan_to_images_time"])

									plan_diff = int(plan_gen_result["plan_length"][0] - baseline_plan_lengths[(plan_gen_result["init"], plan_gen_result["goal"])])
									
									#if (plan_diff < 0):
									#	exit(0)
									correct_plan_diff.append(plan_diff)
								
							else:
								print("---" + str((plan_gen_result["init"], plan_gen_result["goal"])))
				#print ("plan_diff=" + str(correct_plan_diff))
				#print ("action_definition_diff=" + str(action_definition_diff))
				result_str = ""
				result_str += result["domain"] + " & "
				result_str += config + " & "
				result_str += str(missing) + " & "
				result_str += sTi(np.mean(correct_number_of_action_definitions))  + " & "
				result_str += sTi(np.mean(correct_number_of_image_objects))  + " & "
				result_str += sTi(np.mean(correct_number_of_locations))  + " & "
				result_str += sTi(np.mean(created_plan))  + " & "
				result_str += sTi(np.mean(correct_plan_lengths))  + " & "
				result_str += sTi(np.mean(correct_plan_diff))  + " \\\\ "



				if result["domain"] in puzzle_domains:
					puzzle_correct_number_of_action_definitions[missing].extend(correct_number_of_action_definitions)
					puzzle_correct_number_of_image_objects[missing].extend(correct_number_of_image_objects)
					puzzle_correct_number_of_locations[missing].extend(correct_number_of_locations)
					puzzle_created_plan[missing].extend(created_plan)
					puzzle_correct_plan_lengths[missing].extend(correct_plan_lengths)
					puzzle_correct_plan_diff[missing].extend(correct_plan_diff)

				#result_str += sTi(np.mean(obj_and_action_def_creation_times)) + " $\pm$ " + sTi(np.std(obj_and_action_def_creation_times))  + " &     "	
				#result_str += sTi(np.mean(problem_gen_time)) + " $\pm$ " + sTi(np.std(problem_gen_time))  + " & "
				#result_str += sTi(np.mean(planning_time)) + " $\pm$ " + sTi(np.std(planning_time))  + " & "
				#result_str += sTi(np.mean(plan_to_images_time)) + " $\pm$ " + sTi(np.std(plan_to_images_time))  + " \\\\ "
				print(result_str)

	for missing in MISSING_TRANSITIONS:	
		result_str = "Puzzle & "
		result_str += "2 by 2 & "
		result_str += str(missing) + " & "
		result_str += sTi(np.mean(puzzle_correct_number_of_action_definitions[missing]))  + " & "
		result_str += sTi(np.mean(puzzle_correct_number_of_image_objects[missing]))  + " & "
		result_str += sTi(np.mean(puzzle_correct_number_of_locations[missing]))  + " & "
		result_str += sTi(np.mean(puzzle_created_plan[missing]))  + " & "
		result_str += sTi(np.mean(puzzle_correct_plan_lengths[missing]))  + " & "
		result_str += sTi(np.mean(puzzle_correct_plan_diff[missing]))  + " \\\\ "
		print(result_str)
#--------------------------------------

def get_all_configs(results):
	configs = []
	for result1 in results:
		for result in result1:
			if (configToStr(result["option"]) not in configs):
				configs.append(configToStr(result["option"]))
	return configs

#--------------------------------------

def get_all_transtions_base_result(results, config):
	number_of_locations = -1	
	number_of_image_objects = -1	
	number_of_action_definitions = -1	
	plan_lengths = {} #(init, goal) --> plan length

	for result1 in results:
		#result = result1[0]
		for result in result1:
			if (result["percentage_missing"] != 0 or config != configToStr(result["option"])):
				continue
			
			number_of_locations = result["num_locations"]
			number_of_image_objects = result["num_image_objects"]
			number_of_action_definitions = result["num_action_definitions"]
			for plan_gen_result in result["per_goal"]:
				plan_lengths[(plan_gen_result["init"], plan_gen_result["goal"])] = plan_gen_result["plan_length"][0]

	
	return number_of_locations, number_of_image_objects, number_of_action_definitions, plan_lengths

	



#===============================================

def process_precreated_domain_results():
	results_for_creating_plan(precreated_domain_files)	
	mean_obj_creation_time_precreated_domain_results(precreated_domain_files)
	return 
	for precreated_domain_file in precreated_domain_files:
		results = read_in_data(precreated_domain_file)
		processed = []
		for result in results:	
			#result = result1[0]
			if (result["domain"]+configToStr(result["option"]) in processed):
				continue
			processed.append(result["domain"]+configToStr(result["option"]))
			result_str = ""
			result_str += result["domain"] + " & "
			result_str += configToStr(result["option"]) + " & "
			#result_str += str(result["num_transitions"])  + " & "
			#result_str += str(result["num_action_definitions"])  + " & "
			result_str += str(result["num_image_objects"])  + " & "
			result_str += str(result["num_locations"])  + " & "
			result_str += sTi(np.mean(result["obj_creation_time"])) + " $\pm$ " + sTi(np.std(result["obj_creation_time"]))  + " &     "
		#{"domain": domain_name, "option": option, "percentage_missing": percentage_of_missing_transitions, "obj_and_action_def_creation_time": -1,
	       #                  "per_goal": [], "num_transitions": -1, "num_action_definitions": -1, "num_image_objects": -1, "num_locations": -1}
			problem_gen_time = []
			planning_time = []
			plan_to_images_time = []
			plan_length = []
			for plan_gen_result in result["per_goal"]:
				problem_gen_time.extend(plan_gen_result["problem_gen_time"])
				planning_time.extend(plan_gen_result["planning_time"])
				plan_to_images_time.extend(plan_gen_result["plan_to_images_time"])
				plan_length.extend(plan_gen_result["plan_length"])
			

			#"per_goal":[{"init":initial_state.id, "goal":goal_state.id, "problem_gen_time":[], "planning_time":[], "plan_to_images_time":[], "plan_length":[]}]
		
			result_str += sTi(np.mean(problem_gen_time)) + " $\pm$ " + sTi(np.std(problem_gen_time))  + " & "
			result_str += sTi(np.mean(plan_length)) + " $\pm$ " + sTi(np.std(plan_length))  + " & "
			result_str += sTi(np.mean(planning_time)) + " $\pm$ " + sTi(np.std(planning_time))  + " & "
			result_str += sTi(np.mean(plan_to_images_time)) + " $\pm$ " + sTi(np.std(plan_to_images_time))  + " \\\\ "

			print result_str


def mean_obj_creation_time_precreated_domain_results(result_files):
	print("#--------")
	print("Object creation times: ")
	for precreated_domain_file in precreated_domain_files:
		domain_name = precreated_domain_file.split('/')[len(precreated_domain_file.split('/'))-2]
		results = read_in_data(precreated_domain_file)
		config_to_times = {}
		for result in results:	
			str_config = configToStr(result["option"])
			if str_config in config_to_times:
				config_to_times[str_config].extend(result["obj_creation_time"])
			else:
				config_to_times[str_config] = result["obj_creation_time"]
		for config_result in config_to_times:
			print (domain_name + " " + config_result + " = " + sTi(np.mean(config_to_times[config_result])) + " $\pm$ " + sTi(np.std(config_to_times[config_result])))
	print("#--------")
			

#===============================================

def process_all_trantions_results():
	results_for_creating_action_definitions(all_transitions_files)
	results_for_creating_plan(all_transitions_files)
	return

	for all_transitions_file in all_transitions_files:
		results = read_in_data(all_transitions_file)
		for result in results:
			if (result["domain"] == "toh" and result["option"]["towers"] == 2): # error in run experiment script, should have been 3 towers
				continue
			result_str = ""
			result_str += result["domain"] + " & "
			result_str += configToStr(result["option"]) + " & "
			result_str += str(result["num_transitions"])  + " & "
			result_str += str(result["num_action_definitions"])  + " & "
			result_str += str(result["num_image_objects"])  + " & "
			result_str += str(result["num_locations"])  + " & "
			result_str += sTi(np.mean(result["obj_and_action_def_creation_time"])) + " $\pm$ " + sTi(np.std(result["obj_and_action_def_creation_time"]))  + " &     "
		#{"domain": domain_name, "option": option, "percentage_missing": percentage_of_missing_transitions, "obj_and_action_def_creation_time": -1,
           #                  "per_goal": [], "num_transitions": -1, "num_action_definitions": -1, "num_image_objects": -1, "num_locations": -1}
			problem_gen_time = []
			planning_time = []
			plan_to_images_time = []
			plan_length = []
			for plan_gen_result in result["per_goal"]:
				problem_gen_time.extend(plan_gen_result["problem_gen_time"])
				planning_time.extend(plan_gen_result["planning_time"])
				plan_to_images_time.extend(plan_gen_result["plan_to_images_time"])
				plan_length.extend(plan_gen_result["plan_length"])
				

			#"per_goal":[{"init":initial_state.id, "goal":goal_state.id, "problem_gen_time":[], "planning_time":[], "plan_to_images_time":[], "plan_length":[]}]
			
			result_str += sTi(np.mean(problem_gen_time)) + " $\pm$ " + sTi(np.std(problem_gen_time))  + " & "
			result_str += sTi(np.mean(plan_length)) + " $\pm$ " + sTi(np.std(plan_length))  + " & "
			result_str += sTi(np.mean(planning_time)) + " $\pm$ " + sTi(np.std(planning_time))  + " & "
			result_str += sTi(np.mean(plan_to_images_time)) + " $\pm$ " + sTi(np.std(plan_to_images_time))  + " \\\\ "

			print result_str


def results_for_creating_action_definitions(results_files):
	for results_file in results_files:
		results = read_in_data(results_file)
		for result in results:
			result_str = ""
			result_str += result["domain"] + " & " # 
			result_str += configToStr(result["option"]) + " & "
			result_str += str(result["num_transitions"])  + " & "
			result_str += str(result["num_locations"])  + " & "
			result_str += str(result["num_image_objects"])  + " & "
			result_str += str(result["num_action_definitions"])  + " & "
			result_str += sTi(np.mean(result["obj_and_action_def_creation_time"])) + " $\pm$ " + sTi(np.std(result["obj_and_action_def_creation_time"]))  + " \\\\    "		

			print result_str


def results_for_creating_plan(results_files):
	all_planning_times = []
	all_plan_lengths = []
	for results_file in results_files:
		results = read_in_data(results_file)
		for result in results:
			result_str = ""
			result_str += result["domain"] + " & " #&
			result_str += configToStr(result["option"]) + " & "

			problem_gen_time = []
			planning_time = []
			plan_to_images_time = []
			plan_length = []

			problem_gen_time_means = []
			planning_time_means = []
			plan_to_images_time_means = []
			plan_length_means = []
			for plan_gen_result in result["per_goal"]:
				problem_gen_time.extend(plan_gen_result["problem_gen_time"])
				planning_time.extend(plan_gen_result["planning_time"])
				plan_to_images_time.extend(plan_gen_result["plan_to_images_time"])
				plan_length.extend(plan_gen_result["plan_length"])

				all_planning_times.extend(plan_gen_result["planning_time"])
				all_plan_lengths.append(np.mean(plan_gen_result["plan_length"])) # all plan lengths are the same

				problem_gen_time_means.append(np.mean(plan_gen_result["problem_gen_time"]))
				planning_time_means.append(np.mean(plan_gen_result["planning_time"]))
				plan_to_images_time_means.append(np.mean(plan_gen_result["plan_to_images_time"]))
				plan_length_means.append(np.mean(plan_gen_result["plan_length"]))
				

			#"per_goal":[{"init":initial_state.id, "goal":goal_state.id, "problem_gen_time":[], "planning_time":[], "plan_to_images_time":[], "plan_length":[]}]
			result_str += str(len(problem_gen_time_means))  + " & "
			#--result_str += sTi(np.mean(problem_gen_time)) + " $\pm$ " + sTi(np.std(problem_gen_time))  + " & "
			#--result_str += sTi(np.sum(problem_gen_time_means))  + " & "

			result_str += sTi(np.mean(plan_length)) + " $\pm$ " + sTi(np.std(plan_length)) + " & "
			#result_str += sTi(np.sum(problem_gen_time_means))  + " & "

			result_str += sTi(np.mean(planning_time)) + " $\pm$ " + sTi(np.std(planning_time))  + " & "			
			result_str += sTi(np.sum(planning_time_means))  + " \\\\ "

			#--result_str += sTi(np.mean(plan_to_images_time)) + " $\pm$ " + sTi(np.std(plan_to_images_time))  + " & "
			#--result_str += sTi(np.sum(plan_to_images_time_means))  + " \\\\ "

			print result_str
	print ("Average over all planning times = " + sTi(np.mean(all_planning_times)))
	print ("Max over all planning times = " + sTi(max(all_planning_times)))
	print ("Min over all planning times = " + sTi(min(all_planning_times)))


	print ("Average over all planning lengths = " + sTi(np.mean(all_plan_lengths)))
	print ("Max over all planning lengths = " + sTi(max(all_plan_lengths)))
	print ("Min over all planning lengths = " + sTi(min(all_plan_lengths)))
		#print (max(plan_to_images_time))


#===============================================


def main():
	print ("====================") 
	print ("all_trantions") 
	process_all_trantions_results()
	print ("====================") 
	print ("precreated_domain") 
	process_precreated_domain_results()
	print ("====================") 
	print ("missing_transtions") 
	process_missing_transtions_results()


if __name__ == "__main__":
	main()
