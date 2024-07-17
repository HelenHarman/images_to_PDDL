import random

import cv2
import numpy as np

from generate_images import handle_data, image_pairs
from generate_images.puzzle import generate_configs, successors, split_image
import os

panels = None

SPIDER_FILE_PATH = "../../generate_images/spider.png"



#config_to_image = {}
image_states = []
configs = None

spider_width = -1
spider_height = -1
def generate_single_config_use_glob_options(config):
    return generate([config], spider_width, spider_height)[0]
    """
    global panels
    #global config_to_image
    if panels is None:
        panels  = split_image(os.path.join(os.path.dirname(__file__), SPIDER_FILE_PATH),spider_width,spider_height)
        stepy = panels[0].shape[0]//28
        stepx = panels[0].shape[1]//28
        panels = panels[:,::stepy,::stepx][:,:28,:28].round()
    assert spider_width*spider_height <= 9
    base_width = 28
    base_height = 28
    dim_x = base_width*spider_width
    dim_y = base_height*spider_height
    def generate(config):
        if (str(config) in image_states):
            return image_states[image_states.index(str(config))] #config_to_image[str(config)]
        #figure = np.zeros((dim_y+height-1,dim_x+width-1,3))
        figure = np.zeros((dim_y+spider_height-1,dim_x+spider_width-1))
        for digit,pos in enumerate(config):
            x = pos % spider_width
            y = pos // spider_width
            #print ("...")
            #print (y*(base_width+1))
            #print ((y+1)*(base_width+1)-1)
            #print (x*(base_width+1))
            #print ((x+1)*(base_width+1)-1)
            #print (digit)
            figure[y*(base_width+1):(y+1)*(base_width+1)-1,
                   x*(base_width+1):(x+1)*(base_width+1)-1] = panels[digit]
        image_state = image_pairs.ImageState(str(config), figure)
        #config_to_image[str(config)] = figure
        #print(str(config))
        image_states.append(image_state)
        #print(len(image_states))
        return image_state #figure  #preprocess(figure)
    #return np.array([ generate(c) for c in configs ]).reshape((-1,dim_y+height-1,dim_x+width-1,3))
    return generate(config)#np.array([ generate() for c in configs ])#.reshape((-1,dim_y+height-1,dim_x+width-1))
    """



def generate(configs, width, height):
    global panels
    #global config_to_image
    if panels is None:
        panels  = split_image(os.path.join(os.path.dirname(__file__), SPIDER_FILE_PATH),width,height)
        stepy = panels[0].shape[0]//28
        stepx = panels[0].shape[1]//28
        panels = panels[:,::stepy,::stepx][:,:28,:28].round()
    assert width*height <= 9
    base_width = 28
    base_height = 28
    dim_x = base_width*width
    dim_y = base_height*height
    def generate(config):
        if (str(config) in image_states):
            return image_states[image_states.index(str(config))] #config_to_image[str(config)]
        #figure = np.zeros((dim_y+height-1,dim_x+width-1,3))
        figure = np.zeros((dim_y+height-1,dim_x+width-1))
        for digit,pos in enumerate(config):
            x = pos % width
            y = pos // width
            #print ("...")
            #print (y*(base_width+1))
            #print ((y+1)*(base_width+1)-1)
            #print (x*(base_width+1))
            #print ((x+1)*(base_width+1)-1)
            #print (digit)
            figure[y*(base_width+1):(y+1)*(base_width+1)-1,
                   x*(base_width+1):(x+1)*(base_width+1)-1] = panels[digit]
        image_state = image_pairs.ImageState(str(config), figure)
        #config_to_image[str(config)] = figure
        #print(str(config))
        image_states.append(image_state)
        #print(len(image_states))
        return image_state #figure  #preprocess(figure)
    #return np.array([ generate(c) for c in configs ]).reshape((-1,dim_y+height-1,dim_x+width-1,3))
    return np.array([ generate(c) for c in configs ])#.reshape((-1,dim_y+height-1,dim_x+width-1))

def states(width, height, configs=None):
    digit = width * height
    if configs is None:
        configs = generate_configs(digit)
    return generate(configs,width,height)

def transitions(width, height, one_per_state=False, single_state=False):
    global configs
    digit = width * height
    if configs is None:
        configs = list(generate_configs(digit))

    #config_list = list(configs)
    if (single_state):
        index = random.randrange(len(configs)) # #np.random.randint(len(list(configs)), dtype='long')
        c1 = configs[index] #random.choice(list(configs))
        sucs = successors(c1,width,height)
        transitions = []
        #print(c1)

        #index = 0
        pre_images = []
        suc_images = []
        for suc in sucs:
            #print(suc)
            pre,suc = generate([c1, suc], width, height)
            pre_images.append(pre)
            suc_images.append(suc)
            #transitions.append(generate([c1,suc],width,height)) #[c1, suc]
            #cv2.imshow("transition pre" + str(index), np.uint8(transitions[len(transitions)-1].get_image()))
            #cv2.imshow("transition suc" + str(index), np.uint8(transitions[len(transitions)-1].get_image()))
            #index = index + 1
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        return [pre_images, suc_images]#transitions
    elif (one_per_state):
        def pickone(thing):
            index = np.random.randint(0,len(thing))
            return thing[index]
        transitions = np.array([generate([c1,pickone(successors(c1,width,height))],width,height)for c1 in configs ])
    else:
        configs_with_missing = configs.copy()
        num_missing = (float(handle_data.MISSING_PERCENTAGE_OF_PRE_IMAGES) / 100.0) * len(configs_with_missing)
        print(num_missing)
        print(len(configs_with_missing) - num_missing)
        for i in range(int(num_missing)):
            index = random.randrange(len(configs_with_missing))
            configs_with_missing.pop(index)
        #print (sum(1 for ignore in configs))
        transitions = np.array([ generate([c1,c2],width,height)
                                 for c1 in configs_with_missing for c2 in successors(c1,width,height) ])



    return np.einsum('ab...->ba...',transitions)



##########

def normalize(image):
    # into 0-1 range
    if image.max() == image.min():
        return image - image.min()
    else:
        return (image - image.min())/(image.max() - image.min())



def enhance(image):
    return np.clip((image-0.5)*3,-0.5,0.5)+0.5

def preprocess(image):
    image = image.astype(float)
    image = normalize(image)
    image = enhance(image)
    return image
############

def generate_image_pairs_for_single_state(options):
    return generate_image_pairs(options, True)
"""
def generate_image_pairs_for_single_state(options):
    global panels
    global image_states
    global configs
    global spider_width
    global spider_height
    configs = None
    panels = None
    image_states.clear()

    handle_data.create_new_datastore("single_spider", "width" + str(options["width"]) + "_height" + str(options["height"]))

    spider_width = options["width"]
    spider_height = options["height"]


    all_transitions = transitions(options["width"], options["height"], None, False, True)
    pre = all_transitions[0]
    suc = all_transitions[1]
    return pre, suc
"""
def generate_image_pairs(options=None, single_state=False, use_min_transitions = False):
    #options["width"] = 3
    #options["height"] = 3
    #generate_image_pairs_for_single_state(options)
    global panels
    global image_states
    global configs
    global spider_width
    global spider_height
    configs = None
    panels = None
    image_states.clear()

    handle_data.create_new_datastore("spider", "width"+str(options["width"])+"_height"+str(options["height"]))
    spider_width = options["width"]
    spider_height = options["height"]

   # if (not image_pairs.ImageState.keyToImage == None):
   #     image_pairs.ImageState.keyToImage.close()

    #image_pairs.ImageState.keyToImage = handle_data.KeyToImage("spider", "width"+str(options["width"])+"_height"+str(options["height"]))

    #configs = generate_configs(6)
    #puzzles = generate(configs, 2, 3)
    if (options == None):
        all_transitions = transitions(2, 2, False, single_state)
        #all_transitions = transitions(2,2)
    else:
        all_transitions = transitions(options["width"],options["height"], False, single_state)
        #all_transitions = transitions(options["width"],options["height"])
    #print("return...")
    """
    for pre in all_transitions[0]:
        print(pre)
        keyToImg.write_data("test", pre)
        print (keyToImg.get_data("test"))

        exit(0)
    """
    pre = all_transitions[0]
    suc = all_transitions[1]
    return pre, suc
    """
    directory = "./generated_images/"
    for i in range(len(pre)):
        imsave(directory+str(i)+"_pre.png", pre[i])
        imsave(directory+str(i)+"_suc.png", suc[i])
        #exit(0)
    """
"""
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    def plot_image(a,name):
        plt.figure(figsize=(6,6))
        plt.imshow(a,interpolation='nearest',cmap='gray',)
        plt.savefig(name)
    def plot_grid(images,name="plan.png"):
        import matplotlib.pyplot as plt
        l = len(images)
        w = 6
        h = max(l//6,1)
        plt.figure(figsize=(20, h*2))
        for i,image in enumerate(images):
            # display original
            ax = plt.subplot(h,w,i+1)
            plt.imshow(image,interpolation='nearest',cmap='gray',)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
        plt.savefig(name)
    configs = generate_configs(6)
    puzzles = generate(configs, 2, 3)
    print(puzzles[10])
    plot_image(puzzles[10],"spider_puzzle.png")
    plot_grid(puzzles[:36],"spider_puzzles.png")
    _transitions = transitions(2,3)
    import numpy.random as random
    indices = random.randint(0,_transitions[0].shape[0],18)
    _transitions = _transitions[:,indices]
    print(_transitions.shape)
    transitions_for_show = \
        np.einsum('ba...->ab...',_transitions) \
          .reshape((-1,)+_transitions.shape[2:])
    print(transitions_for_show.shape)
    plot_grid(transitions_for_show,"spider_puzzle_transitions.png")
"""