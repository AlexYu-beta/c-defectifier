from pycparser import c_ast


class DaddyVisitor(c_ast.NodeVisitor):
    """
    Who's your daddy now?
    """
    def __init__(self, ast, son):
        """

        :param ast:
        """
        self.ast = ast
        self.son = son
        self.dad = None

    def generic_visit(self, node):
        """

        :param node:
        :return:
        """
        for slot in node.__slots__:
            if self.son == node.__getattribute__(slot):
                self.dad = node
                break
        for c in node:
            self.generic_visit(c)

    def get_dad(self):
        """

        :return:
        """
        return self.dad
