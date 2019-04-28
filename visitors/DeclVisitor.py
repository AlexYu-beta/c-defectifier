from pycparser import c_ast


class DeclVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of declaration nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_Decl(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist

