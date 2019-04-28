from visitors.AssignmentVisitor import AssignmentVisitor
from visitors.BinaryOpVisitor import BinaryOpVisitor
from visitors.CaseVisitor import CaseVisitor
from visitors.CompoundVisitor import CompoundVisitor
from visitors.ConditionVisitor import ConditionVisitor
from visitors.ConstantVisitor import ConstantVisitor
from visitors.DeclVisitor import DeclVisitor
from visitors.DefaultVisitor import DefaultVisitor
from visitors.DoWhileVisitor import DoWhileVisitor
from visitors.ForVisitor import ForVisitor
from visitors.FuncCallVisitor import FuncCallVisitor
from visitors.IDVisitor import IDVisitor
from visitors.IfVisitor import IfVisitor
from visitors.LabelVisitor import LabelVisitor
from visitors.SwitchVisitor import SwitchVisitor
from visitors.TernaryOpVisitor import TernaryOpVisitor
from visitors.TypeDeclVisitor import TypeDeclVisitor
from visitors.WhileVisitor import WhileVisitor


from utils.fs_util import generate_exp_output
from utils.random_picker import random_pick, random_pick_probless, RandomPicker
from utils.ast_util import parse_fileAST_exts
from pycparser import c_ast, c_generator

c_relational_binary_operator_set = {'>', '<', '>=', '<=', '==', '!='}
c_arithmetic_binary_operator_set = {'+', '-', '*', '/', '%'}
generator = c_generator.CGenerator()


def defectify_ORRN(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    condition_visitor = ConditionVisitor(ast)
    condition_visitor.generic_visit(ast)
    # 1. find out all the nodes with 'cond' as one of the attributes
    nodelist = condition_visitor.get_nodelist()
    available_node_list = [node for node in nodelist if node.cond.op in c_relational_binary_operator_set]
    if len(available_node_list) == 0:
        print("Warning: no available node can be defectified with ORRN.")
        return False
    # 2. randomly pick a node
    node = random_pick_probless(available_node_list)
    current_op = node.cond.op
    replace_ops = c_relational_binary_operator_set - {current_op}
    # 3. randomly pick a replacement
    replace_op = random_pick_probless(list(replace_ops))
    # 4. replace
    node.cond.op = replace_op
    # create log
    logger.log_ORRN(node.coord, current_op, replace_op)
    return True


def defectify_OILN_add_and(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    if "random_picker" in exp_spec_dict.keys():
        random_picker_spec = exp_spec_dict["random_picker"]
        random_picker = RandomPicker(random_picker_spec["random_int_list"], random_picker_spec["random_chr_list"])
    else:
        random_picker = RandomPicker(None, None)

    global_ids, global_funcs = parse_fileAST_exts(ast)
    func = None
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    # 3. get all the available type declarations from current if condition scope and randomly pick one identifier
    type_decls = type_decls + global_ids
    id = random_pick_probless(id_visitor.get_name_list())
    id_type = "NOT_DECLARED"
    for type_decl in type_decls:
        if id == type_decl.declname:
            # this may not be true, do not know why here <type names> is a list of names yet
            id_type = type_decl.type.names[0]
            break
    if id_type == "NOT_DECLARED":
        print("Err: Identifier not declared.")
        return False
    # 4. use a simplified strategy to construct randomized branch condition
    op_add = random_pick_probless(["==", "!=", ">", "<", ">=", "<="])
    left_add = c_ast.ID(name=id)
    right_add = c_ast.Constant(type=id_type,
                               value=str(random_picker.gen_random(id_type)))
    cond_add = c_ast.BinaryOp(op=op_add,
                              left=left_add,
                              right=right_add)
    add_left = random_pick_probless([True, False])
    if add_left:
        node.cond = c_ast.BinaryOp(op="&&",
                                   left=cond_add,
                                   right=node.cond,
                                   coord=node.cond.coord)
    else:
        node.cond = c_ast.BinaryOp(op="&&",
                                   left=node.cond,
                                   right=cond_add,
                                   coord=node.cond.coord)

    logger.log_OILN(node.cond.coord, "add_and")
    # *5. retrieve ast
    # if add_left:
    #     node.cond = c_ast.BinaryOp(op=node.cond.right.op,
    #                                left=node.cond.right.left,
    #                                right=node.cond.right.right,
    #                                coord=node.cond.coord)
    # else:
    #     node.cond = c_ast.BinaryOp(op=node.cond.left.op,
    #                                left=node.cond.left.left,
    #                                right=node.cond.left.right,
    #                                coord=node.cond.coord)
    return True


def defectify_OILN_add_or(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    if "random_picker" in exp_spec_dict.keys():
        random_picker_spec = exp_spec_dict["random_picker"]
        random_picker = RandomPicker(random_picker_spec["random_int_list"], random_picker_spec["random_chr_list"])
    else:
        random_picker = RandomPicker(None, None)

    global_ids, global_funcs = parse_fileAST_exts(ast)
    func = None
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    # 3. get all the available type declarations from current if condition scope and randomly pick one identifier
    type_decls = type_decls + global_ids
    id = random_pick_probless(id_visitor.get_name_list())
    id_type = "NOT_DECLARED"
    for type_decl in type_decls:
        if id == type_decl.declname:
            # this may not be true, do not know why here <type names> is a list of names yet
            id_type = type_decl.type.names[0]
            break
    if id_type == "NOT_DECLARED":
        print("Err: Identifier not declared.")
        return False
    # 4. use a simplified strategy to construct randomized branch condition
    op_add = random_pick_probless(["==", "!=", ">", "<", ">=", "<="])
    left_add = c_ast.ID(name=id)
    right_add = c_ast.Constant(type=id_type,
                               value=str(random_picker.gen_random(id_type)))
    cond_add = c_ast.BinaryOp(op=op_add,
                              left=left_add,
                              right=right_add)
    add_left = random_pick_probless([True, False])
    if add_left:
        node.cond = c_ast.BinaryOp(op="||",
                                   left=cond_add,
                                   right=node.cond,
                                   coord=node.cond.coord)
    else:
        node.cond = c_ast.BinaryOp(op="||",
                                   left=node.cond,
                                   right=cond_add,
                                   coord=node.cond.coord)

    logger.log_OILN(node.cond.coord, "add_or")
    # *5. retrieve ast
    # if add_left:
    #     node.cond = c_ast.BinaryOp(op=node.cond.right.op,
    #                                left=node.cond.right.left,
    #                                right=node.cond.right.right,
    #                                coord=node.cond.coord)
    # else:
    #     node.cond = c_ast.BinaryOp(op=node.cond.left.op,
    #                                left=node.cond.left.left,
    #                                right=node.cond.left.right,
    #                                coord=node.cond.coord)
    return True


def defectify_OILN_del_and(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    func = None
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond.op != "&&":
        print("Warning: no && can be deleted.")
        return False
    cond = node.cond
    # 3. save previous conditions
    temp_op, temp_left, temp_right = cond.op, cond.left, cond.right
    del_left = random_pick_probless([True, False])
    if del_left:
        left = cond.left
        cond.op, cond.left, cond.right = left.op, left.left, left.right
    else:
        right = cond.right
        cond.op, cond.left, cond.right = right.op, right.left, right.right
    logger.log_OILN(node.coord, "del_and")
    # *4. retrieve previous conditions
    # cond.op, cond.left, cond.right = temp_op, temp_left, temp_right
    return True


def defectify_OILN_del_or(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    func = None
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond.op != "||":
        print("Warning: no || can be deleted.")
        return False
    cond = node.cond
    # 3. save previous conditions
    temp_op, temp_left, temp_right = cond.op, cond.left, cond.right
    left = cond.left
    cond.op, cond.left, cond.right = left.op, left.left, left.right
    logger.log_OILN(node.coord, "del_or")
    # *4. retrieve previous conditions
    # cond.op, cond.left, cond.right = temp_op, temp_left, temp_right
    return True


def defectify_OILN_negate_cond(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    func = None
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)

    if type(node.cond.left) == c_ast.UnaryOp and node.cond.left.op == '!':
        # find a ! expression
        # save current part of ast
        temp = c_ast.UnaryOp(op='!',
                             expr=node.cond.left.expr,
                             coord=node.cond.left.coord)
        node.cond.left = node.cond.left.expr
        logger.log_OILN(node.cond.left.coord, "denegate")
        # retrieve ast
        # node.cond.left = temp
    else:
        node.cond.left = c_ast.UnaryOp(op='!',
                                       expr=node.cond.left,
                                       coord=node.cond.left.coord)
        logger.log_OILN(node.cond.left.coord, "negate")
        # retrieve ast
        # node.cond.left = node.cond.left.expr
    return True


def defectify_OILN(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger
    :return:
    """
    OILN_EQUAL_PROB = True
    if "OILN" in exp_spec_dict.keys():
        oiln_spec = exp_spec_dict["OILN"]
        if len(oiln_spec) != 0:
            OILN_EQUAL_PROB = False
    if OILN_EQUAL_PROB:
        func = globals()[random_pick_probless(["defectify_OILN_add_and",
                                               "defectify_OILN_add_or",
                                               "defectify_OILN_del_and",
                                               "defectify_OILN_del_or",
                                               "defectify_OILN_negate_cond"])]
    else:
        func = globals()["defectify_" + random_pick(list(oiln_spec.keys()), list(oiln_spec.values()))]
    return func(ast, task_name, logger, exp_spec_dict)


def defectify_SRIF_replace_var(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    id_name_map = {}
    for global_id in global_ids:
        id_name_map[global_id.name] = global_id.type.type.names[0]
    func = None
    count = 0
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    if len(id_name_set) + len(global_ids) < 2:
        print("Warning: no replacement found.")
        return False
    target_id = random_pick_probless(ids)
    ids_remain = id_name_set - {target_id.name}
    global_ids_name = [item.name for item in global_ids]
    ids_remain = ids_remain.union(set(global_ids_name) - {target_id.name})
    # 3. figure out the type of the chosen identifier
    #  , and judge whether the chosen identifier can be replaced or be converted to expression
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        id_name_map[type_decl.declname] = type_decl.type.names[0]
    target_id_type = id_name_map[target_id.name]
    matched_ids = []
    for id_remain in ids_remain:
        if id_name_map[id_remain] == target_id_type:
            matched_ids.append(id_remain)
    if len(matched_ids) == 0:
        print("Warning: no replacement found.")
        return False
    # 4. randomly pick one matched identifier
    matched_id = random_pick_probless(matched_ids)
    temp = target_id.name
    target_id.name = matched_id
    logger.log_SRIF(node.coord, "replace var")
    # retrieve ast
    # target_id.name = temp
    return True


def defectify_SRIF_to_expr(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    if "random_picker" in exp_spec_dict.keys():
        random_picker_spec = exp_spec_dict["random_picker"]
        random_picker = RandomPicker(random_picker_spec["random_int_list"], random_picker_spec["random_chr_list"])
    else:
        random_picker = RandomPicker(None, None)

    global_ids, global_funcs = parse_fileAST_exts(ast)
    id_name_map = {}
    for global_id in global_ids:
        id_name_map[global_id.name] = global_id.type.type.names[0]
    func = None
    count = 0
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    target_id = random_pick_probless(ids)
    # 3. figure out the type of the chosen identifier
    # , and judge whether the chosen identifier can be converted to expression
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        id_name_map[type_decl.declname] = type_decl.type.names[0]
    target_id_type = id_name_map[target_id.name]
    if target_id_type == "char":
        print("Warning: cannot convert to expression.")
        return False

    # 4. search binary op from root
    binary_op_visitor = BinaryOpVisitor(node.cond)
    binary_op_visitor.visit(node.cond)
    binary_ops = binary_op_visitor.get_nodelist()
    if target_id_type in {"int", "short", "long"}:
        op = random_pick_probless(["+", "-", "*", "/", "%"])
    else:
        op = random_pick_probless(["+", "-", "*", "/"])
    value = random_picker.gen_random(target_id_type)
    value_const = c_ast.Constant(type=target_id_type,
                                 value=str(value))
    for binary_op in binary_ops:
        if binary_op.left == target_id:
            temp = target_id
            binary_op.left = c_ast.BinaryOp(op=op,
                                            left=target_id,
                                            right=value_const,
                                            coord=target_id.coord)

            logger.log_SRIF(target_id.coord, "to expr")
            # retrieve ast
            # binary_op.left = temp
            break
        elif binary_op.right == target_id:
            temp = target_id
            binary_op.right = c_ast.BinaryOp(op=op,
                                             left=target_id,
                                             right=value_const,
                                             coord=target_id.coord)
            logger.log_SRIF(target_id.coord, "to expr")
            # retrieve ast
            # binary_op.right = temp
            break
    return True


def defectify_SRIF_wrap_func_call(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    if "random_picker" in exp_spec_dict.keys():
        random_picker_spec = exp_spec_dict["random_picker"]
        random_picker = RandomPicker(random_picker_spec["random_int_list"], random_picker_spec["random_chr_list"])
    else:
        random_picker = RandomPicker(None, None)

    global_ids, global_funcs = parse_fileAST_exts(ast)
    id_name_map = {}
    for global_id in global_ids:
        id_name_map[global_id.name] = global_id.type.type.names[0]
    func = None
    count = 0
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    if func.decl.name != "main":
        print("Warning: Cannot wrap function call outside function main.")
        return False
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    target_id = random_pick_probless(ids)
    # 3. figure out the type of the chosen identifier
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        id_name_map[type_decl.declname] = type_decl.type.names[0]
    target_id_type = id_name_map[target_id.name]

    # 4. figure out the type of the chosen identifier
    # , and judge whether the chosen identifier can be wrapped or unwrapped with some functions
    wrappable_funcs = []
    for f in global_funcs:
        if f.decl.name != "main":
            params = f.decl.type.args.params
            params_type = [param.type.type.names[0] for param in params]
            ret_type = f.decl.type.type.type.names[0]
            if target_id_type == ret_type and target_id_type in params_type:
                wrappable_funcs.append(f)
    if len(wrappable_funcs) == 0:
        print("Warning: No wrappable function call found.")
        return False
    func_to_wrap = random_pick_probless(wrappable_funcs)
    binary_op_visitor = BinaryOpVisitor(node)
    binary_op_visitor.visit(node)
    binary_ops = binary_op_visitor.get_nodelist()
    func_call_id = c_ast.ID(name=func_to_wrap.decl.name)
    func_call_args = []
    func_def_params = func_to_wrap.decl.type.args.params
    for func_def_param in func_def_params:
        if func_def_param.type.type.names[0] == target_id_type:
            arg_item = random_pick_probless([c_ast.ID(name=target_id.name),
                                             c_ast.Constant(type=target_id_type,
                                                            value=str(random_picker.gen_random(target_id_type)))])
            func_call_args.append(arg_item)
        else:
            func_call_args.append(c_ast.Constant(type=func_def_param.type.type.names[0],
                                                 value=str(random_picker.gen_random(func_def_param.type.type.names[0]))))
    func_call = c_ast.FuncCall(name=func_call_id,
                               args=c_ast.ExprList(exprs=func_call_args),
                               coord=target_id.coord)
    # print(generator.visit(func_call))
    for binary_op in binary_ops:
        if binary_op.left == target_id:
            temp = target_id
            binary_op.left = func_call
            logger.log_SRIF(target_id.coord, "wrap func")
            # retrieve ast
            # binary_op.left = temp
            break
        elif binary_op.right == target_id:
            temp = target_id
            binary_op.right = func_call
            logger.log_SRIF(target_id.coord, "wrap func")
            # retrieve ast
            # binary_op.right = temp
            break
    return True


def defectify_SRIF_unwrap_func_call(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    print("testing SRIF...")
    # begin SRIF
    global_ids, global_funcs = parse_fileAST_exts(ast)
    id_name_map = {}
    for global_id in global_ids:
        id_name_map[global_id.name] = global_id.type.type.names[0]
    func = None
    count = 0
    # step 1: find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    ifVisitor = IfVisitor(func)
    ifVisitor.visit(func)
    nodes = ifVisitor.get_nodelist()
    if func.decl.name != "main":
        print("Warning: Cannot unwrap function call outside function main.")
        return False
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    target_id = random_pick_probless(ids)
    # 3. figure out the type of the chosen identifier
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        id_name_map[type_decl.declname] = type_decl.type.names[0]
    target_id_type = id_name_map[target_id.name]

    # 4. figure out the type of the chosen identifier
    # , and judge whether the chosen identifier can be wrapped or unwrapped with some functions
    wrappable_funcs = []
    for f in global_funcs:
        if f.decl.name != "main":
            params = f.decl.type.args.params
            params_type = [param.type.type.names[0] for param in params]
            ret_type = f.decl.type.type.type.names[0]
            if target_id_type == ret_type and target_id_type in params_type:
                wrappable_funcs.append(f)
    if len(wrappable_funcs) == 0:
        print("Warning: No unwrappable function call found.")
        return False
    else:
        wrappable_func_names = [wrappable_func.decl.name for wrappable_func in wrappable_funcs]
        func_call_visitor = FuncCallVisitor(func)
        func_call_visitor.visit(func)
        func_calls = func_call_visitor.get_nodelist()
        unwrappable_func_call = None
        for fc in func_calls:
            arg_list = fc.args.exprs
            if fc.name.name in wrappable_func_names and target_id in arg_list:
                unwrappable_func_call = fc
                break
        if unwrappable_func_call is None:
            print("Warning: No unwrappable function call found.")
            return False
    # unwrap_func_call(target_id, count, node, unwrappable_func_call)
    # unwrap_func_call(node_, count, root, func_call):
    binary_op_visitor = BinaryOpVisitor(node.cond)
    binary_op_visitor.visit(node.cond)
    binary_ops = binary_op_visitor.get_nodelist()
    for binary_op in binary_ops:
        if binary_op.left == unwrappable_func_call:
            temp = binary_op.left
            binary_op.left = c_ast.ID(name=target_id.name,
                                      coord=binary_op.left.coord)
            logger.log_SRIF(target_id.coord, "unwrap func")
            # retrieve ast
            # binary_op.left = temp
            break
        elif binary_op.right == unwrappable_func_call:
            temp = binary_op.right
            binary_op.right = c_ast.ID(name=target_id.name,
                                       coord=binary_op.left.coord)
            logger.log_SRIF(target_id.coord, "unwrap func")
            # retrieve ast
            # binary_op.right = temp
            break
    return False


def defectify_SRIF(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    SRIF_EQUAL_PROB = True
    if "SRIF" in exp_spec_dict.keys():
        srif_spec = exp_spec_dict["SRIF"]
        if len(srif_spec) != 0:
            SRIF_EQUAL_PROB = False
    if SRIF_EQUAL_PROB:
        func = globals()[random_pick_probless(["defectify_SRIF_replace_var",
                                               "defectify_SRIF_to_expr",
                                               "defectify_SRIF_wrap_func_call",
                                               "defectify_SRIF_unwrap_func_call"])]
    else:
        func = globals()["defectify_" + random_pick(list(srif_spec.keys()), list(srif_spec.values()))]
    return func(ast, task_name, logger, exp_spec_dict)


#
# def defectify_SDFN(ast, task_name, mode, logger, outer_count):
#     """
#
#     :param ast:
#     :param task_name:
#     :param mode:
#     :param logger:
#     :param outer_count:
#     :return:
#     """
#     available_func_calls = {}
#     case_visitor = CaseVisitor(ast, mode, task_name)
#     case_visitor.visit(ast)
#     case_nodes = case_visitor.get_nodelist()
#     for case_node in case_nodes:
#         for stmt in case_node.stmts:
#             if type(stmt) == c_ast.FuncCall:
#                 available_func_calls[case_node] = "case"
#                 break
#     compound_visitor = CompoundVisitor(ast, mode, task_name)
#     compound_visitor.visit(ast)
#     compound_nodes = compound_visitor.get_nodelist()
#     for compound_node in compound_nodes:
#         for block_item in compound_node.block_items:
#             if type(block_item) == c_ast.FuncCall:
#                 available_func_calls[compound_node] = "compound"
#                 break
#     default_visitor = DefaultVisitor(ast, mode, task_name)
#     default_visitor.visit(ast)
#     default_nodes = default_visitor.get_nodelist()
#     for default_node in default_nodes:
#         for stmt in default_node.stmts:
#             if type(stmt) == c_ast.FuncCall:
#                 available_func_calls[default_node] = "default"
#                 break
#     dowhile_visitor = DoWhileVisitor(ast, mode, task_name)
#     dowhile_visitor.visit(ast)
#     dowhile_nodes = dowhile_visitor.get_nodelist()
#     for dowhile_node in dowhile_nodes:
#         if type(dowhile_node.stmt) == c_ast.FuncCall:
#             available_func_calls[dowhile_node] = "dowhile"
#     for_visitor = ForVisitor(ast, mode, task_name)
#     for_visitor.visit(ast)
#     for_nodes = for_visitor.get_nodelist()
#     for for_node in for_nodes:
#         if type(for_node.stmt) == c_ast.FuncCall:
#             available_func_calls[for_node] = "for"
#     if_visitor = IfVisitor(ast, mode, task_name)
#     if_visitor.visit(ast)
#     if_nodes = if_visitor.get_nodelist()
#     for if_node in if_nodes:
#         available_func_calls[if_node] = ""
#         if type(if_node.iftrue) == c_ast.FuncCall:
#             available_func_calls[if_node] += "if.true"
#         if type(if_node.iffalse) == c_ast.FuncCall:
#             available_func_calls[if_node] += "if.false"
#     label_visitor = LabelVisitor(ast, mode, task_name)
#     label_visitor.visit(ast)
#     label_nodes = label_visitor.get_nodelist()
#     for label_node in label_nodes:
#         if type(label_node.stmt) == c_ast.FuncCall:
#             available_func_calls[label_node] = "label"
#     switch_visitor = SwitchVisitor(ast, mode, task_name)
#     switch_visitor.visit(ast)
#     switch_nodes = switch_visitor.get_nodelist()
#     for switch_node in switch_nodes:
#         if type(switch_node.stmt) == c_ast.FuncCall:
#             available_func_calls[switch_node] = "switch"
#     while_visitor = WhileVisitor(ast, mode, task_name)
#     while_visitor.visit(ast)
#     while_nodes = while_visitor.get_nodelist()
#     for while_node in while_nodes:
#         if type(while_node.stmt) == c_ast.FuncCall:
#             available_func_calls[while_node] = "while"
#     # filter some unavailable cases
#     available_func_calls = {key: value for key, value in available_func_calls.items() if value != ""}
#
#     if mode == "RANDOM":
#         target_node, target_node_type = random_pick(list(available_func_calls.items()), None)
#         if target_node_type == "case" or target_node_type == "default":
#             func_calls = []
#             for stmt in target_node.stmts:
#                 if type(stmt) == c_ast.FuncCall:
#                     func_calls.append(stmt)
#             func_call = random_pick(func_calls, None)
#             index = target_node.stmts.index(func_call)
#             target_node.stmts.remove(func_call)
#             if outer_count:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#             logger.log_SDFN(func_call.coord, target_node_type)
#             # retrieve ast
#             target_node.stmts.insert(index, func_call)
#         elif target_node_type == "compound":
#             func_calls = []
#             for block_item in target_node.block_items:
#                 if type(block_item) == c_ast.FuncCall:
#                     func_calls.append(block_item)
#             func_call = random_pick(func_calls, None)
#             index = target_node.block_items.index(func_call)
#             target_node.block_items.remove(func_call)
#             if outer_count:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#             logger.log_SDFN(func_call.coord, target_node_type)
#             # retrieve ast
#             target_node.block_items.insert(index, func_call)
#         elif target_node_type == "dowhile" or target_node_type == "for" or target_node_type == "label" or target_node_type == "switch" or target_node_type == "while":
#             func_call = target_node.stmt
#             target_node.stmt = c_ast.EmptyStatement(coord=func_call.coord)
#             if outer_count:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#             logger.log_SDFN(func_call.coord, target_node_type)
#             # retrieve ast
#             target_node.stmt = func_call
#         elif target_node_type == "if.true":
#             func_call = target_node.iftrue
#             target_node.iftrue = c_ast.EmptyStatement(coord=func_call.coord)
#             if outer_count:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#             logger.log_SDFN(func_call.coord, target_node_type)
#             # retrieve ast
#             target_node.iftrue = func_call
#
#         elif target_node_type == "if.false":
#             func_call = target_node.iffalse
#             target_node.iffalse = c_ast.EmptyStatement(coord=func_call.coord)
#             if outer_count:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#             logger.log_SDFN(func_call.coord, target_node_type)
#             # retrieve ast
#             target_node.iffalse = func_call
#         elif target_node_type == "if.trueif.false" or target_node_type == "if.falseif.true":
#             flag = random_pick([True, False], None)
#             if flag:
#                 func_call = target_node.iftrue
#                 target_node.iftrue = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.iftrue = func_call
#             else:
#                 func_call = target_node.iffalse
#                 target_node.iffalse = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, 0), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.iffalse = func_call
#         else:
#             print("Err: Type: " + target_node_type + " not declared.")
#     elif mode == "DEBUG":
#         count = 0
#         for target_node, target_node_type in available_func_calls.items():
#             if target_node_type == "case" or target_node_type == "default":
#                 func_calls = []
#                 for stmt in target_node.stmts:
#                     if type(stmt) == c_ast.FuncCall:
#                         func_calls.append(stmt)
#                 for func_call in func_calls:
#                     count += 1
#                     index = target_node.stmts.index(func_call)
#                     target_node.stmts.remove(func_call)
#                     if outer_count:
#                         generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                     else:
#                         generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                     logger.log_SDFN(func_call.coord, target_node_type)
#                     # retrieve ast
#                     target_node.stmts.insert(index, func_call)
#             elif target_node_type == "compound":
#                 func_calls = []
#                 for block_item in target_node.block_items:
#                     if type(block_item) == c_ast.FuncCall:
#                         func_calls.append(block_item)
#                 for func_call in func_calls:
#                     count += 1
#                     index = target_node.block_items.index(func_call)
#                     target_node.block_items.remove(func_call)
#                     if outer_count:
#                         generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                     else:
#                         generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                     logger.log_SDFN(func_call.coord, target_node_type)
#                     # retrieve ast
#                     target_node.block_items.insert(index, func_call)
#             elif target_node_type == "dowhile" or target_node_type == "for" or target_node_type == "label" or target_node_type == "switch" or target_node_type == "while":
#                 count += 1
#                 func_call = target_node.stmt
#                 target_node.stmt = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.stmt = func_call
#             elif target_node_type == "if.true":
#                 count += 1
#                 func_call = target_node.iftrue
#                 target_node.iftrue = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.iftrue = func_call
#
#             elif target_node_type == "if.false":
#                 count += 1
#                 func_call = target_node.iffalse
#                 target_node.iffalse = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.iffalse = func_call
#             elif target_node_type == "if.trueif.false" or target_node_type == "if.falseif.true":
#                 count += 1
#                 func_call = target_node.iftrue
#                 target_node.iftrue = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.iftrue = func_call
#                 count += 1
#                 func_call = target_node.iffalse
#                 target_node.iffalse = c_ast.EmptyStatement(coord=func_call.coord)
#                 if outer_count:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_SDFN_{}_{}.c".format(target_node_type, count), task_name, ast)
#                 logger.log_SDFN(func_call.coord, target_node_type)
#                 # retrieve ast
#                 target_node.iffalse = func_call
#             else:
#                 print("Err: Type: " + target_node_type + " not declared.")
#
#
# def defectify_OAIS(ast, task_name, mode, logger, outer_count):
#     """
#     OAIS is just like to_expr in SRIF, but different in sequence-flow
#     :param ast:
#     :param task_name:
#     :param mode:
#     :param logger:
#     :param outer_count:
#     :return:
#     """
#     global_ids, global_funcs = parse_fileAST_exts(ast)
#     id_name_map = {}
#     for global_id in global_ids:
#         id_name_map[global_id.name] = global_id.type.type.names[0]
#     if mode == "RANDOM":
#         func = random_pick(global_funcs, None)
#         type_decl_visitor = TypeDeclVisitor(func, mode, task_name)
#         type_decl_visitor.visit(func)
#         type_decls = type_decl_visitor.get_nodelist()
#         for type_decl in type_decls:
#             id_name_map[type_decl.declname] = type_decl.type.names[0]
#         binary_visitor = BinaryOpVisitor(func, mode, task_name)
#         binary_visitor.visit(func)
#         available_nodes = []
#         binary_ops = binary_visitor.get_nodelist()
#         for binary_op in binary_ops:
#             if binary_op.op in c_arithmetic_binary_operator_set:
#                 if type(binary_op.left) == c_ast.ID or type(binary_op.right) == c_ast.ID:
#                     available_nodes.append(binary_op)
#         target_node = random_pick(available_nodes, None)
#         if type(target_node.left) == c_ast.ID:
#             temp = target_node.left
#             id_type = id_name_map[temp.name]
#             if id_type == "int" or id_type == "short" or id_type == "long":
#                 right_const = c_ast.Constant(type=id_type,
#                                              value=str(gen_random(id_type)))
#                 target_node.left = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/', '%'], None),
#                                                   left=temp,
#                                                   right=right_const,
#                                                   coord=temp.coord)
#             elif id_type == "char":
#                 print("Err: OAIS not fit for char values.")
#                 return
#             else:
#                 right_const = c_ast.Constant(type=id_type,
#                                              value=str(gen_random(id_type)))
#                 target_node.left = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/'], None),
#                                                   left=temp,
#                                                   right=right_const,
#                                                   coord=temp.coord)
#             if outer_count:
#                 generate_exp_output("test_OAIS_left_{}.c".format(outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_OAIS_left_{}.c".format(0), task_name, ast)
#             logger.log_OAIS(target_node.coord)
#             # retrieve ast
#             target_node.left = temp
#
#         if type(target_node.right) == c_ast.ID:
#             temp = target_node.right
#             id_type = id_name_map[temp.name]
#             if id_type == "int" or id_type == "short" or id_type == "long":
#                 right_const = c_ast.Constant(type=id_type,
#                                              value=str(gen_random(id_type)))
#                 target_node.right = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/', '%'], None),
#                                                    left=temp,
#                                                    right=right_const,
#                                                    coord=temp.coord)
#             elif id_type == "char":
#                 print("Err: OAIS not fit for char values.")
#                 return
#             else:
#                 right_const = c_ast.Constant(type=id_type,
#                                              value=str(gen_random(id_type)))
#                 target_node.right = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/'], None),
#                                                    left=temp,
#                                                    right=right_const,
#                                                    coord=temp.coord)
#             if outer_count:
#                 generate_exp_output("test_OAIS_right_{}.c".format(outer_count), task_name, ast)
#             else:
#                 generate_exp_output("test_OAIS_right_{}.c".format(0), task_name, ast)
#             logger.log_OAIS(target_node.coord)
#             # retrieve ast
#             target_node.right = temp
#
#     elif mode == "DEBUG":
#         for func in global_funcs:
#             temp_id_map = id_name_map
#             type_decl_visitor = TypeDeclVisitor(func, mode, task_name)
#             type_decl_visitor.visit(func)
#             type_decls = type_decl_visitor.get_nodelist()
#             for type_decl in type_decls:
#                 temp_id_map[type_decl.declname] = type_decl.type.names[0]
#             binary_visitor = BinaryOpVisitor(func, mode, task_name)
#             binary_visitor.visit(func)
#             available_nodes = []
#             binary_ops = binary_visitor.get_nodelist()
#             for binary_op in binary_ops:
#                 if binary_op.op in c_arithmetic_binary_operator_set:
#                     if type(binary_op.left) == c_ast.ID or type(binary_op.right) == c_ast.ID:
#                         available_nodes.append(binary_op)
#             for target_node in available_nodes:
#                 if type(target_node.left) == c_ast.ID:
#                     temp = target_node.left
#                     id_type = id_name_map[temp.name]
#                     if id_type == "int" or id_type == "short" or id_type == "long":
#                         right_const = c_ast.Constant(type=id_type,
#                                                      value=str(gen_random(id_type)))
#                         target_node.left = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/', '%'], None),
#                                                           left=temp,
#                                                           right=right_const,
#                                                           coord=temp.coord)
#                     elif id_type == "char":
#                         print("Err: OAIS not fit for char values.")
#                         return
#                     else:
#                         right_const = c_ast.Constant(type=id_type,
#                                                      value=str(gen_random(id_type)))
#                         target_node.left = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/'], None),
#                                                           left=temp,
#                                                           right=right_const,
#                                                           coord=temp.coord)
#                     if outer_count:
#                         generate_exp_output("test_OAIS_left_{}.c".format(outer_count), task_name, ast)
#                     else:
#                         generate_exp_output("test_OAIS_left_{}.c".format(0), task_name, ast)
#                     logger.log_OAIS(target_node.coord)
#                     # retrieve ast
#                     target_node.left = temp
#
#                 if type(target_node.right) == c_ast.ID:
#                     temp = target_node.right
#                     id_type = id_name_map[temp.name]
#                     if id_type == "int" or id_type == "short" or id_type == "long":
#                         right_const = c_ast.Constant(type=id_type,
#                                                      value=str(gen_random(id_type)))
#                         target_node.right = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/', '%'], None),
#                                                            left=temp,
#                                                            right=right_const,
#                                                            coord=temp.coord)
#                     elif id_type == "char":
#                         print("Err: OAIS not fit for char values.")
#                         return
#                     else:
#                         right_const = c_ast.Constant(type=id_type,
#                                                      value=str(gen_random(id_type)))
#                         target_node.right = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/'], None),
#                                                            left=temp,
#                                                            right=right_const,
#                                                            coord=temp.coord)
#                     if outer_count:
#                         generate_exp_output("test_OAIS_right_{}.c".format(outer_count), task_name, ast)
#                     else:
#                         generate_exp_output("test_OAIS_right_{}.c".format(0), task_name, ast)
#                     logger.log_OAIS(target_node.coord)
#                     # retrieve ast
#                     target_node.right = temp
#
#
# def defectify_STYP(ast, task_name, mode, logger, outer_count):
#     """
#
#     :param ast:
#     :param task_name:
#     :param mode:
#     :param logger:
#     :param outer_count:
#     :return:
#     """
#     global_ids, global_funcs = parse_fileAST_exts(ast)
#     global_func_names = [item.decl.name for item in global_funcs]
#     decl_visitor = DeclVisitor(ast, mode, task_name)
#     decl_visitor.visit(ast)
#     decls = decl_visitor.get_nodelist()
#     var_decls = [item for item in decls if item.name not in global_func_names]
#     int_family = ["short", "int", "long"]
#     char_family = ["char"]
#     float_family = ["float", "double"]
#     if mode == "RANDOM":
#         var_decl = random_pick(var_decls, None)
#         type_name = var_decl.type.type.names[0]
#         if type_name in int_family:
#             int_family.remove(type_name)
#             replace_type = random_pick(int_family, None)
#         elif type_name in char_family:
#             replace_type = "int"
#         elif type_name in float_family:
#             float_family.remove(type_name)
#             replace_type = random_pick(float_family, None)
#         else:
#             print("Err: Current Type cannot be replaced")
#         temp = var_decl.type.type.names[0]
#         var_decl.type.type = c_ast.IdentifierType(names=[replace_type])
#         if outer_count:
#             generate_exp_output("test_STYP_{}.c".format(outer_count), task_name, ast)
#         else:
#             generate_exp_output("test_STYP_{}.c".format(0), task_name, ast)
#         logger.log_STYP(var_decl.coord, temp, replace_type)
#         # retrieve ast
#         var_decl.type.type = c_ast.IdentifierType(names=[temp])
#     elif mode == "DEBUG":
#         for var_decl in var_decls:
#             type_name = var_decl.type.type.names[0]
#             if type_name in int_family:
#                 int_family.remove(type_name)
#                 replace_types = int_family
#             elif type_name in char_family:
#                 replace_types = ["int"]
#             elif type_name in float_family:
#                 float_family.remove(type_name)
#                 replace_types = float_family
#             else:
#                 print("Err: Current Type cannot be replaced")
#             for replace_type in replace_types:
#                 temp = var_decl.type.type.names[0]
#                 var_decl.type.type = c_ast.IdentifierType(names=[replace_type])
#                 if outer_count:
#                     generate_exp_output("test_STYP_{}.c".format(outer_count), task_name, ast)
#                 else:
#                     generate_exp_output("test_STYP_{}.c".format(0), task_name, ast)
#                 logger.log_STYP(var_decl.coord, temp, replace_type)
#                 # retrieve ast
#                 var_decl.type.type = c_ast.IdentifierType(names=[temp])
#
#
# def defectify_SMOV(ast, task_name, mode, logger, outer_count):
#     """
#
#     :param ast:
#     :param task_name:
#     :param mode:
#     :param logger:
#     :param outer_count:
#     :return:
#     """
#     available_stmts = []
#     case_visitor = CaseVisitor(ast, mode, task_name)
#     case_visitor.visit(ast)
#     case_nodes = case_visitor.get_nodelist()
#     for case_node in case_nodes:
#         case_node.stmts = list(filter(lambda x: type(x) != c_ast.Decl, case_node.stmts))
#         if len(case_node.stmts) > 1:
#             available_stmts.append(case_node.stmts)
#     compound_visitor = CompoundVisitor(ast, mode, task_name)
#     compound_visitor.visit(ast)
#     compound_nodes = compound_visitor.get_nodelist()
#     for compound_node in compound_nodes:
#         compound_node.block_items = list(filter(lambda x: type(x) != c_ast.Decl, compound_node.block_items))
#         if len(compound_node.block_items) > 1:
#             available_stmts.append(compound_node.block_items)
#     default_visitor = DefaultVisitor(ast, mode, task_name)
#     default_visitor.visit(ast)
#     default_nodes = default_visitor.get_nodelist()
#     for default_node in default_nodes:
#         default_node.stmts = list(filter(lambda x: type(x) != c_ast.Decl, default_node.stmts))
#         if len(default_node.stmts) > 1:
#             available_stmts.append(default_node.stmts)
#     if mode == "RANDOM":
#         target_stmts = random_pick(available_stmts, None)
#         length = len(target_stmts)
#         distance = random_pick(range(1, length), None)
#         stmt_1 = random_pick(target_stmts, None)
#         index_1 = target_stmts.index(stmt_1)
#         index_2 = (index_1 + distance) % length
#         temp = target_stmts[index_1]
#         target_stmts[index_1] = target_stmts[index_2]
#         target_stmts[index_2] = temp
#         if outer_count:
#             generate_exp_output("test_SMOV_{}.c".format(outer_count), task_name, ast)
#         else:
#             generate_exp_output("test_SMOV_{}.c".format(0), task_name, ast)
#         logger.log_SMOV(target_stmts[index_1].coord, target_stmts[index_2].coord)
#         # retrieve ast
#         temp = target_stmts[index_1]
#         target_stmts[index_1] = target_stmts[index_2]
#         target_stmts[index_2] = temp
#
#     elif mode == "DEBUG":
#         # maybe not feasible for listing all cases
#         pass
#
#
# def defectify_OFPO(ast, task_name, mode, logger, outer_count):
#     """
#
#     :param ast:
#     :param task_name:
#     :param mode:
#     :param logger:
#     :param outer_count:
#     :return:
#     """
#     global_ids, global_funcs = parse_fileAST_exts(ast)
#     available_funcs = []
#     funcs_param_type_map = {}
#     for global_func in global_funcs:
#         params = global_func.decl.type.args.params
#         param_type_map = {}
#         for param in params:
#             param_type = param.type.type
#             if type(param_type) == c_ast.IdentifierType:
#                 param_type_name = param_type.names[0]
#             elif type(param_type) == c_ast.PtrDecl:
#                 param_type_name = param_type.type.type.names[0] + "*"
#             if param_type_name in param_type_map.keys():
#                 param_type_map[param_type_name].append(params.index(param))
#             else:
#                 param_type_map[param_type_name] = [params.index(param)]
#         for index_list in param_type_map.values():
#             if len(index_list) > 1:
#                 available_funcs.append(global_func)
#                 funcs_param_type_map[global_func.decl.name] = param_type_map
#                 break
#     func_call_visitor = FuncCallVisitor(ast, mode, task_name)
#     func_call_visitor.visit(ast)
#     func_calls = func_call_visitor.get_nodelist()
#     available_func_names = [func.decl.name for func in available_funcs]
#     available_func_calls = [func_call for func_call in func_calls if func_call.name.name in available_func_names]
#     if mode == "RANDOM":
#         target_func_call = random_pick(available_func_calls, None)
#         target_param_type_map = funcs_param_type_map[target_func_call.name.name]
#         available_param_index = {key: value for key, value in target_param_type_map.items() if len(value) > 1}
#         target_key = random_pick(list(available_param_index.keys()), None)
#         target_param_index = available_param_index[target_key]
#         length = len(target_param_index)
#         index_1 = target_param_index.index(random_pick(target_param_index, None))
#         distance = random_pick(range(1, length), None)
#         index_2 = (index_1 + distance) % length
#         index_1 = target_param_index[index_1]
#         index_2 = target_param_index[index_2]
#         target_arg = target_func_call.args.exprs
#         temp = target_arg[index_1]
#         target_arg[index_1] = target_arg[index_2]
#         target_arg[index_2] = temp
#         if outer_count:
#             generate_exp_output("test_OFPO_{}.c".format(outer_count), task_name, ast)
#         else:
#             generate_exp_output("test_OFPO_{}.c".format(0), task_name, ast)
#         logger.log_OFPO(target_func_call.coord, index_1, index_2)
#         # retrieve ast
#         temp = target_arg[index_1]
#         target_arg[index_1] = target_arg[index_2]
#         target_arg[index_2] = temp
#     elif mode == "DEBUG":
#         pass
#         # not feasible for listing all cases in current circumstances



def defectify_test(ast, task_name, logger, exp_spec_dict):
    """
    test
    :param ast:
    :param task_name:
    :param mode:
    :param logger:
    :param outer_count:
    :return:
    """
    print("testing OILN")


def defectify(ast, task_name, defectify_type, logger, exp_spec_dict):
    """
    generic defectify entry
    :param ast:                 ast structure
    :param task_name:           experiment name
    :param defectify_type:      what kind of defect to introduce
    :param logger:              a Logger instance
    :param exp_spec_dict:       the specification dictionary of current experiment(task)
    :return:
    """
    method_name = "defectify_" + defectify_type
    try:
        func = globals()[method_name]
    except KeyError:
        print("Err: function {} has not been registered in ./defect/defectify".format(method_name))
        return
    return func(ast, task_name, logger, exp_spec_dict)
