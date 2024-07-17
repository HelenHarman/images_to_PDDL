import random

import cv2
import numpy as np
from generate_images import handle_data, image_pairs
from generate_images.puzzle import generate_configs, successors, split_image
import os

panels = None

base = 21

MANDRILL_FILE_PATH = "../../generate_images/mandrill.png"

image_states = []
configs = None

mandrill_width = -1
mandrill_height = -1
def generate_single_config_use_glob_options(config):
    return generate([config], mandrill_width, mandrill_height)[0]

def generate(configs, width, height):
    global panels
    if panels is None:
        panels  = split_image(os.path.join(os.path.dirname(__file__), MANDRILL_FILE_PATH),width,height)
        stepy = panels[0].shape[0]//base
        stepx = panels[0].shape[1]//base
        panels = panels[:,::stepy,::stepx][:,:base,:base].round()
    assert width*height <= 9
    dim_x = base*width
    dim_y = base*height
    def generate(config):
        if (str(config) in image_states):
            return image_states[image_states.index(str(config))]  # config_to_image[str(config)]
        #figure = np.zeros((dim_y,dim_x))
        figure = np.zeros((dim_y+height-1,dim_x+width-1))
        for digit, pos in enumerate(config):
            x = pos % width
            y = pos // width
            figure[y*(base):(y+1)*(base),
                   x*(base):(x+1)*(base)] = panels[digit]

        image_state = image_pairs.ImageState(str(config), figure)
        #if (str(config) not in image_states):
        image_states.append(image_state)
        return image_state
    return np.array([ generate(c) for c in configs ]) #.reshape((-1,dim_y,dim_x))


def transitions(width, height, one_per_state=False, single_state=False):
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
    elif one_per_state:
        def pickone(thing):
            index = np.random.randint(0,len(thing))
            return thing[index]
        transitions = np.array([
            generate(
                [c1,pickone(successors(c1,width,height))],width,height)
            for c1 in configs ])
    else:
        configs_with_missing = configs.copy()
        num_missing = (float(handle_data.MISSING_PERCENTAGE_OF_PRE_IMAGES) / 100.0) * len(configs_with_missing)
        print(num_missing)
        for i in range(int(num_missing)):
            index = random.randrange(len(configs_with_missing))
            configs_with_missing.pop(index)
        transitions = np.array([ generate([c1,c2],width,height)
                                 for c1 in configs_with_missing for c2 in successors(c1,width,height) ])
    return np.einsum('ab...->ba...',transitions)


def generate_image_pairs_for_single_state(options):
    return generate_image_pairs(options, True)


def generate_image_pairs(options=None, single_state=False, use_min_transitions = False):
    global panels
    global image_states
    global configs
    global mandrill_width
    global mandrill_height
    configs = None
    panels = None
    image_states.clear()

    if (options == None):
        mandrill_width = 2
        mandrill_height = 2
    else:
        mandrill_width = options["width"]
        mandrill_height = options["height"]

    handle_data.create_new_datastore("mandrill", "width"+str(mandrill_width)+"_height"+str(mandrill_height))

    all_transitions = transitions(mandrill_width, mandrill_height, False, single_state)


    return all_transitions[0], all_transitions[1]