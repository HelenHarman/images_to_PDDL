import numpy as np


from scipy import misc

def split_image(path,width,height):
    img = misc.imread(path,True)/256
    # convert the image to *greyscale*
    W, H = img.shape
    dW, dH = W//width, H//height
    return np.array([
        img[dH*i:dH*(i+1), dH*j:dH*(j+1)]
        for i in range(width)
        for j in range(height) ])

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
