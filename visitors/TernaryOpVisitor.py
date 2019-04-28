from pycparser import c_ast


class TernaryOpVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of ternary operator nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_TernaryOp(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
