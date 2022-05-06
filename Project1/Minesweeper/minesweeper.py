import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #Known mines indicate a cell count is equivalent to the number of
        # surrounding unknown cells based on the current knowledge
        #Self.count = cell number
        #self.cells = surrounding cells
        if self.count != 0 and self.count == len(self.cells):
            return self.cells

        #If not, return empty set
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #We know a surrounding cell is safe if the cell.count is equal to
        #the number of known_mines surrounding the cell
        ''''''
        #Cells are known to be safe only if the cell.count is zero

        if self.count == 0:
            return self.cells
        #If not, return empty set
        return set()



    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #Make sure cell is in sentence
        if cell not in self.cells:
            return
        #If cell in sentence, remove and subtract count by 1
        self.cell.remove(cell)
        self.count -= 1
        return


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Make sure cell is in sentence
        if cell not in self.cells:
            return
        # If cell in sentence, remove. no count change required
        self.cells.remove(cell)

        return



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            if sentence:
                sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base
        #       based on the value of `cell` and `count`
            # Get Neighbors
        cell_neighbors = self.neighbors(cell)
            # Update knowledge with known neighbors and count
        self.knowledge.append(Sentence(cell_neighbors, count))

        # 4) mark any additional cells as safe or as mines
        #       if it can be concluded based on the AI's knowledge base

        for sentence in self.knowledge:

            # Get Known mines and safes
            if sentence:
                sentence_safes = sentence.known_safes()
                sentence_mines = sentence.known_mines()

                for safe in sentence_safes:
                    if safe not in self.safes:
                        self.safes.add(safe)

                for mine in sentence_mines:
                    if mine not in self.mines:
                        self.mines.add(mine)

        # 5) add any new sentences to the AI's knowledge base
        #       if they can be inferred from existing knowledge
        self.new_knowledge = []

        for sentence1 in self.knowledge:
            if sentence1:
                for sentence2 in self.knowledge:
                    if sentence2:
                        if sentence1.cells == sentence2.cells:
                            continue
                        elif sentence1.cells.issuperset(sentence2.cells):
                            new_cells = sentence2.cells - sentence1.cells
                            new_count = sentence2.count - sentence1.count
                            self.new_knowledge.append(Sentence(new_cells, new_count))

        if len(self.new_knowledge) != 0:
            self.knowledge.append(self.new_knowledge)
        self.new_knowledge.clear()



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        unplayed_safes = self.safes - self.moves_made
        if len(unplayed_safes) == 0:
            return None
        return unplayed_safes.pop()


    @property
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        random_cells = set()
        # Loop over entire board
        for i in range(self.width):
            for j in range(self.height):
                # If known safe tile (not required cause random move req)
                if (i, j) in self.safes:
                    continue
                # If known mine tile
                if (i, j) in self.mines:
                    continue
                # If square already filled
                if (i, j) in self.moves_made:
                    continue
                random_cells.add((i, j))
        # If no options, return None
        if len(random_cells) == 0:
            return None

        # Return random choice from random cells
        return random_cells.pop()

    def neighbors(self, cell):
        cell_neighbors = set()

        # Loop over entire board, seeking neighbors
        for i in range(self.height):
            for j in range(self.width):
                # Search border of cell for suitable neighbors
                # If cell within one of current cell, it is neighbor
                if (
                        (abs(i - cell[0]) == 1 and abs(j - cell[1]) == 1) or
                        (abs(i - cell[0]) == 0 and abs(j - cell[1]) == 1) or
                        (abs(i - cell[0]) == 1 and abs(j - cell[1]) == 0)
                ):
                    #If known neighbor, we good
                    if (i, j) in self.safes:
                        continue
                    # If known mine, we good
                    elif (i, j) in self.mines:
                        continue
                    # Otherwise, cell is a neighbor
                    else:
                        cell_neighbors.add((i, j))
        return cell_neighbors

