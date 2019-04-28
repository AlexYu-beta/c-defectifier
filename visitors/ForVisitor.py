from pycparser import c_ast


class ForVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of for nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_For(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
