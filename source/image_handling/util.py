import numpy as np
import cv2


def get_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

#-------------------------------

def has_non_zero_pixels(image):
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if (image[x,y] != 0):
                return True
    return False

#-------------------------------

def are_images_equal(image1, image2):
    if image1.shape != image2.shape:
        return False
    image_diff = image1 - image2
    #print ("image_diff.shape[0]=" + str(image_diff.shape[0]) + " image_diff.shape[1]="+ str(image_diff.shape[1]))
    #--b, g, r = cv2.split(image_diff)
    return (cv2.countNonZero(image_diff) == 0 )#--and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0)

#-------------------------------

def are_mean_value_of_images_equal(image1, image2):
    sum1_tuple = cv2.mean(image1)
    sum2_tuple = cv2.mean(image2)
    return (sum1_tuple == sum2_tuple)

#-------------------------------

def do_image_objects_with_positions_overlap(image_obj1, image_obj2):
    if image_obj1.min_x > (image_obj2.min_x + image_obj2.imageObject.image.shape[1]) or (image_obj1.min_x + image_obj1.imageObject.image.shape[1]) < image_obj2.min_x:
        return False
    if image_obj1.min_y > (image_obj2.min_y + image_obj2.imageObject.image.shape[0]) or (image_obj1.min_y + image_obj1.imageObject.image.shape[0]) < image_obj2.min_y:
        return False
    return True
    """
    x = max(image_obj1.min_x, image_obj2.min_x)
    y = max(image_obj1.min_y, image_obj2.min_y)
    w = min(image_obj1.min_x + image_obj1.imageObject.image.shape[1], image_obj2.min_x + image_obj2.imageObject.image.shape[1]) - x
    h = min(image_obj1.min_y +  image_obj1.imageObject.image.shape[0], image_obj2.min_y + image_obj2.imageObject.image.shape[0]) - y
    return (w > 0 or h > 0)
    #if w < 0 or h < 0: return ()  # or (0,0,0,0) ?
    #return (x, y, w, h)
    """


"""
index = 0
for image in action_node.image_objects_pre:
    cv2.imshow('image'+str(index), np.uint8(image.imageObject.image))
    index = index +1
for image in action_node.unchanged_objects:
    cv2.imshow('image'+str(index), np.uint8(image.imageObject.image))
    index = index +1
cv2.waitKey(0)
cv2.destroyAllWindows()
"""
"""
index = 0
    for object in all_objects:
        if object.type == ImageObject_Type.OBJECT:
            cv2.imshow('non_matching_object_start_loc'+str(index), np.uint8(object.image))
            index = index+1
    while cv2.getWindowProperty('non_matching_object_start_loc', 0) >= 0:
        keyCode = cv2.waitKey(50)
"""

"""
index = 0
for transition in self.transitions:
    cv2.imshow("transition pre" +str(index), np.uint8(transition.pre_image.get_image()))
    cv2.imshow("transition suc" +str(index), np.uint8(transition.suc_image.get_image()))
    index = index +1
cv2.waitKey(0)
cv2.destroyAllWindows()
"""
#==============================================================================