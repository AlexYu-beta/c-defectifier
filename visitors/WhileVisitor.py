from pycparser import c_ast


class WhileVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of while nodes
    """
    def __init__(self, ast):
        """

        :param ast:
        :param mode:
        :param task_name:
        """
        self.ast = ast
        self.nodelist = []

    def visit_While(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
