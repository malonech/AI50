import sys

from crossword import *


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
        # print(assignment)
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

        # To future Chris, this function is as such since we cannot modify self.domains[variable]
        # When it defines our FOR loop. Here, we make our revisions after the loop.

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

        # Initialize remove list for loop
        remove = list()

        # Loop through x domain. Initialize found variable and remove list
        for word_x in self.domains[x]:
            found = False
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

    # Again, note that we had to work around not being able to modify self.domains[variable]
    # since it defines our FOR loop

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
            # Initialize arc list
            arcs = list()
            # For each variable in the crossword
            for variable in self.crossword.variables:
                # Loop through neighbors and add them to arcs list
                for neighbor in self.crossword.neighbors(variable):
                    arcs.append((variable, neighbor))

        # While arcs are present
        while arcs:
            # Get first arc in the queue to analyse
            current_arc = arcs.pop(0)
            # print(current_arc)
            x, y = current_arc
            # Revise variables based on arc. If revision true, actions required.
            if self.revise(x, y):
                # If domain of x is None, unsolvable, return false
                if len(self.domains[x]) == 0:
                    return False
                # Get x neighbors, not including y, and add to the arc queue
                x_neighbors_revised = self.crossword.neighbors(x)
                x_neighbors_revised.remove(y)
                # Loop through x neighbors and add arcs to queue
                for neighbor in x_neighbors_revised:
                    arcs.append((neighbor, x))
        # Once arcs is empty, return True signifying a solved puzzle
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment, new_var):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Initialize used words list
        used_words = list()
        # Loop through assignment variables and update used_words list
        for variable in assignment:
            if variable == new_var:
                continue
            used_words.append(assignment[variable])

        # Initialize counter to check all consistent
        counter = 0

        # If used_words list has unique items
        if len(set(used_words)) == len(used_words):
            # Loop through assignment variables
            for variable in assignment:
                # ensure variable assignment are of correct length
                if len(assignment[variable]) == variable.length:
                    # If no multiple assignments, guaranteed consistent
                    if len(assignment) == 0 or len(assignment) == 1:
                        return True

                    # Check neighbor overlaps
                    # Get variables neighbors
                    neighbors = self.crossword.neighbors(variable)

                    # Loop through all variable neighbors
                    for neighbor in neighbors:
                        # Skip if neighbor not assigned. Only need to consider assigned variables
                        if neighbor not in assignment:
                            continue
                        else:
                            # Get overlapping coordinate
                            i, j = self.crossword.overlaps[variable, neighbor]
                            if assignment[variable][i] != assignment[neighbor][j]:
                                return False
                    # Got through all neighbors. this variable is consistent
                    counter += 1
            # If check counter equals length of assignment, we are consistent
            if counter == len(assignment):
                return True
            return False


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Define neighbors and domain/count dictionary
        neighbors = self.crossword.neighbors(var)

        # Define variable domain. Assigned words to be removed.
        unassigned_domain = self.domains[var]

        # Loop through assignment variables
        for variable in assignment:
            if assignment[variable] in unassigned_domain:
                # Remove assigned words
                unassigned_domain.remove(assignment[variable])
            # Remove neighbors with assigned words
            if variable in neighbors:
                neighbors.remove(variable)

        # Initialize dictionary to store LCV Heuristic
        domain_remove_count = dict()

        # Loop through available words
        for word in unassigned_domain:
            counter = 0
            # Compare word with neighboring domain (Not including defined neighbors)
            for neighbor in neighbors:
                # Get overlap coordinate
                i, j = self.crossword.overlaps[var, neighbor]
                # Loop through neighbors domain for comparison
                for corresponding_word in self.domains[neighbor]:
                    # If coordinates do not correlate, the neighbors word can be ruled-out
                    if word[i] != corresponding_word[j]:
                        # Increment the ruled-out counter
                        counter += 1
            # Update LCV heuristic dictionary
            domain_remove_count[word] = counter
        # Sort list by HCV Heuristic value (Ascending)
        sorted_list = sorted(domain_remove_count, key=domain_remove_count.get, reverse=False)

        return sorted_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Initialize dictionary to document domain size
        domain_size = dict()

        # Loop though variables that are not defined in assignment
        for variable in self.crossword.variables - assignment.keys():
            # Update dictionary with the length of the variables domain)
            domain_size[variable] = len(self.domains[variable])
        # Sort the dictionary by domain size
        sorted_list = sorted(domain_size, key=domain_size.get, reverse=False)

        # Check if comparison required
        if len(sorted_list) <= 1:
            return sorted_list[0]
        # Then check for tie at the top
        elif domain_size[sorted_list[0]] > domain_size[sorted_list[1]]:
            # Our sorted list has a defined leader
            return sorted_list[0]
        # Now we know a tie exists at the top
        else:
            # Initialize dictionary used for checking domain count tie & add max
            tie_check = dict()
            tie_check[sorted_list[0]] = len(self.crossword.neighbors(sorted_list[0]))

            # Loop through unassigned variables not including our max
            for variable in self.crossword.variables - assignment.keys():
                # Skip max variable
                if variable == sorted_list[0]:
                    continue
                # Check for tie
                if domain_size[sorted_list[0]] > domain_size[variable]:
                    # We do not care about  this variable
                    pass
                else:
                    # Here we know the variable is tied with our max
                    # Update tie_check with count of variable neighbors
                    tie_check[variable] = len(self.crossword.neighbors(variable))
            # Sort variables by variable value
            sorted_tie_check = sorted(tie_check, key=tie_check.get, reverse=True)
            # Return variable at the top of the list (Largest Domain)
            # If tie present, it doesn't matter. "Arbitrary", so I choose the first variable
            return sorted_tie_check[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
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
