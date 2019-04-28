from pycparser import c_ast


class ConstantVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of constant nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_Constant(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
