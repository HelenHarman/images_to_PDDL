import random

import numpy as np
import numpy as np
from generate_images import handle_data, image_pairs, puzzle
from generate_images.puzzle import generate_configs, successors, split_image
import os


image_states = []
configs = None

digital_width = -1
digital_height = -1
def generate_single_config_use_glob_options(config):
    return generate([config], digital_width, digital_height)[0]

def generate(configs, width, height):
    assert width*height <= 16
    base_width = 5
    base_height = 6
    dim_x = base_width*width
    dim_y = base_height*height
    def generate(config):
        if (str(config) in image_states):
            return image_states[image_states.index(str(config))]  # config_to_image[str(config)]
        figure = np.zeros((dim_y,dim_x))
        for digit,pos in enumerate(config):
            x = pos % width
            y = pos // width
            figure[y*base_height:(y+1)*base_height,
                   x*base_width:(x+1)*base_width] = panels[digit]

        image_state = image_pairs.ImageState(str(config), figure)
        # if (str(config) not in image_states):
        image_states.append(image_state)
        return image_state#return figure
    return np.array([ generate(c) for c in configs ])#.reshape((-1,dim_y,dim_x))

def states(width, height, configs=None):
    digit = width * height
    if configs is None:
        configs = generate_configs(digit)
    return generate(configs,width,height)

def transitions(width, height, single_state = False):
    global configs
    digit = width * height
    if configs is None:
        configs = list(generate_configs(digit))

    if (single_state):
        c1 = configs[random.randrange(len(configs))] #random.choice(list(configs))
        sucs = successors(c1,width,height)
        pre_images = []
        suc_images = []
        for suc in sucs:
            pre,suc = generate([c1, suc], width, height)
            pre_images.append(pre)
            suc_images.append(suc)
        return [pre_images, suc_images]#transitions
    else:
        configs_with_missing = configs.copy()
        num_missing = (float(handle_data.MISSING_PERCENTAGE_OF_PRE_IMAGES) / 100.0) * len(configs_with_missing)
        #num_missing = len(configs_with_missing) - 500
        print(num_missing)
        print(len(configs_with_missing) - num_missing)
        for i in range(int(num_missing)):
            index = random.randrange(len(configs_with_missing))
            configs_with_missing.pop(index)

        transitions = np.array([ generate([c1,c2],width,height)
                             for c1 in configs_with_missing for c2 in successors(c1,width,height) ])

    return np.einsum('ab...->ba...',transitions)


def get_minimum_transitions(width, height):
    global configs
    if configs is None:
        configs = list(generate_configs(width * height))
    pre_images = []
    suc_images = []
    for transition_config in puzzle.min_transition_configs:
        pre_image, suc_image = generate([transition_config[0], transition_config[1]], width, height)
        pre_images.append(pre_image)
        suc_images.append(suc_image)
    return [pre_images, suc_images]


def generate_image_pairs_for_single_state(options):
    return generate_image_pairs(options, True)


def generate_image_pairs(options=None, single_state=False, use_min_transitions = False):
    global image_states
    global configs
    global digital_width
    global digital_height
    configs = None
    image_states.clear()

    if (options == None):
        digital_width = 2
        digital_height = 2
    else:
        digital_width = options["width"]
        digital_height = options["height"]

    handle_data.create_new_datastore("mandrill", "width"+str(digital_width)+"_height"+str(digital_height))

    if ((not single_state) and digital_width == 3 and digital_height == 3):#use_min_transitions):
        all_transitions = get_minimum_transitions(digital_width, digital_height)
    else:
        all_transitions = transitions(digital_width, digital_height, single_state)
    #--

    return all_transitions[0], all_transitions[1]


goal_config = (0,1,2,3,4,5,6,7,8)
init_config = (7,0,1,3,5,2,6,4,8) #To work out states: what are the two positions whose values you want to swap?






panels = [
    [[  0,   0,   0,   0,   0,],
     [  0,   0, 255,   0,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255,   0, 255,   0,],
     [  0,   0, 255,   0,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0,   0, 235,   0,   0,],
     [  0,   0, 235,   0,   0,],
     [  0,   0, 235,   0,   0,],
     [  0,   0, 235,   0,   0,],
     [  0,   0, 235,   0,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 215, 215, 215,   0,],
     [  0,   0,   0, 215,   0,],
     [  0, 215, 215, 215,   0,],
     [  0, 215,   0,   0,   0,],
     [  0, 215, 215, 215,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 195, 195, 195,   0,],
     [  0,   0,   0, 195,   0,],
     [  0, 195, 195, 195,   0,],
     [  0,   0,   0, 195,   0,],
     [  0, 195, 195, 195,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 175,   0, 175,   0,],
     [  0, 175,   0, 175,   0,],
     [  0, 175, 175, 175,   0,],
     [  0,   0,   0, 175,   0,],
     [  0,   0,   0, 175,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 155, 155, 155,   0,],
     [  0, 155,   0,   0,   0,],
     [  0, 155, 155, 155,   0,],
     [  0,   0,   0, 155,   0,],
     [  0, 155, 155, 155,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 135, 135, 135,   0,],
     [  0, 135,   0,   0,   0,],
     [  0, 135, 135, 135,   0,],
     [  0, 135,   0, 135,   0,],
     [  0, 135, 135, 135,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 115, 115, 115,   0,],
     [  0,   0,   0, 115,   0,],
     [  0,   0,   0, 115,   0,],
     [  0,   0,   0, 115,   0,],
     [  0,   0,   0, 115,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0,  95,  95,  95,   0,],
     [  0,  95,   0,  95,   0,],
     [  0,  95,  95,  95,   0,],
     [  0,  95,   0,  95,   0,],
     [  0,  95,  95,  95,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0, 255, 255, 255,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255, 255, 255,   0,],
     [  0,   0,   0, 255,   0,],
     [  0,   0,   0, 255,   0,],],

    [[  0,   0,   0,   0,   0,],
     [  0,   0,   0,   0,   0,],
     [  0,   0, 255, 255,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255, 255, 255,   0,],],
    [[  0,   0,   0,   0,   0,],
     [  0,   0,   0,   0,   0,],
     [  0, 255,   0,   0,   0,],
     [  0, 255, 255,   0,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255, 255,   0,   0,],],
    [[  0,   0,   0,   0,   0,],
     [  0,   0,   0,   0,   0,],
     [  0,   0, 255, 255,   0,],
     [  0, 255,   0,   0,   0,],
     [  0, 255,   0,   0,   0,],
     [  0,   0, 255, 255,   0,],],
    [[  0,   0,   0,   0,   0,],
     [  0,   0,   0,   0,   0,],
     [  0,   0,   0, 255,   0,],
     [  0,   0, 255, 255,   0,],
     [  0, 255,   0, 255,   0,],
     [  0,   0, 255, 255,   0,],],
    [[  0,   0,   0,   0,   0,],
     [  0,   0, 255,   0,   0,],
     [  0, 255,   0, 255,   0,],
     [  0, 255, 255, 255,   0,],
     [  0, 255,   0,   0,   0,],
     [  0,   0, 255, 255,   0,],],
    [[  0,   0,   0,   0,   0,],
     [  0,   0,   0, 255,   0,],
     [  0,   0, 255,   0,   0,],
     [  0, 255, 255, 255,   0,],
     [  0,   0, 255,   0,   0,],
     [  0,   0, 255,   0,   0,],],
]