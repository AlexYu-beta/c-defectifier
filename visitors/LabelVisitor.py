from pycparser import c_ast


class LabelVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of label
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.genCount = 0
        self.nodelist = []

    def visit_Label(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
