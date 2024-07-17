import os

import lmdb
import numpy as np
import pickle

from generate_images import image_pairs

MISSING_PERCENTAGE_OF_PRE_IMAGES = 0

def update_missing_precentage_of_pre_images(amount):
    global MISSING_PERCENTAGE_OF_PRE_IMAGES
    MISSING_PERCENTAGE_OF_PRE_IMAGES = amount


def create_new_datastore(domain_name, option_id):
    if (not image_pairs.ImageState.keyToImage == None):
        image_pairs.ImageState.keyToImage.close()
    image_pairs.ImageState.keyToImage = KeyToImage(domain_name, option_id)
"""
class KeyToImage:

    def __init__(self, domain_name, option_id):
        #    number of states/images * size-of(float) * number of pixels
        map_size = 365000 * 8 * 5100 #images[0].nbytes * 10
        if not os.path.exists("./lmdb/"):
            os.makedirs("./lmdb/")
        self.env = lmdb.open("./lmdb/"+domain_name+ "_" + option_id, map_size=map_size)

    def write_data(self, key, image):
        # Start a new write transaction
        with self.env.begin(write=True) as txn:
            # All key-value pairs need to be strings
            txn.put(str(key).encode(), pickle.dumps(image))# str(image).encode())

    def read_image(self, key):
        with self.env.begin(write=True) as txn:
            read_in_image_string = txn.get(str(key).encode())
            return np.loads(read_in_image_string)

    def close(self):
        self.env.close()

"""
class KeyToImage: #without file store

    def __init__(self, domain_name, option_id):
        self.data = {}

    def write_data(self, key, image):
        self.data[str(key)] = image

    def read_image(self, key):
        return self.data[str(key)]

    def close(self):
        self.data.clear()



