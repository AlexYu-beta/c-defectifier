from pycparser import c_ast


class ConditionVisitor(c_ast.NodeVisitor):
    """
    Visitor of nodes in AST which have 'cond' as one of the attributes
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
        if "cond" in node.__slots__:
            self.nodelist.append(node)
        for c in node:
            self.generic_visit(c)

    def get_nodelist(self):
        """

        :return:
        """
        return self.nodelist
