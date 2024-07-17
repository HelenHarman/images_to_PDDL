#=============================================
## SCRATCH ###

#from sklearn.cluster import KMeans
#from action_graph.action_node import ActionNode, ActionNode_Type
#from image_handling.image_area import ImageArea, ImageObject, ImageObjectWithPosition, ImagePointForSwapActionRectangle
#from scipy import optimize

#unchanged_pixels_count_threshold = 0 # i.e. how many pixels should be unchanged before next object is reached.
#unchanged_pixel_value_threshold = 0 # i.e. how far off black (i.e. unchanged)

#--------------------------------------------
def parse_images(image_directory):

    image_objects = []
    action_nodes = []

    for file in os.listdir(image_directory):
        if "pre.png" not in file:
            continue
        pre_image_file = image_directory + file
        suc_image_file = image_directory + file.replace("pre.png", "suc.png")
        print (pre_image_file)
        print (suc_image_file)

        img_pre = np.int32(cv2.imread(pre_image_file)) #image_directory+'0_pre.png'))
        img_suc = np.int32(cv2.imread(suc_image_file)) #image_directory+'0_suc.png'))
        img_add_eff = img_suc - img_pre
        img_del_eff = img_pre - img_suc

        cv2.imshow('img_add_eff', np.uint8(img_add_eff))
        cv2.imshow('img_del_eff', np.uint8(img_del_eff))
        cv2.imshow('img_pre', np.uint8(img_pre))
        cv2.imshow('img_suc', np.uint8(img_suc))

        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #exit(0)

       # action = ActionNode(img_pre, img_suc)
        if (is_swap_action(img_add_eff, img_del_eff)):
            image_areas = find_area_of_swap_method_2(img_pre, img_suc, img_add_eff, img_del_eff) #find_area_of_swap(img_pre, img_suc, img_add_eff, img_del_eff)
            action_node, image_objects = create_action_node_for_swap(image_areas, img_pre, img_suc, image_objects)
            action_nodes.append(action_node)

    print (len(image_objects))
    print(len(action_nodes))
    index = 0
    for image in image_objects:
        cv2.imshow('img'+str(index), np.uint8(image.image))
        index = index +1


    return action_nodes, image_objects
def is_swap_action(img_add_eff, img_del_eff): # TODO fix this
    added_images = img_add_eff + img_del_eff
    b, g, r = cv2.split(added_images)
    cv2.imshow('difference', np.uint8(added_images))
    if (not ( cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0 )):
        return False

    return True

#--------------------------------------------

def create_image_objects(image_objects, image_areas, img):
    print("image_areas=" + str(len(image_areas)))
    image_objects_with_locations = []
    for image_area  in image_areas:
        pos1, pos2 = image_area.get_positions()
        print (pos1, pos2)
        crop_img = img[pos1[1]:pos2[1], pos1[0]:pos2[0]]
        image_object = next((x for x in image_objects if x.isEquivalent(crop_img)), None)
        if (image_object is None):
            image_object = ImageObject(crop_img)
            image_objects.append(image_object)
        image_objects_with_locations.append(ImageObjectWithPosition(image_object, pos1[0], pos1[1]))

    return image_objects_with_locations, image_objects

#--------------------------------------------

###########################################################################################################
###                          Functions for swap action iamge parsing                                    ###

def create_action_node_for_swap(image_areas, img_pre, img_suc, image_objects):
    #image_objects = []
    image_objects_pre, image_objects = create_image_objects(image_objects, image_areas, img_pre)
    image_objects_suc, image_objects = create_image_objects(image_objects, image_areas, img_suc)
    action_node = ActionNode(img_pre, img_suc, image_objects_pre, image_objects_suc, ActionNode_Type.SWAP)
    return action_node, image_objects

#--------------------------------------------

def get_furthest_altered_points(img_add_eff, img_del_eff):
    min_x = (sys.maxsize, 0)
    min_y = (0, sys.maxsize)
    max_x = (1, 0)
    max_y = (0, 1)
    for x in range(img_add_eff.shape[1]):
        for y in range(img_add_eff.shape[0]):
            if img_add_eff[y, x][0] != 0 or img_del_eff[y,x][0] != 0:
                if (x < min_x[0]):
                    min_x = (x, y)
                if (y < min_y[1]):
                    min_y = (x, y)
    for x in range(img_add_eff.shape[1] - 1, 0, -1):
        for y in range(img_add_eff.shape[0] - 1, 0, -1):
            if img_add_eff[y, x][0] != 0 or img_del_eff[y,x][0] != 0:
                if (x > max_x[0]):
                    max_x = (x, y)
                if (y > max_y[1]):
                    max_y = (x, y)

    dis_minx_maxx = util.get_distance(min_x[0], min_x[1], max_x[0], max_x[1])
    dis_miny_maxx = util.get_distance(min_y[0], min_y[1], max_x[0], max_x[1])
    dis_minx_maxy = util.get_distance(min_x[0], min_x[1], max_y[0], max_y[1])
    dis_miny_maxy = util.get_distance(min_y[0], min_y[1], max_y[0], max_y[1])
    max_dis = max([dis_minx_maxx, dis_miny_maxx, dis_minx_maxy, dis_miny_maxy])

    if (min_x == min_y or dis_minx_maxx == max_dis or dis_minx_maxy == max_dis):
        left_top = ImagePointForSwapActionRectangle(min_x[0], min_x[1], False, False)
    else:
        left_top = ImagePointForSwapActionRectangle(min_y[0], min_y[1], False, False)
    if (max_x == max_y or dis_minx_maxx == max_dis or dis_miny_maxx == max_dis):
        right_bottom = ImagePointForSwapActionRectangle(max_x[0], max_x[1], True, True)
    else:
        right_bottom = ImagePointForSwapActionRectangle(max_y[0], max_y[1], True, True)

    return left_top, right_bottom
#--------------------------------------------

def find_area_of_swap_method_2(img_pre, img_suc, img_add_eff, img_del_eff):
    left_top, right_bottom = get_furthest_altered_points(img_add_eff, img_del_eff)
    print(left_top)
    print(right_bottom)

    width = 1
    height = 1

    ##########################################################################
    ### Expand rectanges so that x,y +/- width,height encompase all points ###
    for x in range(img_add_eff.shape[1]):
        for y in range(img_add_eff.shape[0]):
            if img_add_eff[y,x][0] != 0 or img_del_eff[y,x][0] != 0 :
                if (not left_top.does_width_include_point(x, width) and not right_bottom.does_width_include_point(x, width)):
                    if (left_top.get_width_including_point(x, width) < right_bottom.get_width_including_point(x, width)):
                        width = left_top.get_width_including_point(x, width)
                        left_top.set_x_to_width_including_point(x)
                    else:
                        width = right_bottom.get_width_including_point(x, width)
                        right_bottom.set_x_to_width_including_point(x)

                if (not left_top.does_height_include_point(y, height) and not right_bottom.does_height_include_point(y, height)):
                    if (left_top.get_height_including_point(y, height) < right_bottom.get_height_including_point(y, height)):
                        height = left_top.get_height_including_point(y, height)
                        left_top.set_y_to_height_including_point(y)
                    else:
                        height = right_bottom.get_height_including_point(y, height)
                        right_bottom.set_y_to_height_including_point(y)
                """ !!!!!!
                if ((x > (left_top[0]+width)) and (x < (right_bottom[0]-width))):

                    # same x,y is min/max:
                    if (x - left_top[0]  < (right_bottom[0] - x) ):
                        width = x - left_top[0]
                    else:
                        width = right_bottom[0] - x
                    print("width=" + str(width))

                if ((y > (left_top[1]+height)) and  (y < (right_bottom[1]-height))):
                    # same x,y is min/max:
                    if ((y - left_top[1])  < (right_bottom[1] - y) ):
                        height =  y - left_top[1]
                    else:
                        height = right_bottom[1] - y
                    print("height=" + str(height))
                !!!!!"""
    before_height = height
    before_width = width

    #cv2.rectangle(img_pre, (left_top[0], left_top[1]), (left_top[0] + width, left_top[1] + height), (255, 0, 0), 2)
    #cv2.rectangle(img_pre, (right_bottom[0]-width, right_bottom[1]-height), (right_bottom[0], right_bottom[1]), (255, 0, 0),2)
    #cv2.imshow('img_pre_with_rec_1', np.uint8(img_pre))

    #height = height - 1
    #width = width - 1
    print(width)
    print(height)
    print(left_top)
    print(right_bottom)
    crop_img = img_pre[left_top.y:(left_top.y + height), left_top.x:(left_top.x + width)]
    cv2.imshow('before-img_pre_with_rec_1-crop', np.uint8(crop_img))
    crop_img2 = img_suc[right_bottom.y - height:right_bottom.y, right_bottom.x - width:right_bottom.x]
    cv2.imshow('before-img_pre_with_rec_1-crop-1', np.uint8(crop_img2))


    #########################################################################################
    ###  fix overlapping x or y (if both overlap the swap wouldn't have been discovered): ###
    for x in range(img_add_eff.shape[1]):
        for y in range(img_add_eff.shape[0]):
            if img_add_eff[y,x][0] != 0 or img_del_eff[y,x][0] != 0 :
                #print("x=" + str(x) + "y=" + str(y))
                # if not in first square \n and not in second square
                #if (((x > (left_top[0] + width)) or (y > (left_top[1] + height)))
                 #       and ((x < (right_bottom[0] - width) or (y < (right_bottom[1] - height))))):

                if (not left_top.is_point_in_rect_with_width_height(x,y, width, height) and not right_bottom.is_point_in_rect_with_width_height(x,y,width, height)):
                    if (x > (left_top.x + width) ):
                        width = left_top.get_width_including_point(x, width)
                        #--left_top.set_x_to_width_including_point(x)
                    elif (x < (right_bottom.x - width)):
                        width = right_bottom.get_width_including_point(x, width)
                        #--right_bottom.set_x_to_width_including_point(x)
                """!!!!!
                if ( ((x > (left_top[0] + width)) or (y > (left_top[1]+height)) )
                    and ((x < (right_bottom[0]-width) or (y < (right_bottom[1]-height))))) :
                    print("change width")
                    print("x=" + str(x) + "y=" + str(y))
                    if (x > (left_top[0] + width)):
                        width = x - left_top[0]
                    elif (x < (right_bottom[0]-width)):
                        width = right_bottom[0] - x
                    print(width)
                    #if (y > (left_top[1]+height)):# could also be and else if
                    #    height = left_top[1] + height
                    #elif (y < (right_bottom[1]-height)):
                    #    height = right_bottom[1] - y
                !!!"""

    print (width)
    print (height)
    crop_img = img_pre[left_top.y:(left_top.y + height), left_top.x:(left_top.x + width)]
    crop_img2 = img_suc[right_bottom.y-height:right_bottom.y, right_bottom.x-width:right_bottom.x]
    #image_diff = crop_img - crop_img2
   # b, g, r = cv2.split(image_diff)
    if (not util.are_images_equal(crop_img, crop_img2)):#if (cv2.countNonZero(b) != 0 or cv2.countNonZero(g) != 0  or cv2.countNonZero(r) != 0 ):
        height = before_height
        width = before_width
        for x in range(img_add_eff.shape[1]):
            for y in range(img_add_eff.shape[0]):
                if img_add_eff[y, x][0] != 0 or img_del_eff[y,x][0] != 0 :
                    #print("x=" + str(x) + "y=" + str(y))
                    # if not in first square \n and not in second square
                    if (not left_top.is_point_in_rect_with_width_height(x, y, width, height) and not right_bottom.is_point_in_rect_with_width_height(x, y,width, height)):
                        if (y > (left_top.y + height)):
                            height = left_top.get_height_including_point(y, height)
                            # --left_top.set_x_to_width_including_point(x)
                        elif (y < (right_bottom.y - height)):
                            height = right_bottom.get_height_including_point(y, height)
    ###   END-OF fix overlapping:    ###
    ####################################


    ##################################
    ###        Validate:           ###
    crop_imgb = img_pre[left_top.y:(left_top.y + height), left_top.x:(left_top.x + width)]
    crop_imgb2 = img_suc[right_bottom.y-height:right_bottom.y, right_bottom.x-width:right_bottom.x]
    #image_diff = crop_imgb - crop_imgb2
    #b, g, r = cv2.split(image_diff)
    #if (cv2.countNonZero(b) != 0 or cv2.countNonZero(g) != 0 or cv2.countNonZero(r) != 0):
    if (not util.are_images_equal(crop_imgb, crop_imgb2)):
        print ("something went wrong with determining which areas have been swapped")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        exit(0)
    ##################################

    print("Found: left_top:=" + str(left_top) + ", right_bottom:=" + str(right_bottom) + ", width:=" + str(width) + ", height:=" + str(height) + ".")

    #cv2.rectangle(img_pre, (left_top[0], left_top[1]), (left_top[0]+width, left_top[1]+height), (255, 0, 0),2)
    #cv2.rectangle(img_pre, (right_bottom[0]-width, right_bottom[1]-height), (right_bottom[0], right_bottom[1]), (255, 0, 0),2)
    #cv2.imshow('img_pre_with_rec', np.uint8(img_pre))
    image_area1 = ImageArea(left_top.x, left_top.y, width, height)
    image_area2 = ImageArea(right_bottom.x-width, right_bottom.y-height, width, height)
    return [image_area1, image_area2]

###########################################################################################################

#====================================================================









###########################################################################################3####
##########   SCRATCH

initial =[]
image1= None
image2= None
index_crop =0
def find_area_of_swap_failed(img_pre, img_suc, img_add_eff, img_del_eff):
    global index_crop
    #added_images = img_pre + img_add_eff
    #cv2.imshow('img_suc', np.uint8(img_suc))
    #cv2.imshow('img_pre', np.uint8(img_pre))
    #cv2.imshow('added_images', np.uint8(added_images))
    edges = cv2.Canny(np.uint8(img_add_eff), 100, 200)
    cv2.imshow('edge1', np.uint8(edges))
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    edges = cv2.Canny(np.uint8(img_del_eff), 100, 200)
    cv2.imshow('edge2', np.uint8(edges))
    contours2, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours.extend(contours2)

    #print(len(contours))
    # computes the bounding box for the contour, and draws it on the frame,
    if (len(contours) > 2):
        print("more than 2 contours")
        set1 = []
        set2 = []
        furthest1, furthest2 = get_furthest(contours)
        x1, y1, w1, h1 = cv2.boundingRect(furthest1)
        x1 = x1 + 1
        y1 = y1 + 1
        w1 = w1 - 1
        h1 = h1 - 1
        image_area1 = ImageArea(x1, y1, w1, h1)
        x2, y2, w2, h2 = cv2.boundingRect(furthest2)
        x2 = x2 + 1
        y2 = y2 + 1
        w2 = w2 - 1
        h2 = h2 - 1
        image_area2 = ImageArea(x2, y2, w2, h2)
        edge_contours = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x = x + 1
            y=y+1
            w = w - 1
            h = h - 1
            step_size1 = image_area1.get_distance_between_centers(x, y, w, h)
            step_size2 = image_area2.get_distance_between_centers(x, y, w, h)
            if (abs(step_size1 - step_size2) < 10):
                edge_contours.append((contour, abs(step_size1 - step_size2)))
                continue
            if (step_size1 < step_size2):
                image_area1.add_position_values_from_width_height(x, y, w, h)
            else:
                image_area2.add_position_values_from_width_height(x, y, w, h)

        edge_contours.sort(key=lambda x: x[1], reverse = True) # largest difference_in_distance first
        for edge_contour, dis in edge_contours:
            x, y, w, h = cv2.boundingRect(edge_contour)
            x = x + 1
            y=y+1
            w = w - 1
            h = h - 1
            step_size1 = image_area1.get_distance_between_centers(x, y, w, h)
            step_size2 = image_area2.get_distance_between_centers(x, y, w, h)
            if (abs(step_size1 - step_size2) <5 ):
                print("edge_contour not included: as the difference in distance is less than 10; i.e. is " + str(abs(step_size1 - step_size2)))
                continue
            if (step_size1 < step_size2 and image_area1.get_size() <= image_area2.get_size()):
                set1.append(contour)
                image_area1.add_position_values_from_width_height(x, y, w, h)
            elif (step_size2 < step_size1  and image_area2.get_size() <= image_area1.get_size()):
                set2.append(contour)
                image_area2.add_position_values_from_width_height(x, y, w, h)
            else:
                print("edge_contour not included: as would be added to the larger image area")
    else:
        print("only 2 contours")
        x, y, w, h = cv2.boundingRect(contours[0])
        x = x+1
        y=y+1
        w = w-1
        h = h - 1

        #crop_img = img_pre[y:y+h, x:x+w]
        #cv2.imshow('crop_img1', np.uint8(crop_img))
        image_area1 = ImageArea(x, y, w, h)
        x, y, w, h = cv2.boundingRect(contours[1])
        x = x+1
        y=y+1
        h = h - 1
        w = w-1
        image_area2 = ImageArea(x, y, w, h)

        #crop_img2 = img_pre[y:y+h, x:x+w]
        #cv2.imshow('crop_img2', np.uint8(crop_img2))
        #index_crop = index_crop+1
       # while cv2.getWindowProperty('crop_img1', 0) >= 0 or cv2.getWindowProperty('crop_img2', 0) >= 0:
       #     keyCode = cv2.waitKey(50)

    print(image_area1)
    print(image_area2)
    width = int(np.average([image_area1.get_width(), image_area2.get_width()]))  # max((maxXSet1 - minXSet1), (maxXSet2 - minXSet2))# TODO average appears to work better but further testing required
    height = int(np.average([image_area1.get_height(), image_area2.get_height()]))  # max((maxYSet1 - minYSet1), (maxYSet2 - minYSet2))#
    print("average: width:=" + str(width) + " height:=" + str(height))
    image_area1.set_width_height_keep_center(width, height, img_pre.shape[1], img_pre.shape[0])
    image_area2.set_width_height_keep_center(width, height, img_pre.shape[1], img_pre.shape[0])
    print(image_area1)
    print(image_area2)
    """
    pos1_1, pos1_2 = image_area1.get_positions()
    cv2.rectangle(img_pre, pos1_1, pos1_2, (255, 0, 0))
    pos2_1, pos2_2 = image_area2.get_positions()
    cv2.rectangle(img_pre, pos2_1, pos2_2, (255, 0, 0))
    """
    # cv2.rectangle(img_pre, (minXSet1, minYSet1), (maxXSet1, maxYSet1), (255, 0, 0))
    # cv2.rectangle(img_pre, (minXSet2, minYSet2), (maxXSet2, maxYSet2), (255, 0, 0))
    #--cv2.imshow('img_pre_with_rec', np.uint8(img_pre))
    pos1_1, pos1_2 = image_area1.get_positions()
    pos2_1, pos2_2 = image_area2.get_positions()
    input = [pos1_1[0], pos1_1[1], pos2_1[0], pos2_2[1], width, height]
    global initial
    initial = [pos1_1[0], pos1_1[1], pos2_1[0], pos2_2[1], width, height]
    global image1
    global image2
    image1 = img_pre
    image2 = img_suc

   # result = optimize.fmin(downhill_score, input)

    #image_area1_new = ImageArea(result[0], result[1], result[4], result[5])
    #image_area2_new = ImageArea(result[2], result[3], result[4], result[5])
    return [image_area1, image_area2]#[image_area1_new, image_area2_new]

#--------------------------------------------

def downhill_score(input):


    crop_img = image1[int(input[1]):int(input[1])+int(input[5]), int(input[0]):int(input[0])+int(input[4])]
    crop_img2 = image2[int(input[3]):int(input[3]) + int(input[5]), int(input[2]):int(input[2]) + int(input[4])]
    image_diff = crop_img- crop_img2
    b1, g1, r1 = cv2.split(image_diff)


    crop_img = image2[int(input[1]):int(input[1])+int(input[5]), int(input[0]):int(input[0])+int(input[4])]
    crop_img2 = image1[int(input[3]):int(input[3]) + int(input[5]),int( input[2]):int(input[2]) + int(input[4])]
    image_diff = crop_img- crop_img2
    b2, g2, r2 = cv2.split(image_diff)
    return (cv2.countNonZero(b1) +  cv2.countNonZero(g1) +cv2.countNonZero(r1) + cv2.countNonZero(b2) +  cv2.countNonZero(g2) +cv2.countNonZero(r2)) + abs(input[4] - initial[4] ) + abs(input[5] - initial[5] )


#def reduce_error(from_x, from_y, to_x, to_y, width, height):
 #   while swapped_image_difference(from_x, from_y, to_x, to_y, width, height) != 0:


def swapped_image_difference(from_x, from_y, to_x, to_y, width, height):
    crop_img = image1[int(input[1]):int(input[1]) + int(input[5]), int(input[0]):int(input[0]) + int(input[4])]
    crop_img2 = image2[int(input[3]):int(input[3]) + int(input[5]), int(input[2]):int(input[2]) + int(input[4])]
    image_diff = crop_img - crop_img2
    b1, g1, r1 = cv2.split(image_diff)
    crop_img = image2[int(input[1]):int(input[1])+int(input[5]), int(input[0]):int(input[0])+int(input[4])]
    crop_img2 = image1[int(input[3]):int(input[3]) + int(input[5]),int( input[2]):int(input[2]) + int(input[4])]
    image_diff = crop_img- crop_img2
    b2, g2, r2 = cv2.split(image_diff)
    return (cv2.countNonZero(b1) +  cv2.countNonZero(g1) +cv2.countNonZero(r1) + cv2.countNonZero(b2) +  cv2.countNonZero(g2) +cv2.countNonZero(r2))


#crop_img = img[y:y+h, x:x+w]
#--------------------------------------------

def get_furthest(contours):
    furthest1 = None
    furthest2 = None
    distance = -1
    for contour1 in contours:
        x1, y1, w1, h1 = cv2.boundingRect(contour1)
        for contour2 in contours:
            x2, y2, w2, h2 = cv2.boundingRect(contour2)
            step_size = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            if (step_size > distance):
                #print(step_size)
                distance = step_size
                furthest1 = contour1
                furthest2 = contour2
    x1, y1, w1, h1 = cv2.boundingRect(furthest1)
    x2, y2, w2, h2 = cv2.boundingRect(furthest2)
    #step_size = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    #print(step_size)
    #x1, y1, w1, h1 = cv2.boundingRect(furthest1)
    #x2, y2, w2, h2 = cv2.boundingRect(furthest2)
    # #cv2.rectangle(img_pre, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0))
    #cv2.rectangle(img_pre, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0))
    #cv2.imshow('img_pre_with_rec3', np.uint8(img_pre))
    return furthest1, furthest2

#--------------------------------------------
#--------------------------------------------



#----- scratch:

"""
       minXSet1 = sys.maxsize
       minYSet1 = sys.maxsize
       maxXSet1 = 0
       maxYSet1 = 0
       minXSet2 = sys.maxsize
       minYSet2 = sys.maxsize
       maxXSet2 = 0
       maxYSet2 = 0
       for contour in contours:
           #if furthest1 == contour or furthest1 == contour:
            #   continue
           #centerX1 = minXSet1 + ((maxXSet1-minXSet1)/2)#width/2
           #centerY1 = minYSet1 + ((maxYSet1-minYSet1)/2)#height/2
           #centerX2 = minXSet2 + ((maxXSet2-minXSet2)/2)#width/2
           #centerY2 = minYSet2 + ((maxYSet2-minYSet2)/2)#height/2
           x, y, w, h = cv2.boundingRect(contour)
           step_size1 = np.sqrt((centerX1 - (x+(w/2))) ** 2 + (centerY1 - (y+(h/2))) ** 2)
           step_size2 = np.sqrt((centerX2 - (x+(w/2))) ** 2 + (centerY2 - (y+(h/2))) ** 2)
           print(abs(step_size1 - step_size2))
           if (abs(step_size1 - step_size2) < 15):
               continue
           if (step_size1 < step_size2):
               set1.append(contour)
               minXSet1 = min(minXSet1, x)
               minYSet1 = min(minYSet1, y)
               maxXSet1 = max(maxXSet1, x+w)
               maxYSet1 = max(maxYSet1, y+h)

           else:
               set2.append(contour)
               minXSet2 = min(minXSet2, x)
               minYSet2 = min(minYSet2, y)
               maxXSet2 = max(maxXSet2, x+w)
               maxYSet2 = max(maxYSet2, y+h)
       width = max((maxXSet1-minXSet1), (maxXSet2-minXSet2))
       height = max((maxYSet1-minYSet1), (maxYSet2-minYSet2))

          # set2Center = (x+(w/2), y+(w/2))

       contoursMinX = sys.maxsize
       contorsMaxX = 0
       contoursMinY = sys.maxsize
       contorsMaxY = 0
       for contour in contours:
           x, y, w, h = cv2.boundingRect(contour)
           contoursMinX = min(contoursMinX, x)
           contorsMaxX = max(contorsMaxX, x+w)
           contoursMinY = min(contoursMinY, y)
           contorsMaxY = max(contorsMaxY, y+h)

       """

"""
       print (contours[0])
       clusteringData = []
       for contour in contours:
           x, y, w, h = cv2.boundingRect(contour)
           clustering = {"x": x+(w/2), "y": y+(h/2), "contour": contour}
           clusteringData.append(clustering)

       km = KMeans(
           n_clusters=2, init='random',
           n_init=10, max_iter=300,
           tol=1e-04, random_state=0
       )
       y_km = km.fit_predict(X)



       if (len(contours) > 1):
           min_width = 1
           min_height = 1
           lowestXvalue = -1
           highestXvalue = -1
           lowestYvalue = -1
           highestYvalue = -1

           rectangles  = []
           for contour in contours:
               x, y, w, h = cv2.boundingRect(contour)
               rectangles.append((x, y, w, h))
               lowestXvalue = min(lowestXvalue, x)
               highestXvalue = max(highestXvalue, x + w)
               lowestYvalue = min(lowestYvalue, x)
               highestYvalue = max(highestYvalue, y + h)
           furthestyDistance =- 1
           #width = (highestXvalue - lowestXvalue) / 2
           #height = (highestYvalue - lowestYvalue) / 2
           #rectanglesMinXSorted = rectangles.sort(key=lambda x: x[0])
           #rectanglesMaxXSorted = rectangles.sort(key=lambda x: x[0]+x[2])
           #isInLeftRect = []
           #for rectangle in rectangles:

           #for contour in contours:
       """

"""
def find_x_y_width_height_of_objects(img_add_eff):
    changed_start_x = -1
    changed_start_y = -1
    width = -1
    height = -1
    for y in range(0, img_add_eff.shape[0]): # height
        current_width = 1
        for x in range(0, img_add_eff.shape[1]): # width
            if changed_start_x != -1 and img_add_eff[y][x] > unchanged_pixel_value_threshold:
                current_width = current_width + 1
            elif img_add_eff[y][x] > unchanged_pixel_value_threshold:
                changed_start_x = x
                changed_start_y = y
"""