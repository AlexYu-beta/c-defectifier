from visitors.BinaryOpVisitor import BinaryOpVisitor
from visitors.AssignmentVisitor import AssignmentVisitor
from visitors.IfVisitor import IfVisitor
from visitors.IDVisitor import IDVisitor
from visitors.TypeDeclVisitor import TypeDeclVisitor

from utils.fs_util import generate_exp_output
from utils.random_picker import random_pick, gen_random
from pycparser import c_ast, c_generator

c_relational_binary_operator_set = {'>', '<', '>=', '<=', '==', '!='}
generator = c_generator.CGenerator()


def defectify_ORRN(ast, task_name, mode, logger, outer_count):
    """
    apply ORRN to ast
    :param ast:
    :param task_name:
    :param mode
    :return:
    """
    visitor = BinaryOpVisitor(ast, "ORRN_RELATIONAL", task_name)
    visitor.visit(ast)
    nodelist = visitor.get_nodelist()
    if mode == "RANDOM":
        nodelist = [random_pick(nodelist, None)]
    count = 0
    for node in nodelist:
        current_op = node.op
        if current_op in c_relational_binary_operator_set:
            replace_ops = c_relational_binary_operator_set - set(current_op)
            for replace_op in replace_ops:
                count += 1
                node.op = replace_op
                # save c file
                if outer_count:
                    generate_exp_output(str(outer_count) + ".c", task_name, ast)
                else:
                    generate_exp_output(str(count) + ".c", task_name, ast)
                # create log
                logger.log_ORRN(node.coord, current_op, replace_op)


def defectify_OEDE(ast, task_name, mode, logger, outer_count):
    """
    apply OEDE to ast
    :param ast
    :param task_name
    :param logger
    :return:
    """
    # convert = to ==
    visitor_A = AssignmentVisitor(ast, "OEDE_NORMAL", task_name)
    visitor_A.visit(ast)
    nodelist = visitor_A.get_nodelist()
    if mode == "RANDOM":
        nodelist = [random_pick(nodelist, None)]
    count = 0
    for node in nodelist:
        if node.op == "=":
            count += 1
            node.op = "=="
            # save c file
            if outer_count:
                generate_exp_output("A" + str(outer_count) + ".c", task_name, ast)
            else:
                generate_exp_output("A" + str(count) + ".c", task_name, ast)
            # create log
            logger.log_OEDE(node.coord, "=", "==")
            node.op = "="
    count = 0
    visitor_B = BinaryOpVisitor(ast, "OEDE_NORMAL", task_name)
    visitor_B.visit(ast)
    nodelist = visitor_B.get_nodelist()
    if mode == "RANDOM":
        nodelist = [random_pick(nodelist, None)]
    for node in nodelist:
        if node.op == "==":
            count += 1
            node.op = "="
            # save c file
            if outer_count:
                generate_exp_output("B" + str(outer_count) + ".c", task_name, ast)
            else:
                generate_exp_output("B" + str(count) + ".c", task_name, ast)
            # create log
            logger.log_OEDE(node.coord, "==", "=")
            node.op = "=="


def defectify_OILN(ast, task_name, mode, logger, outer_count):
    """

    :param ast:
    :param task_name:
    :param logger
    :return:
    """
    def add_and_or(node, count, op):
        id_visitor = IDVisitor(node.cond, mode, task_name)
        id_visitor.visit(node.cond)
        ids = set(id_visitor.get_name_list())
        type_decl_visitor = TypeDeclVisitor(ast, mode, task_name)
        type_decl_visitor.visit(ast)
        type_decls = type_decl_visitor.get_nodelist()
        if mode == "RANDOM":
            ids = [random_pick(list(ids), None)]
        for id in ids:
            id_type = "NOT_DECLARED"
            for type_decl in type_decls:
                if id == type_decl.declname:
                    # this may not be true, do not know why here <type names> is a list of names yet
                    id_type = type_decl.type.names[0]
            if id_type == "NOT_DECLARED":
                continue
            # use a simplified strategy to construct randomized branch condition
            op_add = random_pick(["==", "!="], None)
            left_add = c_ast.ID(name=id)
            right_add = c_ast.Constant(type=id_type,
                                       value=str(gen_random(id_type)))
            cond_add = c_ast.BinaryOp(op=op_add,
                                      left=left_add,
                                      right=right_add)
            add_left = random_pick([True, False], None)
            if add_left:
                node.cond = c_ast.BinaryOp(op=op,
                                           left=cond_add,
                                           right=node.cond,
                                           coord=node.cond.coord)
            else:
                node.cond = c_ast.BinaryOp(op=op,
                                           left=node.cond,
                                           right=cond_add,
                                           coord=node.cond.coord)
            if op == "&&":
                if outer_count:
                    generate_exp_output("test_add_and_{}.c".format(outer_count), task_name, ast)
                else:
                    generate_exp_output("test_add_and_{}.c".format(count), task_name, ast)
                logger.log_OILN(node.cond.coord, "add_and")
            else:
                if outer_count:
                    generate_exp_output("test_add_or_{}.c".format(outer_count), task_name, ast)
                else:
                    generate_exp_output("test_add_or_{}.c".format(count), task_name, ast)
                logger.log_OILN(node.cond.coord, "add_or")
            # retrieve ast
            if add_left:
                node.cond = c_ast.BinaryOp(op=node.cond.right.op,
                                           left=node.cond.right.left,
                                           right=node.cond.right.right,
                                           coord=node.cond.coord)
            else:
                node.cond = c_ast.BinaryOp(op=node.cond.left.op,
                                           left=node.cond.left.left,
                                           right=node.cond.left.right,
                                           coord=node.cond.coord)

    def del_and_or(node, count, op):
        cond = node.cond
        if cond.op == op:
            # save previous conditions
            temp_op, temp_left, temp_right = cond.op, cond.left, cond.right
            # condition loosen
            left = cond.left
            cond.op, cond.left, cond.right = left.op, left.left, left.right
            if op == "&&":
                if outer_count:
                    generate_exp_output("test_del_and_{}.c".format(outer_count), task_name, ast)
                else:
                    generate_exp_output("test_del_and_{}.c".format(count), task_name, ast)
            else:
                if outer_count:
                    generate_exp_output("test_del_or{}.c".format(outer_count), task_name, ast)
                else:
                    generate_exp_output("test_del_or{}.c".format(count), task_name, ast)
            logger.log_OILN(node.coord, "del_" + op)
            # retrieve previous conditions
            cond.op, cond.left, cond.right = temp_op, temp_left, temp_right

    def add_and(node, count):
        add_and_or(node, count, "&&")

    def add_or(node, count):
        add_and_or(node, count, "||")

    def del_and(node, count):
        del_and_or(node, count, "&&")

    def del_or(node, count):
        del_and_or(node, count, "||")

    def negate_cond(node, count):
        if type(node.cond.left) == c_ast.UnaryOp and node.cond.left.op == '!':
            # find a ! expression
            # save current part of ast
            temp = c_ast.UnaryOp(op='!',
                                 expr=node.cond.left.expr,
                                 coord=node.cond.left.coord)
            node.cond.left = node.cond.left.expr
            if outer_count:
                generate_exp_output("test_denegate_{}.c".format(outer_count), task_name, ast)
            else:
                generate_exp_output("test_denegate_{}.c".format(count), task_name, ast)
            logger.log_OILN(node.cond.left.coord, "denegate")
            # retrieve ast
            node.cond.left = temp
        else:
            node.cond.left = c_ast.UnaryOp(op='!',
                                           expr=node.cond.left,
                                           coord=node.cond.left.coord)
            if outer_count:
                generate_exp_output("test_negate_{}.c".format(outer_count), task_name, ast)
            else:
                generate_exp_output("test_negate_{}.c".format(count), task_name, ast)
            logger.log_OILN(node.cond.left.coord, "negate")
            # retrieve ast
            node.cond.left = node.cond.left.expr

    ifVisitor = IfVisitor(ast, mode, task_name)
    ifVisitor.visit(ast)
    nodes = ifVisitor.get_nodelist()
    methods = [add_and, add_or, del_and, del_or, negate_cond]

    # code for debugging
    # mode = "RANDOM"
    # nodes = [nodes[4]]
    # methods = [del_and]
    ####
    count = 0

    if mode == "RANDOM":
        node = random_pick(nodes, None)
        if node.cond.op != "&&" and del_and in methods:
            methods.remove(del_and)
        if node.cond.op != "||" and del_or in methods:
            methods.remove(del_or)
        random_pick(methods, None)(node, 1)
    elif mode == "DEBUG":
        for node in nodes:
            for method in methods:
                count += 1
                method(node, count)


def defectify_test(ast, task_name, mode, logger):
    """
    test
    loose if condition
    :param ast:
    :param task_name:
    :param mode
    :return:
    """
    pass


def defectify(ast, task_name, defectify_type, mode, logger, outer_count):
    """
    generic defectify entry
    :param ast:                 ast structure
    :param task_name:           experiment name
    :param defectify_type:      what kind of defect to introduce
    :param mode:                defectify mode
        - DEBUG:                create all defectify possibilities
        - RANDOM:               choose one defectify possibility randomly
    :param logger:              a Logger instance
    :return:
    """
    method_name = "defectify_" + defectify_type
    try:
        func = globals()[method_name]
    except KeyError:
        print("Err: function {} has not been registered in ./defect/defectify".format(method_name))
        return
    globals()[method_name](ast, task_name, mode, logger, outer_count)
