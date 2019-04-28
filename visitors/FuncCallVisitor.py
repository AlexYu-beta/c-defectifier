from pycparser import c_ast


class FuncCallVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of function call nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_FuncCall(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
