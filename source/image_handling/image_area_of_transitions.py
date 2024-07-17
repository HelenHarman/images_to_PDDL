# ======================================================================

def find_image_area_using_pos(image_areas, changed_area):
    for image_area in image_areas:
        if (image_area.pos_min_x == changed_area.pos_min_x and image_area.pos_min_y == changed_area.pos_min_y
                and image_area.pos_max_x == changed_area.pos_max_x and image_area.pos_max_y == changed_area.pos_max_y ):
            return image_area
    return None

class ImageArea:
    def __init__(self, min_x, min_y, max_x, max_y):
        if isinstance(min_x, int):
            self.min_x = min_x
            self.min_y = min_y
            self.max_x = max_x
            self.max_y = max_y
        else:
            self.min_x = min_x[0]
            self.min_y = min_y[1]
            self.max_x = max_x[0]
            self.max_y = max_y[1]

            self.pos_min_x = min_x
            self.pos_min_y = min_y
            self.pos_max_x = max_x
            self.pos_max_y = max_y


    def is_overlapping(self, other):
        if ((self.min_x > other.max_x) or (self.max_x < other.min_x)):
            return False
        if ((self.min_y > other.max_y) or (self.max_y < other.min_y)):
            return False
        return True

    def get_center(self):
        return (self.get_center_x_location(), self.get_center_y_location())

    def get_center_x_location(self):
        return float(self.min_x) + ((float(self.max_x+1) - float(self.min_x)) / 2.0) # +1 to include the max pixel

    def get_center_y_location(self):
        return float(self.min_y) + ((float(self.max_y+1) - float(self.min_y)) / 2.0)

    def get_width_height(self):
        return (self.get_width(), self.get_height())

    def get_width(self):
        return self.max_x - self.min_x

    def get_height(self):
        return self.max_y - self.min_y


    def get_area(self):
        return (self.get_width() * self.get_height())

    def get_area(self):
        return ((self.max_x - self.min_x) * (self.max_y - self.min_y))

    def crop_image(self, image):
        return image[self.min_y:self.max_y + 1, self.min_x:self.max_x + 1] #img[y:y+h, x:x+w]


    def __eq__(self, other):
        #return (isinstance(other, ImageArea) and self.pos_min_x == other.pos_min_x and self.pos_max_x == other.pos_max_x and self.pos_min_y == other.pos_min_y and self.pos_max_y == other.pos_max_y)
        return (isinstance(other, ImageArea) and self.min_x == other.min_x and self.max_x == other.max_x and self.min_y == other.min_y and self.max_y == other.max_y)

    def __hash__(self):
        string = str(self.min_x) + "," + str(self.min_y) + "," + str(self.max_x) + "," + str(self.max_y)
        return string.__hash__()

    def __str__(self):
        return "(min_x= " + str(self.min_x) + ", min_y=" + str(self.min_y) + ", max_x=" + str(self.max_x) + ", max_y=" + str(self.max_y) + ", width=" + str(self.get_width()) + ", height=" + str(self.get_height()) +  ")"



#=====================================================================================
#=====================================================================================


