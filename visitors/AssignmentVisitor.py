from pycparser import c_ast


class AssignmentVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of assignment node
    """
    def __init__(self, ast):
        """

        :param ast:                 ast root
        """
        self.ast = ast
        self.nodelist = []

    def visit_Assignment(self, node):
        self.nodelist.append(node)
        if node.lvalue:
            self.visit(node.lvalue)
        if node.rvalue:
            self.visit(node.rvalue)

    def get_nodelist(self):
        return self.nodelist
