from pycparser import c_ast


class CompoundVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of compound nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_Compound(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
