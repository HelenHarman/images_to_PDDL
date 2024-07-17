
class Node:
    def __init__(self):
        self.parents = []

    def add_parent(self, parent):
        if not parent in self.parents:
            self.parents.append(parent)

    def remove_parent(self, parent):
        if parent in self.parents:
            self.parents.remove(parent)
#=====================================

class OperatorNode(Node):
    def __init__(self, children):
        Node.__init__(self)
        self.children = []
        self.add_children(children)

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def add_child(self, child):
        if not child in self.children:
            child.add_parent(self)
            self.children.append(child)

    def replace_child(self, to_be_replaced, replacement):
        if (to_be_replaced in self.children):
            self.children.remove(to_be_replaced)
        self.children.append(replacement)
        replacement.add_parent(self)
        to_be_replaced.remove_parent(self)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def remove_self_from_graph(self):
        for child in self.children:
            child.remove_parent(self)
        for parent in self.parents:
            parent.remove_child(self)

#======================================

class OrNode(OperatorNode):
    def __init__(self, children, precondition, is_known_precondition):
        self.preconditions = [] # set of grounded_state.Atom. e.g., (not (clear loc1)), (at img1 loc1)
        self.preconditions.append(precondition)
        self.is_known_precondition = is_known_precondition
        OperatorNode.__init__(self, children)

    def do_children_match(self, other):
        return (isinstance(other, OrNode) and self.children == other.children)

    def get_action_nodes(self):
        action_nodes = []
        for child in self.children:
            if (isinstance(child, DepNode)):
                action_nodes.append(child.children[1])
            else:
                action_nodes.append(child)
        return action_nodes



    def __eq__(self, other):
        return (isinstance(other, OrNode) and self.is_known_precondition == other.is_known_precondition and self.children == other.children)

#======================================

class AndNode(OperatorNode):
    def __init__(self, children):
        OperatorNode.__init__(self, children)

    def __eq__(self, other):
        return (isinstance(other, AndNode) and self.children == other.children)
#======================================

class DepNode(OperatorNode):
    def __init__(self, children):
        OperatorNode.__init__(self, children)


    def __eq__(self, other):
        return (isinstance(other, DepNode) and self.children[1] == other.children[1])

#======================================









# RM?:
class OAndNode(OperatorNode):
    def __init__(self, children):
        OperatorNode.__init__(self, children)



#======================================
#======================================