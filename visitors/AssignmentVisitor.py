from pycparser import c_ast


class AssignmentVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of assignment node
    """
    def __init__(self, ast, mode, task_name):
        """

        :param ast:                 ast root
        :param mode:                mode of assignment visitor
            "OEDE_NORMAL":          ==, when trying OEDE
            ...
        :param task_name
        """
        self.ast = ast
        self.mode = mode
        self.task_name = task_name
        self.genCount = 0
        self.nodelist = []

    def visit_Assignment(self, node):
        self.nodelist.append(node)
        if node.lvalue:
            self.visit(node.lvalue)
        if node.rvalue:
            self.visit(node.rvalue)

    def get_nodelist(self):
        return self.nodelist
