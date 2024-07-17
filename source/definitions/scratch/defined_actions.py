












defined_action_id = 0
class DefinedAction:
    def __init__(self):
        global defined_action_id
        self.id = defined_action_id
        defined_action_id = defined_action_id + 1

        self.params = {} # name to Type
        self.preconditions = []
        self.effects = []
        self.action_nodes = []

    def add_action_node(self, action_node):
        if (self.action_nodes and self.can_add_action_node()):
            self.action_nodes.append(action_node)
            return True
        elif (not self.action_nodes):
            self.create_action_definition(action_node)
            return True
        return False


    def add_action_node(self, action_node, defined_params, defined_preconditions, defined_effects):
        if not self.params:
            self.params = defined_params
            self.preconditions = defined_preconditions
            self.effects = defined_effects
        elif ((self.params != defined_params) or (self.preconditions != defined_preconditions) or (self.effects != defined_effects)):
            return False
        self.action_nodes.append(action_node)
        return True

    def __str__(self):
        return_str = "( :action action_" + str(self.id) + "\n"
        return_str = return_str + " :parameters ("
        for i in range(len(self.params)):
            return_str = return_str + " ?" + str(i) + " - " + self.params[i]
        return_str = return_str + ") \n"
        return_str = return_str + " :precondition (and "
        for pre in self.preconditions:
            return_str = return_str + str(pre) + "\n "
        return_str = return_str + ") \n"
        return_str = return_str + " :effect (and "
        for eff in self.effects:
            return_str = return_str + str(eff) + "\n "
        return_str = return_str + ") \n"

        return return_str



def create_action_definition(action_node):
    defined_params = []
    defined_preconditions = []
    defined_effects = []
    action_params = []
    for change in action_node.defined_changes:
        if change[0].get_definition().id not in action_params:
            action_params.append(change[0].get_definition().id)
            defined_params.append(change[0].get_type_as_string()) #["?"+str(len(defined_params))]

        for precondition in change[0].get_predicates_for_action_def():
            pre = PreEffDefinition(precondition[0], precondition[2])
            pre.params = precondition[1]
            defined_preconditions.append(pre)

        for effect in change[1].get_predicates_for_action_def():
            eff = PreEffDefinition(effect[0], effect[2])
            eff.params = effect[1]
            defined_effects.append(eff)

    # Add action_node.linked_objects to preconditions
    #   For changing objects together link: we need to define a predicate <-- which we have set the id of (we just need to find it again - as it was added to the action)
    #   For other link: we (prob) just need to the state of the second object
    for link in action_node.linked_objects:
        ids_and_types = link.get_object_ids_and_types()
        for id_and_type in ids_and_types:
            if id_and_type[0] not in action_params:
                action_params.append(id_and_type[0])
                defined_params.append(id_and_type[1]) #["?" + str(len(defined_params))]

        for precondition in link.get_predicates_for_action_def():
            pre = PreEffDefinition(precondition[0], precondition[2])
            pre.params = precondition[1]
            defined_preconditions.append(pre)

    # we need to get definitions not groundings: so replace objects with correct params:
    for pre in defined_preconditions:
        pre.replace_grounded_params_with_definitions(action_params, defined_params)
    for eff in defined_effects:
        eff.replace_grounded_params_with_definitions(action_params, defined_params)

    return defined_params, defined_preconditions, defined_effects




class PreEffDefinition():
    def __init__(self, name, positive = True):
        self.positive = positive
        self.name = name
        self.params = []

    def replace_grounded_params_with_definitions(self, grounded_action_params, action_def_params):
        for index_self_param in range(len(self.params)):
            replaced = False
            for i in range(len(grounded_action_params)):
                if self.params[index_self_param] == grounded_action_params[i]:
                    self.params[index_self_param] = i #action_def_params[i][0]
                    replaced = True
                    break
            if not replaced:
                print("ERROR: Failed to create actions definitions")
                exit(0)

    def __eq__(self, other):
        return (isinstance(other, PreEffDefinition) and (self.name == other.name) and (self.params == other.params) and self.positive == other.positive)


    def __str__(self):
        if self.positive:
            return_str = "(" + self.name
        else:
            return_str = "(not (" + self.name

        for param in self.params:
            return_str = return_str + " ?" + str(param)

        if not self.positive:
            return_str + ")"
        return return_str + ")"

