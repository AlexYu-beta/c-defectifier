from pycparser import c_ast


class SwitchVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of switch nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_Switch(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
