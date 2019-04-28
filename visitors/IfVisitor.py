from pycparser import c_ast

c_relational_binary_operator_set = {'>', '<', '>=', '<=', '==', '!='}


class IfVisitor(c_ast.NodeVisitor):
    def __init__(self, ast):
        """

        :param ast:
        """
        self.ast = ast
        self.nodelist = []

    def visit_If(self, node):
        self.nodelist.append(node)
        if node.iftrue:
            self.visit(node.iftrue)
        if node.iffalse:
            self.visit(node.iffalse)

    def get_nodelist(self):
        return self.nodelist
