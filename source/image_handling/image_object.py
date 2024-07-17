import inspect

from generate_images import image_pairs
from image_handling import util

#======================================================================
ImageObjectArea_id = 0
class ImageObjectArea:
    def __init__(self, image, changed_image_area_of_transition, location_min_x_offset, location_min_y_offset, center_matches, belongs_to_transition = True):
        global ImageObjectArea_id
        self.id = ImageObjectArea_id
        ImageObjectArea_id = ImageObjectArea_id + 1
        if (belongs_to_transition):
            self.image_state = image_pairs.ImageState(self.id, image, (not belongs_to_transition))
        else:
            self.image = image # TODO when per-transitions this should be stored, otherwise it should be in memory (i.e., as it is a image object definition)
        self.belongs_to_transition = belongs_to_transition

        self.location_min_x_offset = location_min_x_offset
        self.location_min_y_offset = location_min_y_offset
        self.center_matches = center_matches

        self.width = image.shape[1]
        self.height = image.shape[0]

        self.changed_image_area_of_transition = changed_image_area_of_transition # belongs to a transition only to be used when linked to a transition


    def set_not_belongs_to_transition(self):
        self.belongs_to_transition = False
        self.image = self.image_state.get_image()

    def get_area(self):
        return (self.width * self.height)

    #-------------------

    def is_at_location_in_image(self, location_definition, image):
        if (self.center_matches):
            min_x = int(location_definition.image_area.get_center_x_location() - (float(self.width - 1) / 2.0))  # arrays start from 0, so need -1
            min_y = int(location_definition.image_area.get_center_y_location() - (float(self.height - 1) / 2.0))
        else:
            min_x = location_definition.image_area.min_x - self.location_min_x_offset
            min_y = location_definition.image_area.min_y - self.location_min_y_offset
        max_x = min_x + self.width
        max_y = min_y + self.height
        cropped_image = image[min_y:max_y, min_x:max_x]  # we don't need -1 here as we are using the image width (i.e., image.shape[1])
        if (util.are_images_equal(self.get_image(), cropped_image)):
            return True
        return False

    #-------------------

    def get_image(self):
        if (self.belongs_to_transition):
            return self.image_state.get_image()
        else:
            return self.image

    #-------------------

    def __eq__(self, other):
        #print (inspect.stack()[1][3])
        return (isinstance(other, ImageObjectArea) and ( (self.location_min_x_offset == other.location_min_x_offset)
                and (self.location_min_y_offset == other.location_min_y_offset)
                and (util.are_images_equal(self.get_image(), other.get_image())) ) )


#======================================================================
#======================================================================