from pycparser import c_ast


class OpVisitor(c_ast.NodeVisitor):
    """
    Visitor of nodes in AST which have 'op' as one of the attributes
    """
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def generic_visit(self, node):
        """

        :param node:
        :return:
        """
        if "op" in node.__slots__:
            self.nodelist.append(node)
        for c in node:
            self.generic_visit(c)

    def get_nodelist(self):
        """

        :return:
        """
        return self.nodelist
