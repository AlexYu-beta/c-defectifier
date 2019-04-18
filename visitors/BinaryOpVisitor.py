from pycparser import c_ast

c_relational_binary_operator_set = {'>', '<', '>=', '<=', '==', '!='}


class BinaryOpVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of binary operator node
    """
    def __init__(self, ast, mode, task_name):
        """

        :param ast:                 ast root
        :param mode:                mode of binary operator visitor
            "ORRN_RELATIONAL":      only visit relational binary operators, when trying ORRN
            "OEDE_NORMAL":          ==, when trying OEDE
            ...
        :param task_name
        """
        self.ast = ast
        self.mode = mode
        self.task_name = task_name
        self.genCount = 0
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
