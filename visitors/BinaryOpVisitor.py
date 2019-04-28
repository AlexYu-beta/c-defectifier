from pycparser import c_ast

c_relational_binary_operator_set = {'>', '<', '>=', '<=', '==', '!='}


class BinaryOpVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of binary operator node
    """
    def __init__(self, ast):
        """

        :param ast:                 ast root
        """
        self.ast = ast
        self.nodelist = []

    def visit_BinaryOp(self, node):
        """
        a visit of a binary operator node means generating at least one defectify strategy on the node
        :param node:                the node to visit
        :return:
        """
        self.nodelist.append(node)
        if node.left:
            self.visit(node.left)
        if node.right:
            self.visit(node.right)

    def get_nodelist(self):
        return self.nodelist
