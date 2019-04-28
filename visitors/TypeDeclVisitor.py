from pycparser import c_ast


class TypeDeclVisitor(c_ast.NodeVisitor):
    """
    a simple visitor of type declaration node
    """
    def __init__(self, ast):
        """

        :param ast:                 ast root
        """
        self.ast = ast
        self.nodelist = []

    def visit_TypeDecl(self, node):
        self.nodelist.append(node)

    def get_nodelist(self):
        return self.nodelist

    def get_node(self, name):
        ret = None
        for type_decl in self.nodelist:
            if type_decl.declname == name:
                ret = type_decl
                break
        return ret
