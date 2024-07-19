
import numpy as np
from hanoi import generate_configs, successors, config_state
import math

from skimage import data
from skimage.viewer import ImageViewer
from skimage.io import imsave #imsave(fname, arr[, plugin,])
import cv2

## code ##############################################################

disk_height = 4
disk_inc = 2
base_disk_width_factor = 1
base_disk_width = disk_height * base_disk_width_factor

border = 0
tile_factor = 1

def generate1(config,disks,towers, **kwargs):
    l = len(config)
    tower_width  = disks * (2*disk_inc) + base_disk_width + border
    tower_height = disks*disk_height
    figure = np.ones([tower_height,
                      tower_width*towers],dtype=np.int8)
    state = config_state(config,disks,towers)
    for i, tower in enumerate(state):
        tower.reverse()
        # print(i,tower)
        x_center = tower_width *  i + disks * disk_inc # lacks base_disk_width
        for j,disk in enumerate(tower):
            # print(j,disk,(l-j)*2)
            figure[
                tower_height - disk_height * (j+1) :
                tower_height - disk_height * j,
                x_center - disk * disk_inc :
                x_center + disk * disk_inc + base_disk_width] \
                = 0
                # = np.tile(np.tile(patterns[disk],(tile_factor,tile_factor)),
                #           (1,2*disks+base_disk_width_factor))[:,:2 * disk * disk_inc + base_disk_width]
                # = np.tile(np.tile(patterns[disk],(tile_factor,tile_factor)),
                #           (1,disk+base_disk_width_factor))
                # = np.tile(np.tile(patterns[disk],(tile_factor,tile_factor)),
                #           (1,2*disk+base_disk_width_factor))
	
    return preprocess(figure)

def generate(configs,disks,towers, **kwargs):
	
    return np.array([ generate1(c,disks,towers, **kwargs) for c in configs ])
                

def states(disks, towers, configs=None, **kwargs):
    if configs is None:
        configs = generate_configs(disks, towers)
    return generate(configs,disks,towers, **kwargs)


def transitions(disks, towers, configs=None, one_per_state=False, **kwargs):
    if configs is None:
        configs = generate_configs(disks, towers)
    if one_per_state:
        def pickone(thing):
            index = np.random.randint(0,len(thing))
            return thing[index]
        pre = generate(configs, disks, towers, **kwargs)
        suc = generate(np.array([pickone(successors(c1, disks, towers)) for c1 in configs ]), disks, towers, **kwargs)
        return np.array([pre, suc])
    else:
        transitions = np.array([ [c1,c2] for c1 in configs for c2 in successors(c1, disks, towers) ])
        pre = generate(transitions[:,0,:], disks, towers, **kwargs)
        suc = generate(transitions[:,1,:], disks, towers, **kwargs)
       
        return np.array([pre, suc])



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
    image = equalize(image)
    image = normalize(image)
    image = enhance(image)
    return image
############



## patterns ##############################################################

patterns = [
    [[0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],],
    [[1,1,1,1,1,1,1,1,],
     [1,1,1,0,0,1,1,1,],
     [1,1,1,0,0,1,1,1,],
     [1,1,1,0,0,1,1,1,],
     [1,1,1,0,0,1,1,1,],
     [1,0,0,0,0,0,0,1,],
     [1,0,0,0,0,0,0,1,],
     [1,1,1,1,1,1,1,1,],],
    [[1,1,0,0,1,1,0,0,],
     [1,1,0,0,1,1,0,0,],
     [0,0,1,1,0,0,1,1,],
     [0,0,1,1,0,0,1,1,],
     [1,1,0,0,1,1,0,0,],
     [1,1,0,0,1,1,0,0,],
     [0,0,1,1,0,0,1,1,],
     [0,0,1,1,0,0,1,1,],],
    [[1,1,1,1,1,1,1,1,],
     [1,1,0,0,0,0,1,1,],
     [1,0,1,1,1,1,0,1,],
     [1,0,1,1,1,1,0,1,],
     [1,0,1,1,1,1,0,1,],
     [1,0,1,1,1,1,0,1,],
     [1,1,0,0,0,0,1,1,],
     [1,1,1,1,1,1,1,1,],],
    [[0,0,0,1,0,0,0,1,],
     [0,0,1,0,0,0,1,0,],
     [0,1,0,0,0,1,0,0,],
     [1,0,0,0,1,0,0,0,],
     [0,0,0,1,0,0,0,1,],
     [0,0,1,0,0,0,1,0,],
     [0,1,0,0,0,1,0,0,],
     [1,0,0,0,1,0,0,0,],],
    [[1,1,1,1,1,1,1,1,],
     [1,1,0,0,0,0,1,1,],
     [1,0,0,0,0,0,0,1,],
     [1,0,0,0,0,0,0,1,],
     [1,0,0,0,0,0,0,1,],
     [1,0,0,0,0,0,0,1,],
     [1,1,0,0,0,0,1,1,],
     [1,1,1,1,1,1,1,1,],],
    [[0,0,0,0,0,0,0,0,],
     [0,1,1,1,0,0,0,0,],
     [0,1,1,1,0,0,0,0,],
     [0,1,1,1,0,0,0,0,],
     [0,0,0,0,1,1,1,0,],
     [0,0,0,0,1,1,1,0,],
     [0,0,0,0,1,1,1,0,],
     [0,0,0,0,0,0,0,0,],],
    [[1,0,0,0,1,0,0,0,],
     [0,1,0,0,0,1,0,0,],
     [0,0,1,0,0,0,1,0,],
     [0,0,0,1,0,0,0,1,],
     [1,0,0,0,1,0,0,0,],
     [0,1,0,0,0,1,0,0,],
     [0,0,1,0,0,0,1,0,],
     [0,0,0,1,0,0,0,1,],],
    [[0,0,0,1,1,0,0,0,],
     [0,0,1,0,0,1,0,0,],
     [0,1,0,0,0,0,1,0,],
     [1,0,0,0,0,0,0,1,],
     [0,0,0,1,1,0,0,0,],
     [0,0,1,0,0,1,0,0,],
     [0,1,0,0,0,0,1,0,],
     [1,0,0,0,0,0,0,1,],],
    [[1,0,0,0,0,0,0,1,],
     [0,1,0,0,0,0,1,0,],
     [0,0,1,0,0,1,0,0,],
     [0,0,0,1,1,0,0,0,],
     [1,0,0,0,0,0,0,1,],
     [0,1,0,0,0,0,1,0,],
     [0,0,1,0,0,1,0,0,],
     [0,0,0,1,1,0,0,0,],],
    [[1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],
     [1,0,1,0,1,0,1,0,],],
    [[1,1,1,1,1,1,1,1,],
     [0,0,0,0,0,0,0,0,],
     [1,1,1,1,1,1,1,1,],
     [0,0,0,0,0,0,0,0,],
     [1,1,1,1,1,1,1,1,],
     [0,0,0,0,0,0,0,0,],
     [1,1,1,1,1,1,1,1,],
     [0,0,0,0,0,0,0,0,],],
    [[0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],
     [1,1,1,1,1,1,1,1,],
     [1,1,1,1,1,1,1,1,],
     [1,1,1,1,1,1,1,1,],
     [1,1,1,1,1,1,1,1,],
     [0,0,0,0,0,0,0,0,],
     [0,0,0,0,0,0,0,0,],],
    [[0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],
     [0,0,1,1,1,1,0,0,],],
]

patterns = np.array(patterns)



all_transitions = transitions(4, 3)
#print states(4, 3)
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
directory = "./generated_images/"
pre = all_transitions[0]
suc = all_transitions[1]
for i in range(len(pre)):
	imsave(directory+str(i)+"_pre.png", pre[i])
	imsave(directory+str(i)+"_suc.png", suc[i])



