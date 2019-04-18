from pycparser import c_ast


class TypeDeclVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of type declaration node
    """
    def __init__(self, ast, mode, task_name):
        """

        :param ast:                 ast root
        :param mode:                mode of type declaration visitor
            ...
        :param task_name
        """
        self.ast = ast
        self.mode = mode
        self.task_name = task_name
        self.genCount = 0
        self.nodelist = []

    def visit_TypeDecl(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist
