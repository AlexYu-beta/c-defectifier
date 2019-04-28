from pycparser import c_ast


class DoWhileVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of do-while nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_DoWhile(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
