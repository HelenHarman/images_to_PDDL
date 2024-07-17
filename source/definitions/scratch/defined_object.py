from image_handling import util
from image_handling.image_area_of_transitions import ImageObjectWithPosition

number_of_defined_objects = 0

class DefinedObject:
    def __init__(self):
        global number_of_defined_objects
        self.id = number_of_defined_objects
        number_of_defined_objects = number_of_defined_objects + 1

    def get_id_string(self):
        if isinstance(self, DefinedLoction):
            return "location_" + str(self.id)
        elif isinstance(self, DefinedImage):
            return  "image_" + str(self.id)


class DefinedLoction(DefinedObject):
    # center_x, center_y should be floats.
    def __init__(self, center_x, center_y):
        DefinedObject.__init__(self)
        self.center_x = center_x
        self.center_y = center_y
        self.images_when_clear = [] #images_when_clear # or (maybe) possible states for e.g., lights out
        self.overlapping_defined_locations = []
        self.always_from_or_to_clear = True
        self.possible_states = [-1] # TODO: fill in. -1 for clear and then ids for the different objects


    def __eq__(self, other):
        return ((isinstance(other, DefinedLoction) and self.center_x == other.center_x and self.center_y == other.center_y)
                or (isinstance(other, ImageObjectWithPosition) and other.get_center_x() == self.center_x and other.get_center_y() == self.center_y))


    def append_to_images_when_clear(self, image_to_append):
        for image in self.images_when_clear:
            if (util.are_images_equal(image, image_to_append)):
                return
        self.images_when_clear.append(image_to_append)


    def is_equivalent_to_image_object_pos(self, image_object_with_pos):
        return (image_object_with_pos.get_center_x() == self.center_x and image_object_with_pos.get_center_y() == self.center_y)


    def do_locations_with_images_overlap(self, other):
        for image in self.images_when_clear:
            image_min_x = self.center_x - float(float(image.shape[1])/2)
            image_min_y = self.center_y - float(float(image.shape[0])/2)
            for image_other in other.images_when_clear:
                other_min_x = other.center_x - float(float(image_other.shape[1])/2)
                other_min_y = other.center_y - float(float(image_other.shape[0])/2)
               # if (image_min_x > (other_min_x + image_other.shape[1]) or (image_min_x + image.shape[1]) < other_min_x ):
                 #   False
               # if (image_min_y > (other_min_y + image_other.shape[0]) or (image_min_y + image.shape[0]) < other_min_y):
                #    False
                if ( (not (image_min_x > (other_min_x + image_other.shape[1]) or (image_min_x + image.shape[1]) < other_min_x ))
                        and (not(image_min_y > (other_min_y + image_other.shape[0]) or (image_min_y + image.shape[0]) < other_min_y))):
                    return True
        return False


    def add_overlapping_defined_location(self, defined_location):
        self.overlapping_defined_locations.append(defined_location)

    def can_have_same_states(self, other):
        if (self.always_from_or_to_clear == other.always_from_or_to_clear):
            return True
        elif (self.possible_states.sort() == other.possible_states.sort()):
            return True


class DefinedImage(DefinedObject):
    def __init__(self, image):
        DefinedObject.__init__(self)
        self.image = image

    def __eq__(self, other):
        return (isinstance(other, DefinedImage) and util.are_images_equal(self.image, other.image))

    def is_equivalent_to_image_object_pos(self, image_object_with_pos):
        return (util.are_images_equal(self.image, image_object_with_pos.imageObject.image))