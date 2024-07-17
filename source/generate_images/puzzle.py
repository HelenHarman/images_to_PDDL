import numpy as np


#from scipy import misc
import cv2

def split_image(path,width,height):
    #img = misc.imread(path,True)/256
    img = cv2.imread(path) #,True)/256 # 0 == grey
    # convert the image to *greyscale*
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #(thresh, blackAndWhiteImage) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    """
    img2 = np.zeros_like(img)
    img2[:, :, 0] = gray
    img2[:, :, 1] = gray
    img2[:, :, 2] = gray
    """
    W = gray.shape[1]
    H = gray.shape[0]
    dW, dH = W // width, H // height



    return np.array([
        gray[dH*i:dH*(i+1), dH*j:dH*(j+1)]
        for i in range(width)
        for j in range(height) ])
    """
    W = img.shape[1]
    H = img.shape[0]
    dW, dH = W//width, H//height
    return np.array([
        img[dH*i:dH*(i+1), dH*j:dH*(j+1)]
        for i in range(width)
        for j in range(height) ])
    """
def generate_configs(digit=9):
    import itertools
    return itertools.permutations(range(digit))

def successors(config,width,height):
    pos = config[0]
    x = pos % width
    y = pos // width
    succ = []
    try:
        if x != 0:
            dir=1
            c = list(config)
            other = next(i for i,_pos in enumerate(c) if _pos == pos-1)
            c[0] -= 1
            c[other] += 1
            succ.append(c)
        if x != width-1:
            dir=2
            c = list(config)
            other = next(i for i,_pos in enumerate(c) if _pos == pos+1)
            c[0] += 1
            c[other] -= 1
            succ.append(c)
        if y != 0:
            dir=3
            c = list(config)
            other = next(i for i,_pos in enumerate(c) if _pos == pos-width)
            c[0] -= width
            c[other] += width
            succ.append(c)
        if y != height-1:
            dir=4
            c = list(config)
            other = next(i for i,_pos in enumerate(c) if _pos == pos+width)
            c[0] += width
            c[other] -= width
            succ.append(c)
        return succ
    except StopIteration:
        board = np.zeros((height,width))
        for i in range(height*width):
            _pos = config[i]
            _x = _pos % width
            _y = _pos // width
            board[_y,_x] = i
        print(board)
        print(succ)
        print(dir)
        print((c,x,y,width,height))







min_transition_configs = [
   [(0,1,2,3,4,5,6,7,8), (1,0,2,3,4,5,6,7,8) ], #0,1
   [(0,4,1,3,2,6,5,8,7), (3,4,1,0,2,6,5,8,7) ], #0,3  #[(0,1,2,3,4,5,6,7,8), (3,1,2,0,4,5,6,7,8) ], #0,3

    #(0, 1),
   #[(1,0,2,3,4,5,6,7,8), (2,0,1,3,4,5,6,7,8) ], #1,2
   [(1,2,0,5,4,3,7,8,6), (4,2,0,5,1,3,7,8,6) ], #1,4   #[(1,0,2,3,4,5,6,7,8), (4,0,2,3,1,5,6,7,8) ], #1,4

    #(0,3)
   #[(3,1,2,0,4,5,6,7,8), (6,1,2,0,4,5,3,7,8) ], #3,6
   [(3,0,1,2,4,6,5,8,7) , (4,0,1,2,3,6,5,8,7) ], #3,4  #(3,1,2,0,4,5,6,7,8), (4,1,2,0,3,5,6,7,8) ], #3,4

    #(0, 1), (1,2)
   [(2,0,1,3,4,5,6,7,8), (5,0,1,3,4,2,6,7,8) ], #2,5
   [(2,3,1,0,5,4,7,8,6), (1,3,2,0,5,4,7,8,6) ], #2,1 #[(2,0,1,3,4,5,6,7,8), (1,0,2,3,4,5,6,7,8) ], #2,1

    #(0, 1), (1,4)
   #[(4,0,2,3,1,5,6,7,8), (5,0,2,3,1,4,6,7,8) ], #4,5
   [(4,2,0,1,3,7,6,8,5), (7,2,0,1,3,4,6,8,5) ], #4,7 #[(4,0,2,3,1,5,6,7,8), (7,0,2,3,1,5,6,4,8) ], #4,7

    #(0,3), (3,6)
   [(6,1,2,0,4,5,3,7,8), (3,1,2,0,4,5,6,7,8) ], #6,3
   [(6,2,1,4,0,3,8,7,5), (7,2,1,4,0,3,8,6,5) ], #6,7 #[(6,1,2,0,4,5,3,7,8), (7,1,2,0,4,5,3,6,8) ], #6,7

    #(0, 1), (1,2), (2,5)
   [(5,0,1,3,4,2,6,7,8), (4,0,1,3,5,2,6,7,8) ], #5,4
   [(5,1,0,4,3,6,7,2,8), (8,1,0,4,3,6,7,2,5) ], #5,8 #[(5,0,1,3,4,2,6,7,8), (8,0,1,3,4,2,6,7,5) ], #5,8

    #(0, 1), (1,4), (4,7)
   #[(7,0,2,3,1,5,6,4,8), (6,0,2,3,1,5,7,4,8) ], #7,6
   #[(7,2,0,1,3,6,4,5,8), (8,2,0,1,3,6,4,5,7) ], #7,8 #[(7,0,2,3,1,5,6,4,8), (8,0,2,3,1,5,6,4,7) ], #7,8

    #(0, 1), (1,2), (2,5), (5,8)
   #[(8,0,1,3,4,2,6,7,5), (5,0,1,3,4,2,6,7,8) ], #8,5
   [(8,1,0,4,3,6,5,7,2), (7,1,0,4,3,6,5,8,2) ], #8,7 #[(8,0,1,3,4,2,6,7,5), (7,0,1,3,4,2,6,8,5) ], #8,7
]


