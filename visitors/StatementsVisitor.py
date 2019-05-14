from pycparser import c_ast


class StatementsVisitor(c_ast.NodeVisitor):
    """
    Visitor of nodes in AST which have 'stmts' as one of the attributes
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
        if "stmts" in node.__slots__:
            self.nodelist.append(node)
        else:
            pass
        for c in node:
            self.generic_visit(c)

    def get_nodelist(self):
        """

        :return:
        """
        return self.nodelist
