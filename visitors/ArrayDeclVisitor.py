from pycparser import c_ast


class ArrayDeclVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of array declaration nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_ArrayDecl(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist

