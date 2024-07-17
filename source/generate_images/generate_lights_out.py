# https://github.com/guicho271828/latplan/blob/def1ff5b99ca588d40e4ffdaf4166ae788da625b/puzzles/lightsout_digital.py
# also need https://github.com/guicho271828/latplan/blob/def1ff5b99ca588d40e4ffdaf4166ae788da625b/puzzles/model/lightsout.py
import copy
import random

import cv2
import numpy as np

from generate_images import handle_data, image_pairs
from generate_images.lights_out import generate_configs, successors

image_states = []

on = [[0, 0, 0, 0, 0, ],
      [0, 0, 255, 0, 0, ],
      [0, 255, 255, 255, 0, ],
      [0, 0, 255, 0, 0, ],
      [0, 0, 0, 0, 0, ], ]

off = [[0, 0, 0, 0, 0, ],
       [0, 0, 0, 0, 0, ],
       [0, 0, 0, 0, 0, ],
       [0, 0, 0, 0, 0, ],
       [0, 0, 0, 0, 0, ], ]

# config representation: on = 1, off = -1 , not zero!!


configs = None
lights_size = -1
def generate_single_config_use_glob_options(config):
    return generate([config])[0]

def generate(configs_local):
    import math
    size = int(math.sqrt(len(configs_local[0])))
    base = 5
    dim = base * size

    def generate(config):
        #config_t = tuple(config)
        if (str(config) in image_states):
            return image_states[image_states.index(str(config))] #config_to_image[str(config)]
        #figure = np.zeros((dim, dim, 3))
        #print (config_t)
        figure = np.zeros((dim, dim))
        for pos, value in enumerate(config):
            x = pos % size
            y = pos // size
            if value > 0:
                figure[y * base:(y + 1) * base,
                x * base:(x + 1) * base] = on
            else:
                figure[y * base:(y + 1) * base,
                x * base:(x + 1) * base] = off

        image_state = image_pairs.ImageState(str(config), figure)
        image_states.append(image_state)
        return image_state #figure

    #return np.array([generate(c) for c in configs]).reshape((-1, dim, dim, 3))
    return np.array([generate(c) for c in configs_local]) #.reshape((-1, dim, dim))


def states(size, configs=None):
    if configs is None:
        configs = generate_configs(size)
    return generate(configs)


def transitions(size, one_per_state=False, single_state=False):
    global configs
    if configs is None:
        configs = list(generate_configs(size))

    if (single_state):
        index = random.randrange(len(configs))  # #np.random.randint(len(list(configs)), dtype='long')
        c1 = configs[index]  # random.choice(list(configs))
        sucs = successors(c1)
        pre_images = []
        suc_images = []
        #print(c1)
        for suc in sucs:
            #print(suc)
            pre, suc = generate([c1, suc])
            pre_images.append(pre)
            suc_images.append(suc)
        return [pre_images, suc_images]  # transitions
    elif one_per_state:
        def pickone(thing):
            index = np.random.randint(0, len(thing))
            return thing[index]

        transitions = np.array([
            generate([c1, pickone(successors(c1))])
            for c1 in configs])
    else:
        configs_with_missing = configs.copy()
        num_missing = (float(handle_data.MISSING_PERCENTAGE_OF_PRE_IMAGES) / 100.0) * len(configs_with_missing)
        print(num_missing)
        for i in range(int(num_missing)):
            index = random.randrange(len(configs_with_missing))
            configs_with_missing.pop(index)

        transitions = np.array([generate([c1, c2])
                                for c1 in configs_with_missing for c2 in successors(c1)])
    return np.einsum('ab...->ba...', transitions)

def get_minimum_transitions(size):
    global configs
    if configs is None:
        configs = list(generate_configs(size))
    pre_images = []
    suc_images = []
    min_transition_configs = get_min_transition_configs()
    for transition_config in min_transition_configs:
        pre_image, suc_image = generate([transition_config[0], transition_config[1]])
        pre_images.append(pre_image)
        suc_images.append(suc_image)
    return [pre_images, suc_images]

#================================================
def generate_image_pairs_for_single_state(options):
    return generate_image_pairs(options, True)

def generate_image_pairs_with_minimal_transitions(options):
    return generate_image_pairs(options, False, True)


def generate_image_pairs(options=None, single_state=False, use_min_transitions = False):
    global image_states
    global configs
    global lights_size
    configs = None

    image_states.clear()

    if (options == None):
        lights_size = 2
    else:
        lights_size = options["size"]
    handle_data.create_new_datastore("spider", "size"+str(lights_size))


    # configs = generate_configs(6)
    # puzzles = generate(configs, 2, 3)
    #if (options == None):
    #    all_transitions = transitions(2, False, single_state)
    if ((not single_state) and lights_size == 3):  #elif (use_min_transitions):
        all_transitions = get_minimum_transitions(lights_size)
    else:
        all_transitions = transitions(lights_size, False, single_state)

    pre = all_transitions[0]
    suc = all_transitions[1]
    return pre, suc

#================================================


def get_min_transition_configs():
    transition_configs = []
    base =[[1,  1,  1], [1,  1,  1],  [1,  1,  1]]
    #base1 =[[-1,  -1,  -1],  [-1,  -1,  -1],  [-1,  -1,  -1]]
    for i in range(len(base[0])):
        for j in range(len(base)):
            if ((i == 1) and (j == 1)):
                bases =[ #[[1, 1, 1], [1, 1, 1], [1, 1, 1]],
                            [[-1, 1, -1], [1, 1, 1], [-1, 1, -1]],
                         [[1, -1, 1],[1, 1, 1], [1, 1, 1]],
                         [[1, -1, 1],[1, -1, 1],[1, 1, 1]],
                         [[1, -1, 1],[-1, -1, 1],[1, 1, 1]],
                         [[1, -1, 1],[-1, -1, -1],[1, 1, 1]],
                         [[1, -1, 1],[-1, -1, -1],[1, -1, 1]], #[[-1, -1, -1],[-1, -1, -1],[-1, -1, -1]]
                        ]
                for state_base in bases:
                    config = gen_config_with_base(i, j, state_base)
                    #--print ("config=" + str(config) + " flatten(base1)= " + str(flatten(state_base)))
                    transition_configs.append([flatten(state_base), config])

            elif ((i == 0) and (j == 0)):
                bases =[ #[[1, 1, 1], [1, 1, 1], [1, 1, 1]],
                            [[1, 1, -1], [1, -1, -1], [-1, -1, -1]],
                         [[-1, 1, 1], [1, 1, 1], [1, 1, 1]],
                         [[-1, -1, 1], [1, 1, 1], [1, 1, 1]],
                         [[-1, -1, 1], [-1, 1, 1], [1, 1, 1]], #[[-1, -1, -1],[-1, -1, -1],[-1, -1, -1]]
                        ]
                for state_base in bases:
                    config = gen_config_with_base(i, j, state_base)
                    transition_configs.append([flatten(state_base), config])
            elif ((i == 2) and (j == 0)):
                bases = [#[[1, 1, 1], [1, 1, 1], [1, 1, 1]],
                            [[-1, -1, 1], [-1, -1, 1], [-1, -1, -1]],
                        # [[-1, -1, 1], [-1, -1, -1], [-1, -1, -1]], [[1, 1, -1], [1, 1, -1], [1, 1, 1]]
                         ]
                for state_base in bases:
                    config = gen_config_with_base(i, j, state_base)
                    transition_configs.append([flatten(state_base), config])
            elif ((i == 1) and (j == 2)):
                bases =[ #[[1, 1, 1], [1, 1, 1], [1, 1, 1]],
                            [[-1, -1, -1], [-1, 1, -1], [1, 1, 1]],
                         [[1, 1, 1], [1, -1, 1], [-1, -1, -1]],
                         [[1, 1, 1], [1, 1, 1], [-1, -1, -1]],
                         [[1, 1, 1], [1, 1, 1], [1, -1, -1]],
                         [[1, 1, 1], [1, 1, 1], [1, 1, -1]], #[[-1, -1, -1],[-1, -1, -1],[-1, -1, -1]]
                         ]
                for state_base in bases:
                    config = gen_config_with_base(i, j, state_base)
                    transition_configs.append([flatten(state_base), config])
            else:
                config = gen_config_with_base(i, j, base)
                transition_configs.append([flatten(base), config])
                #config = gen_config_with_base(i, j, base1)
                #transition_configs.append([flatten(base1), config])
    #print("transition_configs=" + str(len(transition_configs)))
    #print("transition_configs=" + str(transition_configs[0]))
    """
    states = generate(transition_configs[0])
    cv2.imshow('A ', np.uint8(states[0].get_image()))
    cv2.imshow('B ', np.uint8(states[1].get_image()))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """
    return transition_configs

def gen_config_with_base(i,j, base):
    config = copy.deepcopy(base)
    #print("pre=" + str(config))
    config[j][i] *= -1
    if (i > 0):
        config[j][i - 1] *= -1
    if (j > 0):
        config[j - 1][i] *= -1
    if (i < len(base) - 1):
        config[j][i + 1] *= -1
    if (j < len(base[0]) - 1):
        config[j + 1][i] *= -1

    print("suc=" + str(config))
    return flatten(config)


def flatten(config):
    flat_config = []
    for c in config:
        flat_config.extend(c)
    return flat_config



#=================================================================
#=================================================================