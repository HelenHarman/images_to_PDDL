import numpy as np
from puzzle import generate_configs, successors, split_image
from skimage.io import imsave
import os
import cv2

panels = None

def generate(configs, width, height):
    global panels
    if panels is None:
        panels  = split_image(os.path.join(os.path.dirname(__file__), "spider.png"),width,height)
        stepy = panels[0].shape[0]//28
        stepx = panels[0].shape[1]//28
        panels = panels[:,::stepy,::stepx][:,:28,:28].round()
    assert width*height <= 9
    base_width = 28
    base_height = 28
    dim_x = base_width*width
    dim_y = base_height*height
    def generate(config):
        figure = np.zeros((dim_y+height-1,dim_x+width-1))
        for digit,pos in enumerate(config):
            x = pos % width
            y = pos // width
            figure[y*(base_width+1):(y+1)*(base_width+1)-1,
                   x*(base_width+1):(x+1)*(base_width+1)-1] = panels[digit]
        return preprocess(figure)
    return np.array([ generate(c) for c in configs ]).reshape((-1,dim_y+height-1,dim_x+width-1))

def states(width, height, configs=None):
    digit = width * height
    if configs is None:
        configs = generate_configs(digit)
    return generate(configs,width,height)

def transitions(width, height, configs=None, one_per_state=False):
    digit = width * height
    if configs is None:
        configs = generate_configs(digit)
    if one_per_state:
        def pickone(thing):
            index = np.random.randint(0,len(thing))
            return thing[index]
        transitions = np.array([
            generate(
                [c1,pickone(successors(c1,width,height))],width,height)
            for c1 in configs ])
    else:		
        transitions = np.array([ generate([c1,c2],width,height)
                                 for c1 in configs for c2 in successors(c1,width,height) ])
    return np.einsum('ab...->ba...',transitions)



##########

def normalize(image):
    # into 0-1 range
    if image.max() == image.min():
        return image - image.min()
    else:
        return (image - image.min())/(image.max() - image.min())

def equalize(image):
    from skimage import exposure
    return exposure.equalize_hist(image)

def enhance(image):
    return np.clip((image-0.5)*3,-0.5,0.5)+0.5

def preprocess(image):
    image = image.astype(float)
    #image = equalize(image)
    image = normalize(image)
    image = enhance(image)
    return image
############


#configs = generate_configs(6)
#puzzles = generate(configs, 2, 3)
all_transitions = transitions(2,2)
directory = "./generated_images/"
pre = all_transitions[0]
suc = all_transitions[1]
for i in range(len(pre)):	
	
	imsave(directory+str(i)+"_pre.png", pre[i])
	imsave(directory+str(i)+"_suc.png", suc[i])
	#exit(0)

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
