
#from definitions.defined_object import DefinedImage, DefinedLoction
from definitions.defined_state import State, DefinedImageState, DefinedLocationState, LinkedObjects, Link_Type, Link, \
    LinkedObject
from image_handling.image_area_of_transitions import ImageObject_Type



# TODO The following should be handled by the state of a location:
#    link objects and locations?? <--- object A can only be swapped with locations that are in state X (location is clear for one action but not the other)


def create_definitions(all_actions, all_objects):
    defined_objects = convert_image_objects_into_defined_objects(all_actions, all_objects)
    create_state_definitions_for_all_actions(all_actions, defined_objects)
    match_previous_action_suc_state_match_next_action_pre_state(all_actions, defined_objects)

    for action in all_actions:
        action.sort_preconditions()

    all_linked_objects = find_state_common_to_locations_changing_state(all_actions, defined_objects)
    print_debugging(all_actions)

    return all_actions, defined_objects #

def print_debugging(action_nodes):
    index = 0
    for action_node in action_nodes:
        if index > 10:
            break
        print ("------------------------------")
        print (" State for action " + str(index) )
        print (" Pre State for action " + str(index) )
        print (action_node.defined_pre_state)
        print (" Suc State for action " + str(index) )
        print (action_node.defined_suc_state)

        print ("defined_changes:")
        for change in action_node.defined_changes:
            print ("from=" + str(change[0]) + ", to=" + str(change[1]))

        print("links:")
        for link in action_node.linked_objects:
            print (link)

        print("------------------------------")


        index = index +1



# linked locations etc.
def find_state_common_to_locations_changing_state(all_actions, defined_objects):
    defined_locations = extract_defined_locations(defined_objects)
    print (len(all_actions))
    # --------
    # act links are prefured as there will be less of them and do not require additional params to be added to actions:
    # act_link: when location a changes state (from x to z) location b changes state (from v to w) and location ? changes...
    links = create_changed_value_at_same_time_links(all_actions) # TODO: if result of this never produces an invalid state then don't need next step.
    print ("create_changed_value_at_same_time_links: links= " + str(len(links)) + " " + str(len(links[0].identical_linkings)))
    # TODO : if all links are adjacent, then assume all adjacent locations are linked

    # If any location is linked to all other locations (that can have the same states (or both can be clear)) then for those states changed_value_at_same_time_links are ignored
    #--rm: links = reduce_changed_value_at_same_time_links_if_a_loctions_is_linked_to_all_other_locations(links, defined_locations)
    #print ("reduce_changed_value_at_same_time_links_if_a_loctions_is_linked_to_all_other_locations: links= " + str(len(links)) + " " + str(len(links[0].identical_linkings)))

    #--------
    # loc_link: when location a changes state (from x to z) location b is always in state x
    #if (not links):
    #    links = create_value_change_dependent_on_state_links(defined_locations, all_actions) # TODO: if result of this never produces an invalid state then don't need previous step.
    #    print("create_value_change_dependent_on_state_links: links= " + str(len(links)) + " " + str(len(links[0].identical_linkings)))

    # if only one clear location at a time (and all locations always swap from clear to not clear) then don't bother with next step (as only that location's state matters)--> this would (probably) just reduce the number of atoms,
                                                                                # if a lcoation's clear object is always the same object this is also true (this would make this work for two robots navigating an area)
    all_linked_objects, objects_to_links = create_value_change_dependent_on_state_links2(links, all_actions, is_only_one_clear_location_in_each_state(all_actions, defined_locations)) # TODO: the inverse of is_only_one_clear_location_in_each_state is also true
    print("create_value_change_dependent_on_state_links2: all_linked_objects= " + str(len(all_linked_objects)) )
    # keep list of actions for when the same (with possibly different permutations) act_link is stated
    # ... same for loc_link

    # if actions have same number of act_link and loc_link then they can be the same definition

    # TODO reduce_number_of_links(objects_to_links)

    return all_linked_objects

#------------------------------------------------------------
# TODO: for x to be cleared x and y must be clear and for x to be cleared x, y must be cleared. Therefore x doesn't have to depend on y
def reduce_number_of_links(objects_to_links): # LinkedObject to [LinkedObjects, ] where LinkedObjects.objects[0]==LinkedObject and LinkedObjects.objects[1].object_state_to==None
    for object in objects_to_links:
        for linked_object in objects_to_links[object]:
            pass
            # TODO get the objects_to_links where LinkedObjects.objects[0].object_state_to matches linked_object.objects[1].object_state_from
            # then for linked_object2 in objects_to_links[object]:
                # if linked_object2 is in one of objects_to_links[object]:
                    # remove linked_object2 from objects_to_links[object] and thus from the actions it was added to
#---------------------------------------------------------------------

#  if a location's clear object is always the same object this is also true (this would make this work for two robots navigating an area)
# TODO: if helicopter and robot navigating area: then we should handle: location is clear for helicopter but not for robot. i.e., this should return true for such a domain (# TODO IF object A can never be moved to a location of state x then (not (at state_x location)))
def is_only_one_clear_location_in_each_state(all_actions, defined_locations): # THIS HAS BEEN CHANGED:
    """ if all clear locations have one possible object then this is true:
    for defined_location in defined_locations: # THIS WILL NOT WORK IF ALL THE ToH PIECES ARE THE SAME SIZE
        if (len(defined_location.images_when_clear) > 1 or len(defined_location.images_when_clear) == 0):
            return False
    return True
    """
    for action in all_actions:
        clear_state = None
        for location_state in action.defined_pre_state.defined_location_states:
            if ((location_state.get_state() == -1) and (clear_state == None)):
                clear_state = location_state
            elif ((location_state.get_state() == -1) and (clear_state != None) and (not location_state.is_equivalent_location(clear_state)) ):
                return False
    return True



def extract_defined_locations(defined_objects):
    defined_locations = []
    for defined_object in defined_objects:
        if (isinstance(defined_object, DefinedLoction)):
            defined_locations.append(defined_object)
    return defined_locations




def create_value_change_dependent_on_state_links2(links, all_actions, is_only_one_clear):
    #action_mapped_to_links = {} # <---TODO, to make it easier/possible to create the action definitions
    linked_objects_value_change = []
    for link in links:
        linked_objects_value_change.extend(link.identical_linkings)
    all_linked_objects = []
    processed_link_objects = []
    objects_to_links = {}
    for linked_objects in linked_objects_value_change:
        if (linked_objects in processed_link_objects):
            continue

        matching_links = get_all_links_with_same_object_state_and_permitation(linked_objects, linked_objects_value_change)
        same_states = matching_links[0].action_node.defined_pre_state.defined_location_states.copy()
        for matching_link in matching_links:
            matching_states = []
            for defined_pre_state in matching_link.action_node.defined_pre_state.defined_location_states:
                if defined_pre_state in same_states and matching_link.action_node.get_defined_objects_change(defined_pre_state.get_definition()) == None:
                    matching_states.append(defined_pre_state)
            same_states = matching_states.copy()

        # for each state does that state hold true for every time one of the objects in linked_objects changes state (in the same way)
        created_linked_objects = []
        objects_to_actions = {}
        for object in linked_objects.objects:
            objects_to_actions[object] = get_actions_that_change_object_state(object.object_state_from, object.object_state_to, all_actions)
        for state in same_states:
            if (is_only_one_clear and state.defined_location.always_from_or_to_clear): # if only one clear location then this is the "clear" precondition, as all the other states (that transition between clear and not(clear)) are "not (clear)" we don't need to worry about this.
                continue
            for object in linked_objects.objects:
                if (is_state_in_all_objects_actions_pre_state(state, objects_to_actions[object])):
                    # create link
                    link_object2 = LinkedObject(state)
                    link_objects_new = LinkedObjects(None)
                    link_objects_new.set_linked_objects(object, link_object2)
                    created_linked_objects.append(link_objects_new)
                    for action in objects_to_actions[object]:
                        action.add_linked_objects([link_objects_new])
                    if object in objects_to_links:
                        objects_to_links[object].append(link_objects_new)
                    else:
                        objects_to_links[object] = [link_objects_new]


        for matching_link in matching_links:
            matching_link.action_node.add_linked_objects(created_linked_objects)
            matching_link.action_node.add_linked_objects([matching_link])
            processed_link_objects.append(matching_link)
        all_linked_objects.extend(created_linked_objects)
        all_linked_objects.append(matching_link)
    return all_linked_objects, objects_to_links


def is_state_in_all_objects_actions_pre_state(state, objects_actions):
    print (len(objects_actions))
    for action in objects_actions:
        if state not in action.defined_pre_state:
            return False
    return True


def get_actions_that_change_object_state(object_state_from, object_state_to, all_actions):
    matching_actions = []
    for action in all_actions:
        if (action.does_action_contain_change(object_state_from, object_state_to)):
            matching_actions.append(action)
    return  matching_actions

def get_all_links_with_same_object_state_and_permitation(linked_objects, list_linked_objects):
    matching_linked_objects = []
    for link in list_linked_objects:
        if (linked_objects.have_same_locations_and_states(link)):
            matching_linked_objects.append(link)
    return matching_linked_objects



    # if two sets of links are the same they can be removed
    # TODO reduce number of links: if state x  requires states z  and q; and state z requires q then in preconditions x does need to require q

    # TODO handle reduced number of transactions: For each location that changes between state x and z is there something in common (i.e., relative position other objects). if there is something in common remove all others.. but need to handle image edges

    # if we have only ever observed a changing from z to x when b has been in state q; then how do we know that is not a precondition?... i.e., we can't
     # if b has been in different none-clear states when a has changed state, we should assume that it can be any none-clear state. if b has been multiple states when a is changed don't assume anything

def create_changed_value_at_same_time_links(all_actions):
    links = []
    for action in all_actions:
        linked_objects = LinkedObjects(action)
        linked_objects.create_changed_value_at_same_time_linked_locations_from_action()
        if (len(linked_objects.objects) <= 1):
            continue
        inserted = False
        for link in links:
            if (link.can_add_linked_objects(linked_objects, Link_Type.CHANGED_VALUE_AT_SAME_TIME)):
                link.add_linked_objects(linked_objects)
                inserted = True
                break
        if (not inserted):
            link = Link(Link_Type.CHANGED_VALUE_AT_SAME_TIME)
            link.add_linked_objects(linked_objects)
            links.append(link)
        action.add_linked_objects([linked_objects])
    return links



# if overlapping allowed in states then there will be miss-match between suc and pre that cannot be resolved
def match_previous_action_suc_state_match_next_action_pre_state(all_actions, defined_objects):
    processed = []
    for action in all_actions:
        if action in processed:
            continue
        preceding_actions = action.get_preceding_actions()
        if not preceding_actions:
            continue # action has not preceding actions
        next_actions = preceding_actions[0].get_subsequent_actions() # this will include "action". Note: all preceding_actions will have the same next_actions
        processed.extend(next_actions) #<-- optimisation
        state = State()
        #state.defined_image_states = preceding_actions[0].defined_suc_state.defined_image_states.copy()
        #state.defined_location_states = preceding_actions[0].defined_suc_state.defined_location_states.copy()
        for preceding_action in preceding_actions:
            state = add_state2_to_state1(state, preceding_action.defined_suc_state)
        for next_action in next_actions:
            state = add_state2_to_state1(state, next_action.defined_pre_state)

        state = set_all_unknown_locations_to_clear(state, defined_objects)

        for preceding_action in preceding_actions:
            preceding_action.defined_suc_state = state
        for next_action in next_actions:
            next_action.defined_pre_state = state

def set_all_unknown_locations_to_clear(state, defined_objects): # TODO we should check what the location's clear state is and check that the location matches its clear state
    for defined_location in defined_objects:
        if (isinstance(defined_location, DefinedLoction)) and not state.is_defined_object_in_state_use_ids(defined_location):
            state.add_defined_state(DefinedLocationState(defined_location))
    return state

def add_state2_to_state1(state1, state2):
    for image_state in state2.defined_image_states:
        if image_state not in state1.defined_image_states:
            if (state1.is_defined_object_in_state(image_state.defined_image)):
                print("ERROR STATES CANNOT MATCH; TODO: we don't yet support overlapping images")
                exit(0)
            else:
                state1.add_defined_state(image_state)

    for location_state in state2.defined_location_states:
        if location_state not in state1.defined_location_states:
            if (state1.is_defined_object_in_state(location_state.defined_location)):
                print (state1)
                print (state2)
                print("ERROR STATES CANNOT MATCH; TODO: we don't yet support overlapping locations")
                exit(0)
            else:
                state1.add_defined_state(location_state)

    return state1




def create_state_definitions_for_all_actions(all_actions, defined_objects):
    for action in all_actions:
        pre_state = State()
        suc_state = State()

        add_state_for_image_objects(pre_state, action.image_objects_pre, defined_objects)
        add_state_for_image_objects(suc_state, action.image_objects_suc, defined_objects)

        #skip_location_index = []
        for i in range(len(pre_state.defined_image_states)):
            if (pre_state.defined_image_states[i].defined_image.id != suc_state.defined_image_states[i].defined_image.id):
                print ("ERROR pre and suc objects don't match")
                exit(0)
            action.defined_changes.append((pre_state.defined_image_states[i], suc_state.defined_image_states[i]))
            #if pre_state.defined_image_states[i].is_at_location != None:
                #for j in range(len(pre_state.defined_location_states)):
                #    if (pre_state.defined_location_states[j].get_definition().id == pre_state.defined_image_states[i].is_at_location.get_definition().id) or (suc_state.defined_location_states[j].get_definition().id == suc_state.defined_image_states[i].is_at_location.get_definition().id):
                 #       action.defined_changes.append( (pre_state.defined_location_states[j], suc_state.defined_location_states[j]))
                #        skip_location_index.append(j)

        for i in range(len(pre_state.defined_location_states)):
            #if i in skip_location_index:
             #   continue
            if (pre_state.defined_location_states[i].defined_location.id != suc_state.defined_location_states[i].defined_location.id):
                print ("ERROR pre and suc objects don't match")
                exit(0)
            action.defined_changes.append((pre_state.defined_location_states[i], suc_state.defined_location_states[i]))



        add_state_for_image_objects(pre_state, action.unchanged_objects, defined_objects)
        add_state_for_image_objects(suc_state, action.unchanged_objects, defined_objects)

        action.defined_pre_state = pre_state
        action.defined_suc_state = suc_state


def add_state_for_image_objects(state, image_objects, defined_objects):
    for unchanged_object in image_objects:
        for defined_object in defined_objects:
            if (defined_object.is_equivalent_to_image_object_pos(unchanged_object)):
                if (isinstance(defined_object, DefinedImage)):
                    location_def_obj = find_location_def_for_object_position(unchanged_object, defined_objects)
                    if (not state.is_defined_object_in_state(defined_object)):
                        pre_location_def_state = DefinedLocationState(location_def_obj)
                        add_overlapping_locations_to_state(pre_location_def_state, state)
                        pre_image_state = DefinedImageState(defined_object, pre_location_def_state)
                        state.add_defined_state(pre_image_state)
                        state.add_defined_state(pre_location_def_state)
                elif (isinstance(defined_object, DefinedLoction)):  # could also use else
                    if (not state.is_defined_object_in_state(defined_object)):
                        pre_location_def_state = DefinedLocationState(defined_object)
                        add_overlapping_locations_to_state(pre_location_def_state, state)
                        state.add_defined_state(pre_location_def_state)



def find_location_def_for_object_position(image_object_with_pos, defined_objects):
    for defined_object in defined_objects:
        if (isinstance(defined_object, DefinedLoction)):
            if image_object_with_pos.get_center_x() == defined_object.center_x and image_object_with_pos.get_center_y() == defined_object.center_y:
                return defined_object
    return None


def add_overlapping_locations_to_state(location_def_state, state):
    for overlap in location_def_state.defined_location.overlapping_defined_locations:
        if (not state.is_defined_object_in_state(overlap)):#defined_location
            print ("add overlapping location")
            overlap_location_def_state = DefinedLocationState(overlap)
            location_def_state.equivalent_locations.append(overlap_location_def_state)
            overlap_location_def_state.equivalent_locations.append(location_def_state)
            state.add_defined_state(overlap_location_def_state)




def convert_image_objects_into_defined_objects(all_actions, all_objects):
    defined_objects = []
    for object in all_objects:
        if object.type == ImageObject_Type.OBJECT:
            defined_objects.append(DefinedImage(object.image))

    for action in all_actions:
        defined_objects = get_defined_locations_for_image_objects(action.image_objects_pre, defined_objects)
        defined_objects = get_defined_locations_for_image_objects(action.image_objects_suc, defined_objects)

    set_locations_that_overlap(defined_objects)
    return defined_objects


def get_defined_locations_for_image_objects(image_objects, defined_objects):
    for image_object in image_objects: #action.image_objects_pre:
        if image_object.imageObject.type == ImageObject_Type.LOCATION:
            found = False
            for defined_object in defined_objects:
                if defined_object == image_object: #.get_center_x()  == defined_object.center_x and image_object.get_center_y() == defined_object.center_y:
                    #print ("image_object append_to_images_when_clear min_x=" + str(image_object.min_x) + " min_y=" + str(image_object.min_y))
                    defined_object.append_to_images_when_clear(image_object.imageObject.image)
                    found = True
                    break
            if (not found):
                #print ("image_object min_x=" + str(image_object.min_x) + " min_y=" + str(image_object.min_y))
                defined_object = DefinedLoction(image_object.get_center_x(), image_object.get_center_y())
                defined_object.append_to_images_when_clear(image_object.imageObject.image)
                defined_objects.append(defined_object)
    return defined_objects


def set_locations_that_overlap(defined_objects):
    for defined_object in defined_objects:
        if (not isinstance(defined_object, DefinedLoction)):
            continue
        for other_defined_object in defined_objects:
            if ((not isinstance(other_defined_object, DefinedLoction)) or (defined_object == other_defined_object or defined_object in other_defined_object.overlapping_defined_locations)):
                continue
            if (defined_object.do_locations_with_images_overlap(other_defined_object)):
                defined_object.add_overlapping_defined_location(other_defined_object)
                other_defined_object.add_overlapping_defined_location(defined_object)


# TODO  find hidden effects - i.e, the overlapping locations becoming clear in the pizzle domain

# occlusions: if object a is in location z and object b is in location  x and (z and x overlap) then either z or x can't be moved. (although pos z/x is not clear object can still be moved there <-- nope)

















# TODO should also check that the list of links was created correctly!!!!!
# TODO: DEBUG!!!!!!: this should have reduced the links to 0 (for ToH):
def reduce_changed_value_at_same_time_links_if_a_loctions_is_linked_to_all_other_locations(links, defined_locations):
    #reduced_links = []
    for defined_location in defined_locations:
        linked_to = []
        rm_links = []
        for link in links: # therefore will only be 1 link <-- but maybe in the future we will change this
            link_identical_linkings_rm = []
            for identical_linkings in link.identical_linkings:
                if defined_location in identical_linkings:
                    for linked_location in identical_linkings.objects:
                        if (isinstance(linked_location.object_state_from.get_definition(), DefinedLoction)
                                and (linked_location.object_state_from.get_definition().id != defined_location.id) and linked_location.object_state_from.get_definition().id not in linked_to
                                and (defined_location.can_have_same_states(linked_location.object_state_from.get_definition())) ): #  checks that the locations can be the same states
                            linked_to.append(linked_location.object_state_from.get_definition().id)
                if (len(linked_to) == (len(defined_locations)-1)):
                    link_identical_linkings_rm.append(identical_linkings)
                    for also_remove in link.identical_linkings:
                        if (defined_location.can_have_same_states(also_remove.object_state_from.get_definition()) ): # checks that the locations can be the same states
                            link_identical_linkings_rm.append(also_remove)
                    break


            reduced_identical_linkings = []
            for identical_linking in link.identical_linkings:
                if identical_linking not in link_identical_linkings_rm:
                    reduced_identical_linkings.append(identical_linking)
            link.identical_linkings = reduced_identical_linkings
            if not link.identical_linkings: # if empty
                rm_links.append(link)
                break

        reduced_links = []
        for link in links:
            if link not in rm_links:
                reduced_links.append(link)
        links = reduced_links
        if not links:  # if empty
            break
    return links
# TODO: consider changing this to finding the difference between a valid state and an invalid state
def create_value_change_dependent_on_state_links(defined_locations, all_actions): # TODO if only one location is clear (at one time) then this could be simplified
    # for each defined_objects find the actions for which it changes value, in all of those actions do certain objects always have the same state

    links = []

    for defined_location in defined_locations:
        pass
        # find all actions that change the state of defined_location:
        # for ToH etc. actions_that_change_defined_objects_state will have two items clear->not(clear) and not(clear)->clear
        actions_that_change_defined_objects_state = {} # linked object (with are_same_locations_and_states==true) mapped to list of actions.
        for action in all_actions:
            defined_location_change = action.get_defined_objects_change(defined_location)
            if defined_location_change != None: # i.e., action changed the object's state
                linked_object = LinkedObject(defined_location_change[0], defined_location_change[1])
                found = False
                for key in actions_that_change_defined_objects_state:
                    if (linked_object.are_same_locations_and_states(key)):
                        actions_that_change_defined_objects_state[key].append(action)
                        found = True
                        break
                if not found:
                    actions_that_change_defined_objects_state[linked_object] = [action]



        for key in actions_that_change_defined_objects_state:
            same_states = actions_that_change_defined_objects_state[key][0].defined_pre_state.defined_location_states.copy() # Objects that are in the same state for all actions

            for action in actions_that_change_defined_objects_state[key]:
                matching_states = []
                for defined_pre_state in action.defined_pre_state.defined_location_states:
                    if defined_pre_state in same_states and action.get_defined_objects_change(defined_pre_state.get_definition()) == None: # isinstance(state_obj, DefinedLocationState)
                        matching_states.append(defined_pre_state)
                same_states = matching_states.copy()
            # TODO ADD LINK
            for state_obj in same_states:
                linked_objects = LinkedObjects(action)
                linked_objects.set_linked_objects(key, LinkedObject(state_obj))
                inserted = False
                for link in links:
                    if (link.can_add_linked_objects(linked_objects, Link_Type.VALUE_CHANGE_IS_STATE_DEPENDENT)):
                        link.add_linked_objects(linked_objects)
                        inserted = True
                        break
                if (not inserted):
                    link = Link(Link_Type.VALUE_CHANGE_IS_STATE_DEPENDENT)
                    link.add_linked_objects(linked_objects)
    return links