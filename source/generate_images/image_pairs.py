import itertools
import os

import cv2
import numpy as np
import random

from generate_images import generate_spider_puzzle, generate_hanoi, generate_lights_out, generate_mandrill_puzzle, \
    generate_digital_puzzle
from image_handling import util


class ImageState:
    keyToImage = None #handle_data.KeyToImage()
    def __init__(self, key, image, in_memory = False):
        if (in_memory):
            self.image = image
        else:
            ImageState.keyToImage.write_data(key, image)
        self.key = key
        self.in_memory = in_memory

    def get_image(self):
        if (self.in_memory ):
            return self.image
        else:
            return ImageState.keyToImage.read_image(self.key)

    def __eq__(self, other):
        if (isinstance(other, str)):
            return (self.key == other)
        return (isinstance(other, ImageState) and self.key == other.key)



class ImagePairs:
    def __init__(self, domain_name, create_images=False, domain_config=None, all_transitions=True):
        self.count = 0
        self.pre = []
        self.suc = []
        self.percentage_of_missing_transitions = 0
        self.missing = []
        self.configs = None

        self.func_gen_image_states = None
        if (create_images):
            if (domain_name == "spider"):
                import_lib = generate_spider_puzzle
            elif (domain_name == "toh"):
                import_lib = generate_hanoi
            elif (domain_name == "lights"):
                import_lib = generate_lights_out
            elif (domain_name == "mandrill"):
                import_lib = generate_mandrill_puzzle
            elif (domain_name == "digital"):
                import_lib = generate_digital_puzzle

            if (all_transitions):
                self.pre, self.suc = import_lib.generate_image_pairs(domain_config)
            else:
                self.pre, self.suc = import_lib.generate_image_pairs_for_single_state(domain_config)
            self.configs = import_lib.configs
            self.func_gen_image_states = import_lib.generate_single_config_use_glob_options

            """
        if (create_images):
            if (domain_name == "spider"):
                if (all_transitions):
                    self.pre, self.suc = generate_spider_puzzle.generate_image_pairs(domain_config)
                else:
                    self.pre, self.suc = generate_spider_puzzle.generate_image_pairs_for_single_state(domain_config)
                self.configs = generate_spider_puzzle.configs
                self.func_gen_image_states = generate_spider_puzzle.generate_single_config_use_glob_options
                #self.covert_to_opencv_images(pre, suc)
            elif (domain_name == "toh"):
                if (all_transitions):
                    self.pre, self.suc = generate_hanoi.generate_image_pairs(domain_config)
                else:
                    self.pre, self.suc = generate_hanoi.generate_image_pairs_for_single_state(domain_config)
                self.configs = generate_hanoi.configs
                self.func_gen_image_states = generate_hanoi.generate_single_config_use_glob_options
                
            elif (domain_name == "lights"):
                self.pre, self.suc = generate_lights_out.generate_image_pairs(domain_config)
            """
        else:
            self.read_images_from_file(domain_name)
        """
        cv2.imshow("image pre ", np.uint8(self.pre[0]))
        cv2.imshow("image suc ", np.uint8(self.suc[0]))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        """

        self.states = []
        self.generate_states()
        print("num states=" + str(len(self.states)))
        self.init_choice = []
        self.goal_choice = []
        self.state_index_list = []
        for i in range(len(self.states)):
            self.state_index_list.append(i)
            self.init_choice.append(i)
            self.goal_choice.append(i)
        if (len(self.states) < 200):  # we don't have enough states for every goal and init to be different:
            self.goal_init_pairs = list(itertools.permutations(self.state_index_list, 2))
        else: # to prevent pc crashing:
            self.goal_init_pairs = None
            self.state_index_list = None

        self.selected_index_goal = []
        self.selected_index_init = []
        self.reset()

    def has_next(self):
        return (self.count < len(self.pre))

    def get_next(self):
        pre = self.pre[self.count]
        suc = self.suc[self.count]

        self.count = self.count +1
        while (self.count in self.missing):
            self.count = self.count +1

        return (pre, suc)

    def reset(self):
        self.count = 0
        while (self.count in self.missing):
            self.count = self.count +1

    def generate_states(self):
        for i in range(len(self.configs)):
            self.states.append(State(self.configs[i], i))

        #for i in range(len(self.pre)):
        #    if (self.pre[i] not in self.states):
        #        self.states.append(State(self.pre[i], i))

    #-------------------------

    def set_percentage_of_missing_transitions(self, percentage_of_missing_transitions):
        self.percentage_of_missing_transitions = percentage_of_missing_transitions
        self.missing = []
        self.transitions = np.arange(len(self.pre)).tolist()
        num_missing = (float(self.percentage_of_missing_transitions)/100.0) * len(self.pre)
        for i in range(int(num_missing)):
            rm = random.choice(self.transitions)
            self.transitions.remove(rm)
            self.missing.append(rm)


    #-------------------------

    def get_init_and_goal_image(self, experiments=False):

        #return State(self.func_gen_image_states(self.states[0].image), self.states[0].id), State(self.func_gen_image_states(self.states[len(self.states) - 1].image), self.states[len(self.states) - 1].id)

        # for testing:
        if (not experiments):
            self.selected_index_init.append(0)
            self.selected_index_goal.append(len(self.states) - 1)
            init = State(self.func_gen_image_states(self.states[0].image), self.states[0].id)
            goal = State(self.func_gen_image_states(self.states[len(self.states) - 1].image), self.states[len(self.states) - 1].id) #300000
            """
            init_image = self.func_gen_image_states(generate_digital_puzzle.init_config)
            goal_image = self.func_gen_image_states(generate_digital_puzzle.goal_config)
            init = State(init_image, self.states[0].id)
            goal = State(goal_image, self.states[len(self.states) - 1].id) #300000
            """
            return init, goal#self.pre[0], self.pre[len(self.pre) - 1]

        # for experiments:
        if (self.goal_init_pairs == None): # to prevent pc crashing:
            initial_state = random.choice(self.init_choice)  # states)
            self.init_choice.remove(initial_state)

            # if (initial_state in self.selected_index_init):
            # goal_match = self.selected_index_goal[self.selected_index_init.index(initial_state)]
            self.selected_index_init.append(initial_state)  # initial_state.id)
            goal_state = initial_state
            while (goal_state == initial_state):
                goal_state = random.choice(self.goal_choice)
            self.goal_choice.remove(goal_state)
            self.selected_index_goal.append(goal_state)  # goal_state.id)

            init = State(self.func_gen_image_states(self.states[initial_state].image), self.states[initial_state].id)
            goal = State(self.func_gen_image_states(self.states[goal_state].image), self.states[goal_state].id)
            return init, goal  # self.states[initial_state], self.states[goal_state] #initial_state.image, goal_state.image
        else: # we don't have enough states for every goal and init to be different:
            if (not self.goal_init_pairs):
                return None, None
            picked = random.choice(self.goal_init_pairs)
            self.goal_init_pairs.remove(picked)
            self.selected_index_init.append(picked[0])
            self.selected_index_goal.append(picked[1])
            init = State(self.func_gen_image_states(self.states[picked[0]].image), self.states[picked[0]].id)
            goal = State(self.func_gen_image_states(self.states[picked[1]].image), self.states[picked[1]].id)
            return init, goal #self.states[initial_state], self.states[goal_state] #initial_state.image, goal_state.image


    def init_and_goal_pre_made_translator(self, pre_init, pre_goal):

        #image_with_config = self.func_gen_image_states(eval(pre_init.image.key))
        init = State(self.func_gen_image_states(eval(pre_init.image.key)), pre_init.id)
        goal = State(self.func_gen_image_states(eval(pre_goal.image.key)), pre_goal.id)
        return init, goal


    def read_images_from_file(self, image_directory):
        for file in os.listdir(image_directory):
            if "pre.png" not in file:  # if "suc.png" in file :
                continue
            pre_image_file = image_directory + file
            suc_image_file = image_directory + file.replace("pre.png", "suc.png")

            self.pre.append(cv2.imread(pre_image_file))
            self.suc.append(cv2.imread(suc_image_file))


    def print_selected(self):
        print("Selected inits: " + str(self.selected_index_init))
        print("Selected goals: " + str(self.selected_index_goal))

    #------------------------------------------------------------------------

    def covert_to_opencv_images(self, pre, suc):
        for i in range(len(pre)):
            self.pre.append(self.convert_image(pre[i]))
            self.suc.append(self.convert_image(suc[i]))

    #----------------------

    def convert_image(self, before_img):
        img = np.zeros([len(before_img), len(before_img[0]), 3])
        for j in range(len(before_img)):
            for k in range(len(before_img[j])):
                if before_img[j][k] == 0:
                    img[j, k, 0] = 0
                    img[j, k, 1] = 0
                    img[j, k, 2] = 0
                else:
                    img[j, k, 0] = 255
                    img[j, k, 1] = 255
                    img[j, k, 2] = 255
        #r, g, b = cv2.split(img)
        #img_bgr = cv2.merge([b, g, r])
        return img
    #----------------------------------------------------------------


#==========================================================================

class State:
    def __init__(self, image, id):
        self.image = image
        self.id = id
    def __eq__(self, other):
        return (self.image == other.image)
        """
        if (isinstance(other, State)):
            return util.are_images_equal(self.image, other.image)
        else:
            return (util.are_images_equal(self.image, other))
        """






#==========================================================================
#==========================================================================

