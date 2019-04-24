from pycparser import c_ast


class IDVisitor(c_ast.NodeVisitor):
    def __init__(self, ast, mode, task_name):
        """

        :param ast:
        :param mode:
        :param task_name:
        """
        self.ast = ast
        self.mode = mode
        self.task_name = task_name
        self.nodes = []
        self.names = []

    def visit_ID(self, node):
        name = node.name
        self.nodes.append(node)
        self.names.append(name)

    def get_id_list(self):
        return self.nodes

    def get_name_list(self):
        return self.names

    def get_nodes(self, name):
        ret = []
        for node in self.nodes:
            if node.name == name:
                ret.append(node)
        return ret
