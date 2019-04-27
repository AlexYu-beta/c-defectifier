from pycparser import c_ast


class ConstantVisitor(c_ast.NodeVisitor):
    """
        a simple visitor of constant nodes
    """
    def __init__(self, ast, mode, task_name):
        """

        :param ast:
        :param mode:
        :param task_name:
        """
        self.ast = ast
        self.mode = mode
        self.task_name = task_name
        self.genCount = 0
        self.nodelist = []

    def visit_Constant(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
