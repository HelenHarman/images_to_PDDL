
#============================
# Atom helper methods:

def get_common_atoms(atoms1, atoms2):
    common_atoms = []
    for atom1 in atoms1:
        for atom2 in atoms2:
            if atom1 == atom2:
                common_atoms.append(atom1)
                break
    return common_atoms

#============================

class GroundedState:
    static_atoms = [] # all grounded states have these

    def __init__(self):
        self.fluent_atoms = []
        self.associated_static_atoms = [] # needed to be able to create the action (that this state belongs to)'s preconditions

    #----------------------

    def add_atom(self, atom):
        if (atom.is_static):
            if (atom not in GroundedState.static_atoms):
                GroundedState.static_atoms.append(atom)
            if (atom not in self.associated_static_atoms):
                self.associated_static_atoms.append(atom)
        elif (atom not in self.fluent_atoms):
            self.fluent_atoms.append(atom)

    #----------------------

    def get_all_atoms_for_object(self, object_definition):
        atoms = []
        for atom in GroundedState.static_atoms:
            if object_definition in atom.defined_objects:
                atoms.append(atom)
        atoms.extend(self.get_fluent_atoms_for_object(object_definition))
        return atoms

    #----------------------

    def get_fluent_atoms_for_object(self, object_definition):
        atoms = []
        for atom in self.fluent_atoms:
            if object_definition in atom.defined_objects:
                atoms.append(atom)
        return atoms

    #----------------------

    def has_one_clear_location(self): # if the state has a single clear location, we don't care that the other locations are not clear
        num_clear = 0
        for atom in self.fluent_atoms:
            if ((atom.predicate.name == "clear") and (not atom.negated)):
                num_clear = num_clear + 1
            if num_clear > 1:
                break
        return (num_clear == 1)

    #----------------------

    def __str__(self):
        return_str = ""
        for static_atom in GroundedState.static_atoms:
            return_str = return_str + str(static_atom) + "\n"

        for fluent_atom in self.fluent_atoms:
            return_str = return_str + str(fluent_atom) + "\n"
        return return_str

    #----------------------

    def __eq__(self, other):
        return (isinstance(other, GroundedState) and self.fluent_atoms == other.fluent_atoms)


#=====================================================================


class Atom:
    def __init__(self, predicate, defined_objects, negated = False, is_static = False):
        self.negated = negated
        self.predicate = predicate
        self.defined_objects = defined_objects # constant
        self.is_static = is_static

    def __eq__(self, other):
       # if (isinstance(other, DefinedAtom) ): # use the DefinedAtom == to prevent cyclic includes
        #    return ((self.negated == other.negated) and (self.predicate == other.predicate) and (len(self.defined_objects) == len(other.defined_objects)))
        """
        if (isinstance(other, Atom) and (self.negated == other.negated) and (self.predicate == other.predicate)):
            for i in range(len(self.defined_objects)):if (self.defined_objects[i] != other.defined_objects[i]):
                    return False
            return True
        return False
        """
        return (isinstance(other, Atom) and (self.negated == other.negated) and (self.predicate == other.predicate) and (self.defined_objects == other.defined_objects))

    #-----------------------------------------

    def __str__(self):
        return_str = "("
        if self.negated:
            return_str = return_str + " not ("
        return_str = return_str + self.predicate.name
        for defined_object in self.defined_objects:
            return_str = return_str + " " + defined_object.get_string_id()

        return_str = return_str + ")"
        if self.negated:
            return_str = return_str + ")"
        return return_str

    def __hash__(self):
        return (str(self).__hash__())

#=====================================================================
#=====================================================================