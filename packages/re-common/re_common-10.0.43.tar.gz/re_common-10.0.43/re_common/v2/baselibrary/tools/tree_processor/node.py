class TreeNode:
    def __init__(self, cid, count):
        self.id = cid
        self.count = count
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def is_leaf(self):
        return len(self.children) == 0