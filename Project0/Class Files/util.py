class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []
        """Creates empty frontier in form of list"""

    def add(self, node):
        self.frontier.append(node)
        """Appends frontier by adding node to end of list"""

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)
        """checks if frontier contains particular state"""

    def empty(self):
        return len(self.frontier) == 0
        """Checks if frontieer is empty"""

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node
        """Removes last item from list (Stack Frontier,
            last in, first out)"""


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
        """Removes first item from list (Queue frontier,
            first in, first out)"""
