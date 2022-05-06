import sys

from crossword import *
from collections import OrderedDict


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        #print(assignment)
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop through variables and initialize list of words to be removed
        for variable in self.crossword.variables:
            remove = list()
            # loop through variable domains to add words of incorrect length to remove list
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    remove.append(word)
            # Remove words from variable domain that are in remove list
            for word in remove:
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Quit if there is no overlap
        if self.crossword.overlaps[x, y] is None:
            return False

        # Get overlapping square. Initialize overlap check variable
        i, j = self.crossword.overlaps[x, y]
        revision = False

        # Loop through x domain. Initialize found variable and remove list
        for word_x in self.domains[x]:
            found = False
            remove = list()
            # Loop through y domain.
            for word_y in self.domains[y]:
                # check if overlapping letter for x and y words exist
                if word_x[i] == word_y[j]:
                    found = True
            # If no overlapping word exists, add to remove list
            if found is False:
                remove.append(word_x)
                revision = True
        # Remove words in remove list from x domain
        if remove:
            for word in remove:
                self.domains[x].remove(word)
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is empty, add all arcs to the queue
        if arcs is None:
            arcs_none = list()
            for var1 in self.crossword.variables:
                for var2 in self.crossword.variables:
                    if var1 == var2:
                        continue
                    else:
                        overlap = self.crossword.overlaps[var1, var2]
                        if overlap is None:
                            continue
                        if ((var1, var2) in arcs_none) or ((var2, var1) in arcs_none):
                            continue
                        else:
                            arcs_none.append((var1, var2))
            arcs = arcs_none

        # WHile there are arcs
        while arcs:
            # Get arc to analyse
            current_arc = arcs.pop(0)
            # print(current_arc)
            x, y = current_arc
            # Revise variables based on arc. If revision true, actions required.
            if self.revise(x, y):
                # If domain of x is None, unsolveable
                if len(self.domains[x]) == 0:
                    return False
                # Get x neighbors, not includiong y, and add to the queue
                x_neighbors_revised = self.crossword.neighbors(x)
                x_neighbors_revised.remove(y)
                for z in x_neighbors_revised:
                    arcs.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        number_vars = self.crossword.variables
        if len(assignment) == number_vars:
            return True
        return False

    def consistent(self, assignment, new_var):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_words = list()
        for variable in assignment:
            if variable == new_var:
                continue
            used_words.append(assignment[variable])
        for variable in assignment:
            if variable is None:
                break
            if assignment[variable] not in used_words:
                if len(assignment[variable]) == variable.length:
                    if len(assignment) == 0 or len(assignment) == 1:
                        return True
                    # print("")
                    # print(f"Banked word length: {len(assignment[variable])}")
                    # print(f"variable length: {variable.length}")

                    # Check neighbor overlaps
                    neighbors = self.crossword.neighbors(variable)
                    overlap_check = True

                    for neighbor in neighbors:
                        if neighbor not in assignment:
                            continue
                        else:
                            i, j = self.crossword.overlaps[variable, neighbor]
                            if assignment[variable][i] != assignment[neighbor][j]:
                                overlap_check = False
                    if overlap_check:
                        return True
        return False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        neighbors = self.crossword.neighbors(var)
        domain_count = dict()
        for word in self.domains[var]:
            counter = 0
            for neighbor in neighbors:
                i, j = self.crossword.overlaps[var, neighbor]
                for corr_word in self.domains[neighbor]:
                    if word[i] == corr_word[j]:
                        counter += 1
            domain_count[word] = counter
        sorted_list = sorted(domain_count, key=domain_count.get, reverse=True)
        return sorted_list


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        domain_size = dict()
        for variable in self.crossword.variables - assignment.keys():
            domain_size[variable] = len(self.domains[variable])
        sorted_list = sorted(domain_size, key=domain_size.get, reverse=True)
        
        return sorted_list[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.crossword.variables):
            # print(f"length of assignment: {len(assignment)}")
            # print(f"Number of Variables: {len(self.crossword.variables)}")
            return assignment
        else:
            var = self.select_unassigned_variable(assignment)
            for value in self.order_domain_values(var, assignment):
                assignment[var] = value
                if self.consistent(assignment, var):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return assignment
                del assignment[var]
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result;
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
