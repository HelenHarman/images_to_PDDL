import random

import numpy as np

from generate_images import image_pairs, handle_data
from generate_images.hanoi import generate_configs, successors, config_state

## code ##############################################################

image_states = []


disk_height = 4
disk_inc = 2
base_disk_width_factor = 1
base_disk_width = disk_height * base_disk_width_factor

border = 0
tile_factor = 1

configs = None

toh_disks = -1
toh_towers = -1
def generate_single_config_use_glob_options(config):
    return generate([config], toh_disks, toh_towers)[0]

def generate1(config, disks, towers):
    l = len(config)
    if (str(config) in image_states):
        return image_states[image_states.index(str(config))]

    tower_width = disks * (2 * disk_inc) + base_disk_width + border
    tower_height = disks * disk_height
    #figure = np.full([tower_height, tower_width * towers, 3], 255,dtype=np.int8)
    figure = np.full([tower_height, tower_width * towers], 255,dtype=np.int8)
    #figure = np.ones([tower_height,
    #                  tower_width * towers], dtype=np.int8)
    state = config_state(config, disks, towers)
    for i, tower in enumerate(state):
        tower.reverse()
        # print(i,tower)
        x_center = tower_width * i + disks * disk_inc  # lacks base_disk_width
        for j, disk in enumerate(tower):
            # print(j,disk,(l-j)*2)
            figure[
            tower_height - disk_height * (j + 1):
            tower_height - disk_height * j,
            x_center - disk * disk_inc:
            x_center + disk * disk_inc + base_disk_width] \
                = 0 #(0,0,0)#
            # = np.tile(np.tile(patterns[disk],(tile_factor,tile_factor)),
            #           (1,2*disks+base_disk_width_factor))[:,:2 * disk * disk_inc + base_disk_width]
            # = np.tile(np.tile(patterns[disk],(tile_factor,tile_factor)),
            #           (1,disk+base_disk_width_factor))
            # = np.tile(np.tile(patterns[disk],(tile_factor,tile_factor)),
            #           (1,2*disk+base_disk_width_factor))
    image_state = image_pairs.ImageState(str(config), figure)
    image_states.append(image_state)
    return image_state #figure #preprocess(figure)


def generate(configs, disks, towers):
    return np.array([generate1(c, disks, towers) for c in configs])


def transitions(disks, towers, one_per_state=False, single_state = False):
    global configs
    if configs is None:
        configs = list(generate_configs(disks, towers))
    if (single_state):
        index = random.randrange(len(configs))  # #np.random.randint(len(list(configs)), dtype='long')
        c1 = configs[index]  # random.choice(list(configs))
        sucs = successors(c1, disks, towers)
        pre_images = []
        suc_images = []
        for suc in sucs:
            pre, suc = generate([c1, suc], disks, towers)
            pre_images.append(pre)
            suc_images.append(suc)
        return [pre_images, suc_images]  # transitions
    elif one_per_state:
        def pickone(thing):
            index = np.random.randint(0, len(thing))
            return thing[index]

        pre = generate(configs, disks, towers)
        suc = generate(np.array([pickone(successors(c1, disks, towers)) for c1 in configs]), disks, towers)
        return np.array([pre, suc])
    else:
        configs_with_missing = configs.copy()
        num_missing = (float(handle_data.MISSING_PERCENTAGE_OF_PRE_IMAGES) / 100.0) * len(configs_with_missing)
        print(num_missing)
        for i in range(int(num_missing)):
            index = random.randrange(len(configs_with_missing))
            configs_with_missing.pop(index)
        transitions = np.array([[c1, c2] for c1 in configs_with_missing for c2 in successors(c1, disks, towers)])
        pre = generate(transitions[:, 0, :], disks, towers)
        suc = generate(transitions[:, 1, :], disks, towers)

        return np.array([pre, suc])


#directory = "./generated_images/"
#pre = all_transitions[0]
#suc = all_transitions[1]

def generate_image_pairs_for_single_state(options):
    return generate_image_pairs(options, True)

def generate_image_pairs(domain_config=None, single_state=False, use_min_transitions = False):
    global image_states
    global configs
    global toh_disks
    global toh_towers
    configs = None
    image_states.clear()
    handle_data.create_new_datastore("toh", "blocks"+str(domain_config["blocks"])+"_towers"+str(domain_config["towers"]))

    toh_disks = domain_config["blocks"]
    toh_towers = domain_config["towers"]
    #if (not image_pairs.ImageState.keyToImage == None):
    #    image_pairs.ImageState.keyToImage.close()
    #image_pairs.ImageState.keyToImage = handle_data.KeyToImage("toh", "blocks"+str(domain_config["blocks"])+"_towers"+str(domain_config["towers"]))
    #configs = generate_configs(6)
    #puzzles = generate(configs, 2, 3)
    if (domain_config):
        all_transitions = transitions(domain_config["blocks"], domain_config["towers"], False, single_state)
    else:
        all_transitions = transitions(4, 3, False, single_state)
    pre = all_transitions[0]
    suc = all_transitions[1]
    return pre, suc
#for i in range(len(pre)):
 #   imsave(directory + str(i) + "_pre.png", pre[i])
 #   imsave(directory + str(i) + "_suc.png", suc[i])

















##########
def states(disks, towers, configs=None, **kwargs):
    if configs is None:
        configs = generate_configs(disks, towers)
    return generate(configs, disks, towers, **kwargs)

def normalize(image):
    # into 0-1 range
    if image.max() == image.min():
        return image - image.min()
    else:
        return (image - image.min()) / (image.max() - image.min())


#def equalize(image):
 #   from skimage import exposure
  #  return exposure.equalize_hist(image)


def enhance(image):
    return np.clip((image - 0.5) * 3, -0.5, 0.5) + 0.5


def preprocess(image):
    image = image.astype(float)
    #image = equalize(image)
    image = normalize(image)
    image = enhance(image)
    return image


############


## patterns ##############################################################
"""
patterns = [
    [[0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ], ],
    [[1, 1, 1, 1, 1, 1, 1, 1, ],
     [1, 1, 1, 0, 0, 1, 1, 1, ],
     [1, 1, 1, 0, 0, 1, 1, 1, ],
     [1, 1, 1, 0, 0, 1, 1, 1, ],
     [1, 1, 1, 0, 0, 1, 1, 1, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ], ],
    [[1, 1, 0, 0, 1, 1, 0, 0, ],
     [1, 1, 0, 0, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 0, 0, 1, 1, ],
     [0, 0, 1, 1, 0, 0, 1, 1, ],
     [1, 1, 0, 0, 1, 1, 0, 0, ],
     [1, 1, 0, 0, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 0, 0, 1, 1, ],
     [0, 0, 1, 1, 0, 0, 1, 1, ], ],
    [[1, 1, 1, 1, 1, 1, 1, 1, ],
     [1, 1, 0, 0, 0, 0, 1, 1, ],
     [1, 0, 1, 1, 1, 1, 0, 1, ],
     [1, 0, 1, 1, 1, 1, 0, 1, ],
     [1, 0, 1, 1, 1, 1, 0, 1, ],
     [1, 0, 1, 1, 1, 1, 0, 1, ],
     [1, 1, 0, 0, 0, 0, 1, 1, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ], ],
    [[0, 0, 0, 1, 0, 0, 0, 1, ],
     [0, 0, 1, 0, 0, 0, 1, 0, ],
     [0, 1, 0, 0, 0, 1, 0, 0, ],
     [1, 0, 0, 0, 1, 0, 0, 0, ],
     [0, 0, 0, 1, 0, 0, 0, 1, ],
     [0, 0, 1, 0, 0, 0, 1, 0, ],
     [0, 1, 0, 0, 0, 1, 0, 0, ],
     [1, 0, 0, 0, 1, 0, 0, 0, ], ],
    [[1, 1, 1, 1, 1, 1, 1, 1, ],
     [1, 1, 0, 0, 0, 0, 1, 1, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [1, 1, 0, 0, 0, 0, 1, 1, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ], ],
    [[0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 1, 1, 1, 0, 0, 0, 0, ],
     [0, 1, 1, 1, 0, 0, 0, 0, ],
     [0, 1, 1, 1, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 1, 1, 1, 0, ],
     [0, 0, 0, 0, 1, 1, 1, 0, ],
     [0, 0, 0, 0, 1, 1, 1, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ], ],
    [[1, 0, 0, 0, 1, 0, 0, 0, ],
     [0, 1, 0, 0, 0, 1, 0, 0, ],
     [0, 0, 1, 0, 0, 0, 1, 0, ],
     [0, 0, 0, 1, 0, 0, 0, 1, ],
     [1, 0, 0, 0, 1, 0, 0, 0, ],
     [0, 1, 0, 0, 0, 1, 0, 0, ],
     [0, 0, 1, 0, 0, 0, 1, 0, ],
     [0, 0, 0, 1, 0, 0, 0, 1, ], ],
    [[0, 0, 0, 1, 1, 0, 0, 0, ],
     [0, 0, 1, 0, 0, 1, 0, 0, ],
     [0, 1, 0, 0, 0, 0, 1, 0, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [0, 0, 0, 1, 1, 0, 0, 0, ],
     [0, 0, 1, 0, 0, 1, 0, 0, ],
     [0, 1, 0, 0, 0, 0, 1, 0, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ], ],
    [[1, 0, 0, 0, 0, 0, 0, 1, ],
     [0, 1, 0, 0, 0, 0, 1, 0, ],
     [0, 0, 1, 0, 0, 1, 0, 0, ],
     [0, 0, 0, 1, 1, 0, 0, 0, ],
     [1, 0, 0, 0, 0, 0, 0, 1, ],
     [0, 1, 0, 0, 0, 0, 1, 0, ],
     [0, 0, 1, 0, 0, 1, 0, 0, ],
     [0, 0, 0, 1, 1, 0, 0, 0, ], ],
    [[1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ],
     [1, 0, 1, 0, 1, 0, 1, 0, ], ],
    [[1, 1, 1, 1, 1, 1, 1, 1, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ], ],
    [[0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [1, 1, 1, 1, 1, 1, 1, 1, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ],
     [0, 0, 0, 0, 0, 0, 0, 0, ], ],
    [[0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ],
     [0, 0, 1, 1, 1, 1, 0, 0, ], ],
]

patterns = np.array(patterns)

all_transitions = transitions(4, 3)
# print states(4, 3)
"""
"""
 #figure = preprocess(figure)
        #print figure
        viewer = ImageViewer(pre[0])
        viewer.show()
        viewer = ImageViewer(suc[0])
        viewer.show()
        viewer = ImageViewer(pre[1])
        viewer.show()
        viewer = ImageViewer(suc[1])
        viewer.show()
        viewer = ImageViewer(pre[2])
        viewer.show()
        viewer = ImageViewer(suc[2])
        viewer.show()
"""

