from visitors.ArrayDeclVisitor import ArrayDeclVisitor
from visitors.AssignmentVisitor import AssignmentVisitor
from visitors.BinaryOpVisitor import BinaryOpVisitor
from visitors.ConditionVisitor import ConditionVisitor
from visitors.CompoundVisitor import CompoundVisitor
from visitors.DaddyVisitor import DaddyVisitor
from visitors.DeclVisitor import DeclVisitor
from visitors.FuncCallVisitor import FuncCallVisitor
from visitors.IDVisitor import IDVisitor
from visitors.OpVisitor import OpVisitor
from visitors.StatementsVisitor import StatementsVisitor
from visitors.StatementVisitor import StatementVisitor
from visitors.TypeDeclVisitor import TypeDeclVisitor
from utils.random_picker import random_pick, random_pick_probless, RandomPicker, get_randint
from utils.ast_util import parse_fileAST_exts
from pycparser import c_ast, c_generator

import re

c_relational_binary_operator_set = {'>', '<', '>=', '<=', '==', '!='}
c_arithmetic_binary_operator_set = {'+', '-', '*', '/', '%'}
generator = c_generator.CGenerator()


def defectify_ORRN(ast, task_name, logger, exp_spec_dict):
    """
    {
        available_nodes <- visit_nodes_with_condition(root)
        node <- random_pick(available_nodes)
        replace_ops <- {all_relation_operators} - node.operator
        replace_op <- random_pick(replace_ops)
        node.operator <- replace_op
    }
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
    available_node_list = [node for node in nodelist if type(node.cond) == c_ast.BinaryOp and node.cond.op in c_relational_binary_operator_set]
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
    line_code = generator.visit(node).split("\n")[0]
    node.cond.op = replace_op
    # create log
    logger.log_ORRN(node.coord, current_op, replace_op)
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "ORRN",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "op": current_op,
        "op_replace": replace_op
    }
    return annotation


def defectify_OILN_add_and(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        identifiers <- visit_identifiers(if_node.condition)
        identifier <- random_pick(identifiers)
        identifier_type <- typeof(identifier)
        new_node <- BinaryOp{
            op <- random_pick({relation operators})
            left <- identifier
            right <- get_random_value_by_type(identifier_type)
        }
        add_left <- random_pick(True, False)
        if add_left:
            ast.add(if_node.left, new_node, op=&&)
        else:
            ast.add(if_node.right, new_node, op=&&)
    }
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
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No condition can be found")
        return False
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
        if type(type_decl) == c_ast.Decl:
            type_decl = type_decl.type
        if type(type_decl) in {c_ast.ArrayDecl, c_ast.Struct, c_ast.PtrDecl, c_ast.FuncDecl}:
            continue
        if type(type_decl.type) in {c_ast.Struct}:
            continue
        if id == type_decl.declname:
            # this may not be true, do not know why here <type names> is a list of names yet
            id_type = type_decl.type.names[0]
            break
    if id_type == "NOT_DECLARED":
        print("Err: Identifier not declared.")
        return False
    line_code = generator.visit(node).split("\n")[0]
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

    if node.cond.coord:
        logger.log_OILN(node.cond.coord, "add_and")
    else:
        logger.log_OILN(node.coord, "add_and")
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "OILN_add_and",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "cond_add": generator.visit(cond_add)
    }
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
    return annotation


def defectify_OILN_add_or(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        identifiers <- visit_identifiers(if_node.condition)
        identifier <- random_pick(identifiers)
        identifier_type <- typeof(identifier)
        new_node <- BinaryOp{
            op <- random_pick({relation operators})
            left <- identifier
            right <- get_random_value_by_type(identifier_type)
        }
        add_left <- random_pick(True, False)
        if add_left:
            ast.add(if_node.left, new_node, op=||)
        else:
            ast.add(if_node.right, new_node, op=||)
    }
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
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No condition can be found")
        return False
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
        if type(type_decl) == c_ast.Decl:
            type_decl = type_decl.type
        if type(type_decl) in {c_ast.ArrayDecl, c_ast.Struct, c_ast.PtrDecl, c_ast.FuncDecl}:
            continue
        if type(type_decl.type) in {c_ast.Struct}:
            continue
        if id == type_decl.declname:
            # this may not be true, do not know why here <type names> is a list of names yet
            id_type = type_decl.type.names[0]
            break
    if id_type == "NOT_DECLARED":
        print("Err: Identifier not declared.")
        return False
    line_code = generator.visit(node).split("\n")[0]
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

    if node.cond.coord:
        logger.log_OILN(node.cond.coord, "add_or")
    else:
        logger.log_OILN(node.coord, "add_or")
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "OILN_add_or",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "cond_add": generator.visit(cond_add)
    }
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
    return annotation


def defectify_OILN_del_and(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        delete_left <- random_pick(True, False)
        if delete_left:
            ast.delete(if_node.left)
        else:
            ast.delete(if_node.right)
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No condition can be found")
        return False
    if type(node.cond) != c_ast.BinaryOp:
        print("Warning: no binary operation can be found, no && can be deleted.")
        return False
    if node.cond.op != "&&":
        print("Warning: no && can be deleted.")
        return False
    line_code = generator.visit(node).split("\n")[0]
    # 3. save previous conditions
    temp = node.cond
    del_left = random_pick_probless([True, False])
    try:
        if del_left:
            cond_del = node.cond.left
            node.cond = node.cond.right

        else:
            cond_del = node.cond.right
            node.cond = node.cond.left
    except:
        return False
    logger.log_OILN(node.coord, "del_and")
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "OILN_del_and",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "cond_del": generator.visit(cond_del)
    }
    # *4. retrieve previous conditions
    # cond = temp
    return annotation


def defectify_OILN_del_or(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        delete_left <- random_pick(True, False)
        if delete_left:
            ast.delete(if_node.left)
        else:
            ast.delete(if_node.right)
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No condition can be found")
        return False
    if type(node.cond) != c_ast.BinaryOp:
        print("Warning: no binary operation can be found, no || can be deleted.")
        return False
    if node.cond.op != "||":
        print("Warning: no || can be deleted.")
        return False
    line_code = generator.visit(node).split("\n")[0]
    # 3. save previous conditions
    temp = node.cond
    del_left = random_pick_probless([True, False])
    try:
        if del_left:
            cond_del = node.cond.left
            node.cond = node.cond.right

        else:
            cond_del = node.cond.right
            node.cond = node.cond.left
    except:
        return False
    logger.log_OILN(node.coord, "del_or")
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "OILN_del_or",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "cond_del": generator.visit(cond_del)
    }
    # *4. retrieve previous conditions
    # cond = temp
    return annotation


def defectify_OILN_negate_cond(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        if if_node.condition.left is UnaryOp(!):
            if_node.condition.left <- UnaryOp(!).get_expression(if_node.condition.left)
        else:
            if_node.condition.left <- UnaryOp(!).set_expression(if_node.condition.left)
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. randomly pick one if node from current function scope
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No condition can be found")
        return False
    if type(node.cond) != c_ast.BinaryOp:
        print("Warning: no binary operation can be found, no || can be deleted.")
        return False
    line_code = generator.visit(node).split("\n")[0]
    if type(node.cond.left) == c_ast.UnaryOp and node.cond.left.op == '!':
        # find a ! expression
        # save current part of ast
        temp = c_ast.UnaryOp(op='!',
                             expr=node.cond.left.expr,
                             coord=node.cond.left.coord)
        node.cond.left = node.cond.left.expr
        if node.cond.left.coord:
            logger.log_OILN(node.cond.left.coord, "denegate")
        else:
            logger.log_OILN(node.cond.coord, "denegate")
        # retrieve ast
        # node.cond.left = temp
    else:
        node.cond.left = c_ast.UnaryOp(op='!',
                                       expr=node.cond.left,
                                       coord=node.cond.left.coord)
        if node.cond.left.coord:
            logger.log_OILN(node.cond.left.coord, "negate")
        else:
            logger.log_OILN(node.coord, "negate")
        # retrieve ast
        # node.cond.left = node.cond.left.expr
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "OILN_negate_cond",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
    }
    return annotation


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
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        identifiers <- visit_identifiers(if_node) + global_identifiers
        target_identifier <- random_pick(identifiers)
        identifiers_remain <- identifiers.remove(target_identifier)
        filter(element.type == target_identifier.type, identifiers_remain)
        matched_identifier <- random_pick(identifiers_remain)
        target_identifier.name <- matched_identifier.name
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    id_name_map = {}
    for global_id in global_ids:
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}\
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No node condition can be found")
        return False
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
    if target_id is None:
        print("No Target ID Found")
        return False
    ids_remain = id_name_set - {target_id.name}
    global_ids_name = [item.name for item in global_ids]
    ids_remain = ids_remain.union(set(global_ids_name) - {target_id.name})
    # 3. figure out the type of the chosen identifier
    #  , and judge whether the chosen identifier can be replaced or be converted to expression
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False
    matched_ids = []
    for id_remain in ids_remain:
        if id_remain in id_name_map.keys() and id_name_map[id_remain] == target_id_type:
            matched_ids.append(id_remain)
    if len(matched_ids) == 0:
        print("Warning: no replacement found.")
        return False
    line_code = generator.visit(node).split("\n")[0]
    # 4. randomly pick one matched identifier
    matched_id = random_pick_probless(matched_ids)
    temp = target_id.name
    target_id.name = matched_id
    logger.log_SRIF(node.coord, "replace var")
    line_code_def = generator.visit(node).split("\n")[0]
    annotation = {
        "class": "SRIF_replace_var",
        "line_num": node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "var": temp,
        "replace_var": target_id.name
    }
    # retrieve ast
    # target_id.name = temp
    return annotation


def defectify_SRIF_to_expr(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        identifiers <- visit_identifiers(if_node) + global_identifiers
        target_identifier <- random_pick(identifiers)
        binary_ops <- visit_binary_operations(if_node)
        new_node <- BinaryOp{
            op <- random_pick({arithmetic operators})
            left <- target_identifier
            right <- get_random_value_by_type(target_identifier.type)
        }
        for binary_op in binary_ops:
            if binary_op.left == target_identifier:
                binary_op.left <- new_node
                break
            if binary_op.right == target_identifier:
                binary_op.right <- new_node
                break
    }
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No node condition can be found")
        return False
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    target_id = random_pick_probless(ids)
    if target_id is None:
        print("No Target ID Found")
        return False
    # 3. figure out the type of the chosen identifier
    # , and judge whether the chosen identifier can be converted to expression
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False

    if target_id_type == "char":
        print("Warning: cannot convert to expression.")
        return False
    line_code = generator.visit(node).split("\n")[0]
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
    annotation = False
    for binary_op in binary_ops:
        if binary_op.left == target_id:
            temp = target_id
            binary_op.left = c_ast.BinaryOp(op=op,
                                            left=target_id,
                                            right=value_const,
                                            coord=target_id.coord)
            if target_id.coord:
                logger.log_SRIF(target_id.coord, "to expr")
            else:
                logger.log_SRIF(node.coord, "to expr")
            line_code_def = generator.visit(node).split("\n")[0]
            annotation = {
                "class": "SRIF_to_expr",
                "line_num": node.coord.line,
                "line_code": line_code,
                "line_code_def": line_code_def,
                "var": temp.name,
                "replace_expression": generator.visit(binary_op.left)
            }
            # retrieve ast
            # binary_op.left = temp
            break
        elif binary_op.right == target_id:
            temp = target_id
            binary_op.right = c_ast.BinaryOp(op=op,
                                             left=target_id,
                                             right=value_const,
                                             coord=target_id.coord)
            if target_id.coord:
                logger.log_SRIF(target_id.coord, "to expr")
            else:
                logger.log_SRIF(node.coord, "to expr")
            line_code_def = generator.visit(node).split("\n")[0]
            annotation = {
                "class": "SRIF_to_expr",
                "line_num": node.coord.line,
                "line_code": line_code,
                "line_code_def": line_code_def,
                "var": temp.name,
                "replace_expression": generator.visit(binary_op.right)
            }
            # retrieve ast
            # binary_op.right = temp
            break

    return annotation


def defectify_SRIF_wrap_func_call(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        identifiers <- visit_identifiers(if_node) + global_identifiers
        target_identifier <- random_pick(identifiers)
        wrappable_functions = filter(target_identifier.type in element.params.types()
            and target_identifier.type == element.return_type, global_functions)
        func_to_wrap = random_pick(wrappable_functions)
        for param_item in func_to_wrap.params():
            if param_item.type == target_identifier.type:
                new_param.append(random_pick(target_identifier, get_random_value_by_type(target_identifier.type)))
            else:
                new_param.append(get_random_value_by_type(param_item.type))

        binary_ops <- visit_binary_operations(if_node)
        new_node <- FuncCall(func_to_wrap, param=new_param)
        for binary_op in binary_ops:
            if binary_op.left == target_identifier:
                binary_op.left <- new_node
                break
            if binary_op.right == target_identifier:
                binary_op.right <- new_node
                break
    }
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # 1. find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False
    if func.decl.name != "main":
        print("Warning: Cannot wrap function call outside function main.")
        return False
    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    if node.cond is None:
        print("No node condition can be found")
        return False
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    target_id = random_pick_probless(ids)
    if target_id is None:
        print("No target id found")
        return False
    # 3. figure out the type of the chosen identifier
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False

    # 4. figure out the type of the chosen identifier
    # , and judge whether the chosen identifier can be wrapped or unwrapped with some functions
    wrappable_funcs = []
    for f in global_funcs:
        if f.decl.name != "main":
            if f.decl.type.args is None:
                continue
            params = f.decl.type.args.params
            params_type = []
            param_success = True
            for param in params:
                if type(param.type) in {c_ast.TypeDecl}:
                    if type(param.type.type) in {c_ast.Struct}:
                        param_success = False
                        break
                    params_type.append(param.type.type.names[0])
                elif type(param.type) in {c_ast.ArrayDecl, c_ast.Struct, c_ast.PtrDecl}:
                    param_success = False
                    break
                else:
                    params_type.append(param.type.type.type.names[0])
            if not param_success:
                continue
            if type(f.decl.type.type) in {c_ast.PtrDecl}:
                continue
            if type(f.decl.type.type.type) in {c_ast.Struct}:
                continue
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
        if type(func_def_param.type) in {c_ast.ArrayDecl, c_ast.PtrDecl}:
            print("Wrapping function with arrays or pointers as parameters is not supported.")
            return False
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
    line_code = generator.visit(node).split("\n")[0]
    annotation = False
    for binary_op in binary_ops:
        if binary_op.left == target_id:
            temp = target_id
            binary_op.left = func_call
            logger.log_SRIF(target_id.coord, "wrap func")
            line_code_def = generator.visit(node).split("\n")[0]
            annotation = {
                "class": "SRIF_wrap_func_call",
                "line_num": node.coord.line,
                "line_code": line_code,
                "line_code_def": line_code_def,
                "var": temp.name,
                "replace_func_call": generator.visit(binary_op.left)
            }
            # retrieve ast
            # binary_op.left = temp
            break
        elif binary_op.right == target_id:
            temp = target_id
            binary_op.right = func_call
            logger.log_SRIF(target_id.coord, "wrap func")
            line_code_def = generator.visit(node).split("\n")[0]
            annotation = {
                "class": "SRIF_wrap_func_call",
                "line_num": node.coord.line,
                "line_code": line_code,
                "line_code_def": line_code_def,
                "var": temp.name,
                "replace_func_call": generator.visit(binary_op.right)
            }
            # retrieve ast
            # binary_op.right = temp
            break
    return annotation


def defectify_SRIF_unwrap_func_call(ast, task_name, logger, exp_spec_dict):
    """
    {
        func <- random_pick(global_functions)
        if_nodes <- visit_if_nodes(func)
        if_node <- random_pick(if_nodes)
        identifiers <- visit_identifiers(if_node) + global_identifiers
        target_identifier <- random_pick(identifiers)
        wrappable_functions = filter(target_identifier.type in element.params.types()
            and target_identifier.type == element.return_type, global_functions)
        function_calls <- visit_function_calls(func)
        for function_call in function_calls:
            if function_call is wrappable and target_identifier in function_call.params():
                unwrappable_function_call <- function_call
                break
        binary_ops <- visit_binary_operations(if_node)
        new_node <- ID(target_identifier)
        for binary_op in binary_ops:
            if binary_op.left == unwrappable_function_call:
                binary_op.left <- new_node
                break
            if binary_op.right == unwrappable_function_call:
                binary_op.right <- new_node
                break
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    # begin SRIF
    global_ids, global_funcs = parse_fileAST_exts(ast)
    id_name_map = {}
    for global_id in global_ids:
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # step 1: find all the if-nodes from current function
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    # if func.decl.name != "main":
    #     print("Warning: Cannot unwrap function call outside function main.")
    #     return False

    condition_visitor = ConditionVisitor(func)
    condition_visitor.generic_visit(func)
    nodes = condition_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No condition node can be found")
        return False

    # 2. choose one if-node and find out all the identifiers from its condition
    node = random_pick_probless(nodes)
    if node is None:
        print("No node condition can be found")
        return False
    if node.cond is None:
        print("No condition node can be found")
        return False
    id_visitor = IDVisitor(node.cond)
    id_visitor.visit(node.cond)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    target_id = random_pick_probless(ids)
    if target_id is None:
        print("No target id found")
        return False
    # 3. figure out the type of the chosen identifier
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False

    # 4. figure out the type of the chosen identifier
    # , and judge whether the chosen identifier can be wrapped or unwrapped with some functions

    wrappable_funcs = []
    for f in global_funcs:
        if f.decl.name != "main":
            if f.decl.type.args is None:
                continue
            params = f.decl.type.args.params
            params_type = []
            param_success = True
            for param in params:
                if type(param.type) in {c_ast.TypeDecl}:
                    if type(param.type.type) in {c_ast.Struct}:
                        param_success = False
                        break
                    params_type.append(param.type.type.names[0])
                elif type(param.type) in {c_ast.ArrayDecl, c_ast.Struct, c_ast.PtrDecl}:
                    param_success = False
                    break
                else:
                    params_type.append(param.type.type.type.names[0])
            if not param_success:
                continue
            if type(f.decl.type.type) in {c_ast.PtrDecl}:
                continue
            if type(f.decl.type.type.type) in {c_ast.Struct}:
                continue
            ret_type = f.decl.type.type.type.names[0]
            if target_id_type == ret_type and target_id_type in params_type:
                wrappable_funcs.append(f)

    if len(wrappable_funcs) == 0:
        # print("Warning: No unwrappable function call found.")
        return False
    else:
        wrappable_func_names = [wrappable_func.decl.name for wrappable_func in wrappable_funcs]
        func_call_visitor = FuncCallVisitor(func)
        func_call_visitor.visit(func)
        func_calls = func_call_visitor.get_nodelist()
        if len(func_calls) == 0:
            print("No function call found.")
            return False
        unwrappable_func_call = None
        for fc in func_calls:
            if fc.args is None:
                continue
            arg_list = fc.args.exprs
            if fc.name.name in wrappable_func_names and target_id in arg_list:
                unwrappable_func_call = fc
                break
        if unwrappable_func_call is None:
            # print("Warning: No unwrappable function call found.")
            return False
        else:
            line_code = generator.visit(node).split("\n")[0]
            annotation = False
            binary_op_visitor = BinaryOpVisitor(node.cond)
            binary_op_visitor.visit(node.cond)
            binary_ops = binary_op_visitor.get_nodelist()
            for binary_op in binary_ops:
                if binary_op.left == unwrappable_func_call:
                    temp = binary_op.left
                    binary_op.left = c_ast.ID(name=target_id.name,
                                              coord=binary_op.left.coord)
                    if target_id.coord:
                        logger.log_SRIF(target_id.coord, "unwrap func")
                    else:
                        logger.log_SRIF(node.coord, "unwrap func")
                    line_code_def = generator.visit(node).split("\n")[0]
                    annotation = {
                        "class": "SRIF_unwrap_func_call",
                        "line_num": node.coord.line,
                        "line_code": line_code,
                        "line_code_def": line_code_def,
                        "func_call_to_unwrap": generator.visit(temp),
                        "replacement": generator.visit(binary_op.left)
                    }
                    # retrieve ast
                    # binary_op.left = temp
                    break
                elif binary_op.right == unwrappable_func_call:
                    temp = binary_op.right
                    binary_op.right = c_ast.ID(name=target_id.name,
                                               coord=binary_op.left.coord)
                    if target_id.coord:
                        logger.log_SRIF(target_id.coord, "unwrap func")
                    else:
                        logger.log_SRIF(node.coord, "unwrap func")
                    line_code_def = generator.visit(node).split("\n")[0]
                    annotation = {
                        "class": "SRIF_unwrap_func_call",
                        "line_num": node.coord.line,
                        "line_code": line_code,
                        "line_code_def": line_code_def,
                        "func_call_to_unwrap": generator.visit(temp),
                        "replacement": generator.visit(binary_op.right)
                    }
                    # retrieve ast
                    # binary_op.right = temp
                    break
            return annotation


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


def defectify_SDFN(ast, task_name, logger, exp_spec_dict):
    """
    {
        statement_nodes <- visit_statements(root)
        filter(element.type == function_call or function call in element, statement_nodes)
        target_node <- random_pick(statement_nodes)
        if target_node.type == function_call:
            target_node <- empty_statement
        else:
            target_node.find(function_call).remove()
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    statement_visitor = StatementVisitor(ast)
    statement_visitor.visit(ast)
    stmt_list = statement_visitor.get_nodelist()
    statements_visitor = StatementsVisitor(ast)
    statements_visitor.visit(ast)
    stmts_list = statements_visitor.get_nodelist()
    available_nodes = []
    for stmt_node in stmt_list:
        if type(stmt_node.stmt) == c_ast.FuncCall:
            available_nodes.append(stmt_node)
    for stmts_node in stmts_list:
        for stmt in stmts_node.stmts:
            if type(stmt) == c_ast.FuncCall:
                available_nodes.append(stmts_node)
                break
    if len(available_nodes) == 0:
        print("Warning: No function call can be deleted.")
        return False
    target_node = random_pick_probless(available_nodes)
    annotation = False
    if hasattr(target_node, "stmt"):
        line_code = generator.visit(target_node).split("\n")[1]
        func_call = target_node.stmt
        target_node.stmt = c_ast.EmptyStatement(coord=func_call.coord)
        logger.log_SDFN(func_call.coord, "delete function call from statement")
        annotation = {
            "class": "SDFN",
            "line_num": target_node.coord.line,
            "line_code": line_code
        }
        # retrieve ast
        # target_node.stmt = func_call
    else:
        func_calls = []
        for stmt in target_node.stmts:
            if type(stmt) == c_ast.FuncCall:
                func_calls.append(stmt)
        func_call = random_pick_probless(func_calls)
        index = target_node.stmts.index(func_call)
        line_code = generator.visit(target_node).split("\n")[index+1]
        target_node.stmts.remove(func_call)
        logger.log_SDFN(func_call.coord, "delete function call from statements")
        annotation = {
            "class": "SDFN",
            "line_num": target_node.coord.line,
            "line_code": line_code
        }
        # retrieve ast
        # target_node.block_items.insert(index, func_call)
    return annotation


def defectify_OAIS_add_op(ast, task_name, logger, exp_spec_dict):
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    binary_visitor = BinaryOpVisitor(func)
    binary_visitor.visit(func)
    available_nodes = []
    binary_ops = binary_visitor.get_nodelist()
    for binary_op in binary_ops:
        if binary_op.op in c_arithmetic_binary_operator_set:
            if type(binary_op.left) == c_ast.ID or type(binary_op.right) == c_ast.ID:
                available_nodes.append(binary_op)
    if len(available_nodes) == 0:
        print("no available nodes")
        return False
    target_node = random_pick_probless(available_nodes)
    if type(target_node.left) == c_ast.ID:
        temp = target_node.left
        if temp.name in id_name_map.keys():
            id_type = id_name_map[temp.name]
        else:
            return False
        line_code = generator.visit(target_node).split("\n")[0]
        if id_type in {"int", "short", "long"}:
            right_const = c_ast.Constant(type=id_type,
                                         value=str(random_picker.gen_random(id_type)))
            target_node.left = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/', '%'], None),
                                              left=temp,
                                              right=right_const,
                                              coord=temp.coord)
        elif id_type == "char":
            print("Err: OAIS not fit for char values.")
            return False
        else:
            right_const = c_ast.Constant(type=id_type,
                                         value=str(random_picker.gen_random(id_type)))
            target_node.left = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/'], None),
                                              left=temp,
                                              right=right_const,
                                              coord=temp.coord)
        logger.log_OAIS(target_node.coord, "add_op")
        line_code_def = generator.visit(target_node).split("\n")[0]
        annotation = {
            "class": "OAIS_add_op",
            "line_num": target_node.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def,
            "op_add": target_node.left.op,
            "right_value_add": target_node.left.right.value
        }
        # retrieve ast
        # target_node.left = temp
        return annotation

    if type(target_node.right) == c_ast.ID:
        temp = target_node.right
        if temp.name in id_name_map.keys():
            id_type = id_name_map[temp.name]
        else:
            return False
        line_code = generator.visit(target_node).split("\n")[0]
        if id_type in {"int", "short", "long"}:
            right_const = c_ast.Constant(type=id_type,
                                         value=str(random_picker.gen_random(id_type)))
            target_node.right = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/', '%'], None),
                                               left=temp,
                                               right=right_const,
                                               coord=temp.coord)
        elif id_type == "char":
            print("Err: OAIS not fit for char values.")
            return False
        else:
            right_const = c_ast.Constant(type=id_type,
                                         value=str(random_picker.gen_random(id_type)))
            target_node.right = c_ast.BinaryOp(op=random_pick(['+', '-', '*', '/'], None),
                                               left=temp,
                                               right=right_const,
                                               coord=temp.coord)
        logger.log_OAIS(target_node.coord, "add_op")
        line_code_def = generator.visit(target_node).split("\n")[0]
        annotation = {
            "class": "OAIS_add_op",
            "line_num": target_node.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def,
            "op_add": target_node.right.op,
            "right_value_add": target_node.right.right.value
        }
        # retrieve ast
        # target_node.right = temp
        return annotation


def defectify_OAIS_del_op(ast, task_name, logger, exp_spec_dict):
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    binary_visitor = BinaryOpVisitor(func)
    binary_visitor.visit(func)
    available_nodes = []
    binary_ops = binary_visitor.get_nodelist()
    for binary_op in binary_ops:
        if binary_op.op in c_arithmetic_binary_operator_set:
            if type(binary_op.left) == c_ast.ID or type(binary_op.right) == c_ast.ID:
                available_nodes.append(binary_op)
    if len(available_nodes) == 0:
        print("no available nodes")
        return False
    target_node = random_pick_probless(available_nodes)
    if type(target_node.left) == c_ast.ID:
        daddy_visitor = DaddyVisitor(ast, target_node)
        daddy_visitor.visit(ast)
        dad = daddy_visitor.get_dad()
        if dad is None:
            print("Orphan")
            return False
        line_code = generator.visit(dad).split("\n")[0]
        for slot in dad.__slots__:
            if dad.__getattribute__(slot) == target_node:
                setattr(dad, slot, target_node.left)
                break
        logger.log_OAIS(target_node.coord, "del_op")
        line_code_def = generator.visit(dad).split("\n")[0]
        annotation = {
            "class": "OAIS_del_op",
            "line_num": dad.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def
        }
        return annotation
    if type(target_node.right) == c_ast.ID:
        daddy_visitor = DaddyVisitor(ast, target_node)
        daddy_visitor.visit(ast)
        dad = daddy_visitor.get_dad()
        if dad is None:
            print("Orphan")
            return False
        line_code = generator.visit(dad).split("\n")[0]
        for slot in dad.__slots__:
            if dad.__getattribute__(slot) == target_node:
                setattr(dad, slot, target_node.left)
                break
        logger.log_OAIS(target_node.coord, "del_op")
        line_code_def = generator.visit(dad).split("\n")[0]
        annotation = {
            "class": "OAIS_del_op",
            "line_num": dad.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def
        }
        return annotation


def defectify_OAIS(ast, task_name, logger, exp_spec_dict):
    """
    OAIS is just like to_expr in SRIF, but different in sequence-flow
    {
    }
    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict
    :return:
    """
    OAIS_EQUAL_PROB = True
    if "OAIS" in exp_spec_dict.keys():
        oais_spec = exp_spec_dict["OAIS"]
        if len(oais_spec) != 0:
            OAIS_EQUAL_PROB = False
    if OAIS_EQUAL_PROB:
        func = globals()[random_pick_probless(["defectify_OAIS_add_op",
                                               "defectify_OAIS_del_op"])]
    else:
        func = globals()["defectify_" + random_pick(list(oais_spec.keys()), list(oais_spec.values()))]
    return func(ast, task_name, logger, exp_spec_dict)


def defectify_STYP(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    global_func_names = [item.decl.name for item in global_funcs]
    decl_visitor = DeclVisitor(ast)
    decl_visitor.visit(ast)
    decls = decl_visitor.get_nodelist()
    var_decls = [item for item in decls if item.name not in global_func_names]
    int_family = ["short", "int", "long"]
    char_family = ["char"]
    float_family = ["float", "double"]
    var_decl = random_pick_probless(var_decls)
    if var_decl is None:
        print("No variant declaration.")
        return False
    if type(var_decl.type) in {c_ast.ArrayDecl, c_ast.PtrDecl, c_ast.FuncDecl, c_ast.Struct}:
        print("Conversion of arrays, pointers, function calls and structs is not supported")
        return False
    if type(var_decl.type.type) in {c_ast.Struct}:
        print("Conversion of arrays, pointers, function calls and structs is not supported")
        return False
    type_name = var_decl.type.type.names[0]
    if type_name in int_family:
        int_family.remove(type_name)
        replace_type = random_pick_probless(int_family)
    elif type_name in char_family:
        replace_type = "int"
    elif type_name in float_family:
        float_family.remove(type_name)
        replace_type = random_pick_probless(float_family)
    else:
        print("Err: Current Type cannot be replaced")
        return False
    line_code = generator.visit(var_decl).split("\n")[0]
    temp = var_decl.type.type.names[0]
    var_decl.type.type = c_ast.IdentifierType(names=[replace_type])
    logger.log_STYP(var_decl.coord, temp, replace_type)
    line_code_def = generator.visit(var_decl).split("\n")[0]
    annotation = {
        "class": "STYP",
        "line_num": var_decl.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "type": temp,
        "type_replace": replace_type
    }
    # retrieve ast
    # var_decl.type.type = c_ast.IdentifierType(names=[temp])
    return annotation


def defectify_SMOV(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    # statements_visitor = StatementsVisitor(ast)
    statements_visitor = CompoundVisitor(ast)
    # statements_visitor.generic_visit(ast)
    statements_visitor.visit(ast)
    stmts_nodes = statements_visitor.get_nodelist()
    available_nodes = []
    available_decls = []
    available_body = []
    for stmts_node in stmts_nodes:
        if stmts_node.block_items is None:
            continue
        # stmts_node.stmts = list(filter(lambda x: type(x) not in {c_ast.Decl, c_ast.FuncDecl, c_ast.PtrDecl, c_ast.Struct}, stmts_node.stmts))
        decls = list(
            filter(lambda x: type(x) in {c_ast.Decl, c_ast.FuncDecl, c_ast.PtrDecl, c_ast.Struct},
                   stmts_node.block_items))
        body = list(
            filter(lambda x: type(x) not in {c_ast.Decl, c_ast.FuncDecl, c_ast.PtrDecl, c_ast.Struct},
                   stmts_node.block_items))
        # if len(stmts_node.stmts) > 1:
        #     available_stmts.append(stmts_node.stmts)
        if len(body) > 1:
            available_nodes.append(stmts_node)
            available_decls.append(decls)
            available_body.append(body)
    if len(available_nodes) == 0:
        print("Warning: No available statement block found.")
        return False
    target_node = random_pick_probless(available_nodes)
    target_stmts = target_node.block_items
    index = available_nodes.index(target_node)
    decls = available_decls[index]
    body = available_body[index]
    length = len(body)
    distance = get_randint(1, length - 1)
    stmt_1 = random_pick_probless(body)
    index_1 = body.index(stmt_1)
    index_2 = (index_1 + distance) % length
    temp = body[index_1]
    body[index_1] = body[index_2]
    body[index_2] = temp
    result = decls + body
    target_node.block_items = result
    logger.log_SMOV(target_stmts[index_1].coord, target_stmts[index_2].coord)
    annotation = {
        "class": "SMOV",
        "line_num_1": body[index_2].coord.line,
        "line_code_1": generator.visit(body[index_2]),
        "line_num_2": body[index_1].coord.line,
        "line_code_2": generator.visit(body[index_1])
    }
    # retrieve ast
    # temp = target_stmts[index_1]
    # target_stmts[index_1] = target_stmts[index_2]
    # target_stmts[index_2] = temp
    return annotation


def defectify_OFPO(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    global_ids, global_funcs = parse_fileAST_exts(ast)
    available_funcs = []
    funcs_param_type_map = {}
    for global_func in global_funcs:
        if global_func.decl.type.args is None:
            continue
        params = global_func.decl.type.args.params
        param_type_map = {}
        for param in params:
            if type(param) == c_ast.ID:
                continue
            param_type = param.type.type
            if type(param_type) == c_ast.IdentifierType:
                param_type_name = param_type.names[0]
            elif type(param_type) == c_ast.PtrDecl:
                if type(param_type.type.type) in {c_ast.Struct}:
                    continue
                param_type_name = param_type.type.type.names[0] + "*"
            else:
                continue
            if param_type_name in param_type_map.keys():
                param_type_map[param_type_name].append(params.index(param))
            else:
                param_type_map[param_type_name] = [params.index(param)]
        for index_list in param_type_map.values():
            if len(index_list) > 1:
                available_funcs.append(global_func)
                funcs_param_type_map[global_func.decl.name] = param_type_map
                break
    func_call_visitor = FuncCallVisitor(ast)
    func_call_visitor.visit(ast)
    func_calls = func_call_visitor.get_nodelist()
    available_func_names = [func.decl.name for func in available_funcs]
    available_func_calls = [func_call for func_call in func_calls if func_call.name.name in available_func_names]
    if len(available_func_calls) == 0:
        print("Warning: No available function calls can be found.")
        return False
    target_func_call = random_pick_probless(available_func_calls)
    line_code = generator.visit(target_func_call).split("\n")[0]
    target_param_type_map = funcs_param_type_map[target_func_call.name.name]
    available_param_index = {key: value for key, value in target_param_type_map.items() if len(value) > 1}
    target_key = random_pick_probless(list(available_param_index.keys()))
    target_param_index = available_param_index[target_key]
    length = len(target_param_index)
    index_1 = target_param_index.index(random_pick_probless(target_param_index))
    distance = get_randint(1, length - 1)
    index_2 = (index_1 + distance) % length
    index_1 = target_param_index[index_1]
    index_2 = target_param_index[index_2]
    target_arg = target_func_call.args.exprs
    temp = target_arg[index_1]
    target_arg[index_1] = target_arg[index_2]
    target_arg[index_2] = temp
    logger.log_OFPO(target_func_call.coord, index_1, index_2)
    line_code_def = generator.visit(target_func_call).split("\n")[0]
    annotation = {
        "class": "OFPO",
        "line_num": target_func_call.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "index_1": index_1,
        "index_2": index_2
    }
    # retrieve ast
    # temp = target_arg[index_1]
    # target_arg[index_1] = target_arg[index_2]
    # target_arg[index_2] = temp
    return annotation


def defectify_DCCR_to_const(ast, task_name, logger, exp_spec_dict):
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
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    op_visitor = OpVisitor(func)
    op_visitor.generic_visit(func)
    nodes = op_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No nodes with op can be found.")
        return False
    available_nodes = []
    for node in nodes:
        if type(node) == c_ast.UnaryOp:
            if type(node.expr) == c_ast.Constant:
                available_nodes.append(node)
        elif type(node) == c_ast.BinaryOp:
            if type(node.left) == c_ast.Constant or type(node.right) == c_ast.Constant:
                available_nodes.append(node)
        else:
            continue
    if len(available_nodes) == 0:
        print("No constant can be found.")
        return False

    target_node = random_pick_probless(available_nodes)
    line_code = generator.visit(target_node).split("\n")[0]
    replacement_offset = random_picker_spec["replacement_offset"]

    if type(target_node) == c_ast.UnaryOp:
        temp = target_node.expr
        const_type = target_node.expr.type
        const_value = target_node.expr.value
        const_value = re.sub("[^0-9]", "", const_value)
        if const_type in {'int', 'long', 'short'}:
            offset = random_pick_probless(replacement_offset)
            new_value = str(int(const_value) + offset)
            new_const = c_ast.Constant(type=const_type,
                                       value=new_value,
                                       coord=target_node.expr.coord)
            target_node.expr = new_const
            logger.log_DCCR(target_node.coord, "to_const")
        elif const_type in {'float', 'double'}:
            offset = random_pick_probless(replacement_offset)
            new_value = str(float(const_value) + offset)
            new_const = c_ast.Constant(type=const_type,
                                       value=new_value,
                                       coord=target_node.expr.coord)
            target_node.expr = new_const
            logger.log_DCCR(target_node.coord, "to_const")
        elif const_type in {'char'}:
            new_value = str(random_picker.gen_random('char'))
            new_const = c_ast.Constant(type=const_type,
                                       value=new_value,
                                       coord=target_node.expr.coord)
            target_node.expr = new_const
            logger.log_DCCR(target_node.coord, "to_const")
        else:
            print("Other type not supported.")
            return False
        line_code_def = generator.visit(target_node).split("\n")[0]
        annotation = {
            "class": "DCCR_to_const",
            "line_num": target_node.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def,
            "const": temp.value,
            "const_replacement": new_const.value
        }
    elif type(target_node) == c_ast.BinaryOp:
        if type(target_node.left) == c_ast.Constant:
            temp = target_node.left
            const_type = target_node.left.type
            const_value = target_node.left.value
            const_value = re.sub("[^0-9]", "", const_value)
            if const_type in {'int', 'long', 'short'}:
                offset = random_pick_probless(replacement_offset)
                new_value = str(int(const_value) + offset)
                new_const = c_ast.Constant(type=const_type,
                                           value=new_value,
                                           coord=target_node.left.coord)
                target_node.left = new_const
                logger.log_DCCR(target_node.coord, "to_const")
            elif const_type in {'float', 'double'}:
                offset = random_pick_probless(replacement_offset)
                new_value = str(float(const_value) + offset)
                new_const = c_ast.Constant(type=const_type,
                                           value=new_value,
                                           coord=target_node.left.coord)
                target_node.left = new_const
                logger.log_DCCR(target_node.coord, "to_const")
            elif const_type in {'char'}:
                new_value = str(random_picker.gen_random('char'))
                new_const = c_ast.Constant(type=const_type,
                                           value=new_value,
                                           coord=target_node.left.coord)
                target_node.left = new_const
                logger.log_DCCR(target_node.coord, "to_const")
            else:
                print("Other type not supported.")
                return False
        else:
            temp = target_node.right
            const_type = target_node.right.type
            const_value = target_node.right.value
            const_value = re.sub("[^0-9]", "", const_value)
            if const_type in {'int', 'long', 'short'}:
                offset = random_pick_probless(replacement_offset)
                new_value = str(int(const_value) + offset)
                new_const = c_ast.Constant(type=const_type,
                                           value=new_value,
                                           coord=target_node.right.coord)
                target_node.right = new_const
                logger.log_DCCR(target_node.coord, "to_const")
            elif const_type in {'float', 'double'}:
                offset = random_pick_probless(replacement_offset)
                new_value = str(float(const_value) + offset)
                new_const = c_ast.Constant(type=const_type,
                                           value=new_value,
                                           coord=target_node.right.coord)
                target_node.right = new_const
                logger.log_DCCR(target_node.coord, "to_const")
            elif const_type in {'char'}:
                new_value = str(random_picker.gen_random('char'))
                new_const = c_ast.Constant(type=const_type,
                                           value=new_value,
                                           coord=target_node.right.coord)
                target_node.right = new_const
                logger.log_DCCR(target_node.coord, "to_const")
            else:
                print("Other type not supported.")
                return False
        line_code_def = generator.visit(target_node).split("\n")[0]
        annotation = {
            "class": "DCCR_to_const",
            "line_num": target_node.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def,
            "const": temp.value,
            "const_replacement": new_const.value
        }
    else:
        print("Strange Type")
        print(type(target_node))
        return False
    return annotation


def defectify_DCCR_to_var(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    print("testing dccr2var")
    if "random_picker" in exp_spec_dict.keys():
        random_picker_spec = exp_spec_dict["random_picker"]
        random_picker = RandomPicker(random_picker_spec["random_int_list"], random_picker_spec["random_chr_list"])
    else:
        random_picker = RandomPicker(None, None)

    global_ids, global_funcs = parse_fileAST_exts(ast)
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    available_decls = []
    params = func.decl.type.args.params if func.decl.type.args is not None else None
    if params:
        for param in params:
            if not hasattr(param, "type"):
                continue
            if param.name not in {"argc", "argv"} \
                    and type(param.type) not in {c_ast.ArrayDecl, c_ast.FuncDecl, c_ast.Struct, c_ast.PtrDecl}:
                available_decls.append(param.type)
    if len(global_ids) > 0:
        for global_id in global_ids:
            if type(global_id.type) not in {c_ast.ArrayDecl, c_ast.FuncDecl, c_ast.Struct, c_ast.PtrDecl}:
                available_decls.append(global_id.type)
    global_func_names = [item.decl.name for item in global_funcs]
    for funcwise_decl in type_decls:
        if funcwise_decl.declname not in global_func_names:
            available_decls.append(funcwise_decl)
    op_visitor = OpVisitor(func)
    op_visitor.generic_visit(func)
    nodes = op_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No nodes with op can be found.")
        return False
    available_nodes = []
    for node in nodes:
        if type(node) == c_ast.UnaryOp:
            if type(node.expr) == c_ast.Constant:
                available_nodes.append(node)
        elif type(node) == c_ast.BinaryOp:
            if type(node.left) == c_ast.Constant or type(node.right) == c_ast.Constant:
                available_nodes.append(node)
        else:
            continue
    if len(available_nodes) == 0:
        print("No constant can be found.")
        return False

    target_node = random_pick_probless(available_nodes)
    line_code = generator.visit(target_node).split("\n")[0]
    replace_var = random_pick_probless(available_decls)
    if replace_var is None:
        print("No replacement found.")
        return False
    if type(target_node) == c_ast.UnaryOp:
        temp = target_node.expr.value
        target_node.expr = c_ast.ID(name=replace_var.declname,
                                    coord=target_node.expr.coord)
        logger.log_DCCR(target_node.expr.coord, "to_var")
        line_code_def = generator.visit(target_node).split("\n")[0]
        annotation = {
            "class": "DCCR_to_var",
            "line_num": target_node.coord.line,
            "line_code": line_code,
            "line_code_def": line_code_def,
            "const": temp,
            "const_replacement": replace_var.declname
        }
    elif type(target_node) == c_ast.BinaryOp:
        if type(target_node.left) == c_ast.Constant:
            temp = target_node.left.value
            target_node.left = c_ast.ID(name=replace_var.declname,
                                        coord=target_node.left.coord)
            logger.log_DCCR(target_node.left.coord, "to_var")
            line_code_def = generator.visit(target_node).split("\n")[0]
            annotation = {
                "class": "DCCR_to_var",
                "line_num": target_node.coord.line,
                "line_code": line_code,
                "line_code_def": line_code_def,
                "const": temp,
                "const_replacement": replace_var.declname
            }
        else:
            temp = target_node.right.value
            target_node.right = c_ast.ID(name=replace_var.declname,
                                         coord=target_node.right.coord)
            logger.log_DCCR(target_node.right.coord, "to_var")
            line_code_def = generator.visit(target_node).split("\n")[0]
            annotation = {
                "class": "DCCR_to_var",
                "line_num": target_node.coord.line,
                "line_code": line_code,
                "line_code_def": line_code_def,
                "const": temp,
                "const_replacement": replace_var.declname
            }
    else:
        print("strange")
        return False
    return annotation


def defectify_DCCR(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    DCCR_EQUAL_PROB = True
    if "DCCR" in exp_spec_dict.keys():
        dccr_spec = exp_spec_dict["DCCR"]
        if len(dccr_spec) != 0:
            DCCR_EQUAL_PROB = False
    if DCCR_EQUAL_PROB:
        func = globals()[random_pick_probless(["defectify_DCCR_to_const",
                                               "defectify_DCCR_to_var"])]
    else:
        func = globals()["defectify_" + random_pick(list(dccr_spec.keys()), list(dccr_spec.values()))]
    return func(ast, task_name, logger, exp_spec_dict)


def defectify_DRVA_to_const(ast, task_name, logger, exp_spec_dict):
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    assignment_visitor = AssignmentVisitor(func)
    assignment_visitor.visit(func)
    nodes = assignment_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No Assignment node can be found.")
        return False
    available_nodes = [node for node in nodes if type(node.rvalue) == c_ast.ID]
    if len(available_nodes) == 0:
        print("No available node can be found.")
        return False
    target_node = random_pick_probless(available_nodes)
    line_code = generator.visit(target_node).split("\n")[0]
    target_id = target_node.rvalue
    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False
    temp = target_node.rvalue.name
    target_node.rvalue = c_ast.Constant(type=target_id_type,
                                        value=random_picker.gen_random(target_id_type),
                                        coord=target_node.rvalue.coord)
    logger.log_DRVA(target_node.coord, "to_const")
    line_code_def = generator.visit(target_node).split("\n")[0]
    annotation = {
        "class": "DRVA_to_const",
        "line_num": target_node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "var": temp,
        "var_replacement": target_node.rvalue.value
    }
    return annotation


def defectify_DRVA_to_var(ast, task_name, logger, exp_spec_dict):
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    assignment_visitor = AssignmentVisitor(func)
    assignment_visitor.visit(func)
    nodes = assignment_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No Assignment node can be found.")
        return False
    available_nodes = [node for node in nodes if type(node.rvalue) == c_ast.ID]
    if len(available_nodes) == 0:
        print("No available node can be found.")
        return False
    target_node = random_pick_probless(available_nodes)
    line_code = generator.visit(target_node).split("\n")[0]
    target_id = target_node.rvalue
    temp = target_id.name
    id_visitor = IDVisitor(func)
    id_visitor.visit(func)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    if len(id_name_set) + len(global_ids) < 2:
        print("Warning: no replacement found.")
        return False
    ids_remain = id_name_set - {target_id.name}
    global_ids_name = [item.name for item in global_ids]
    ids_remain = ids_remain.union(set(global_ids_name) - {target_id.name})

    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False
    matched_ids = []
    for id_remain in ids_remain:
        if id_remain in id_name_map.keys() and id_name_map[id_remain] == target_id_type:
            matched_ids.append(id_remain)
    if len(matched_ids) == 0:
        print("Warning: no replacement found.")
        return False
    # 4. randomly pick one matched identifier
    matched_id = random_pick_probless(matched_ids)
    target_id.name = matched_id
    logger.log_DRVA(target_node.coord, "to_var")
    line_code_def = generator.visit(target_node).split("\n")[0]
    annotation = {
        "class": "DRVA_to_var",
        "line_num": target_node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "var": temp,
        "var_replacement": target_node.rvalue.name
    }
    return annotation


def defectify_DRVA(ast, task_name, logger, exp_spec_dict):
    """

    :param ast:
    :param task_name:
    :param logger:
    :param exp_spec_dict:
    :return:
    """
    DRVA_EQUAL_PROB = True
    if "DRVA" in exp_spec_dict.keys():
        drva_spec = exp_spec_dict["DRVA"]
        if len(drva_spec) != 0:
            DRVA_EQUAL_PROB = False
    if DRVA_EQUAL_PROB:
        func = globals()[random_pick_probless(["defectify_DRVA_to_const",
                                               "defectify_DRVA_to_var"])]
    else:
        func = globals()["defectify_" + random_pick(list(drva_spec.keys()), list(drva_spec.values()))]
    return func(ast, task_name, logger, exp_spec_dict)


def defectify_DRWV(ast, task_name, logger, exp_spec_dict):
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
        if type(global_id) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl} \
                and type(global_id.type.type) not in {c_ast.ArrayDecl, c_ast.TypeDecl, c_ast.Struct, c_ast.PtrDecl}:
            id_name_map[global_id.name] = global_id.type.type.names[0]
    # 1. randomly pick one function from global functions including main()
    func = random_pick_probless(global_funcs)
    if func is None:
        print("NONE")
        return False
    assignment_visitor = AssignmentVisitor(func)
    assignment_visitor.visit(func)
    nodes = assignment_visitor.get_nodelist()
    if len(nodes) == 0:
        print("No Assignment node can be found.")
        return False
    available_nodes = [node for node in nodes if type(node.lvalue) == c_ast.ID]
    if len(available_nodes) == 0:
        print("No available node can be found.")
        return False
    target_node = random_pick_probless(available_nodes)
    line_code = generator.visit(target_node).split("\n")[0]
    target_id = target_node.lvalue
    temp = target_id.name
    id_visitor = IDVisitor(func)
    id_visitor.visit(func)
    ids = id_visitor.get_id_list()
    global_func_names = [func.decl.name for func in global_funcs]
    for id in ids:
        if id.name in global_func_names:
            ids.remove(id)
    id_name_set = set([id.name for id in ids])
    if len(id_name_set) + len(global_ids) < 2:
        print("Warning: no replacement found.")
        return False
    ids_remain = id_name_set - {target_id.name}
    global_ids_name = [item.name for item in global_ids]
    ids_remain = ids_remain.union(set(global_ids_name) - {target_id.name})

    type_decl_visitor = TypeDeclVisitor(func)
    type_decl_visitor.visit(func)
    type_decls = type_decl_visitor.get_nodelist()
    for type_decl in type_decls:
        if type(type_decl.type) not in {c_ast.Struct}:
            id_name_map[type_decl.declname] = type_decl.type.names[0]
    if target_id.name in id_name_map.keys():
        target_id_type = id_name_map[target_id.name]
    else:
        return False
    matched_ids = []
    for id_remain in ids_remain:
        if id_remain in id_name_map.keys() and id_name_map[id_remain] == target_id_type:
            matched_ids.append(id_remain)
    if len(matched_ids) == 0:
        print("Warning: no replacement found.")
        return False
    # 4. randomly pick one matched identifier
    matched_id = random_pick_probless(matched_ids)
    target_id.name = matched_id
    logger.log_DRWV(target_node.coord)
    line_code_def = generator.visit(target_node).split("\n")[0]
    annotation = {
        "class": "DRWV",
        "line_num": target_node.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "var": temp,
        "var_replacement": target_node.lvalue.name
    }
    return annotation


def defectify_DCCA(ast, task_name, logger, exp_spec_dict):
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

    array_decl_visitor = ArrayDeclVisitor(ast)
    array_decl_visitor.visit(ast)
    array_decls = array_decl_visitor.get_nodelist()
    if len(array_decls) == 0:
        print("No array declaration found.")
        return False
    random_array_len_list = random_picker_spec["random_array_len_list"]
    target_array_decl = random_pick_probless(array_decls)
    line_code = generator.visit(target_array_decl).split("\n")[0]
    extra = []
    dim_value = 0
    if type(target_array_decl.dim) == c_ast.Constant:
        dim_value = int(target_array_decl.dim.value)
        extra.append(dim_value * 10)
        extra.append(dim_value + 1)
        if dim_value > 1:
            extra.append(dim_value - 1)
    else:
        return False
    target_array_decl.dim = c_ast.Constant(type='int',
                                           value=str(random_pick_probless(random_array_len_list + extra)),
                                           coord=target_array_decl.coord)
    logger.log_DCCA(target_array_decl.coord, "rand")
    line_code_def = generator.visit(target_array_decl).split("\n")[0]
    annotation = {
        "class": "DCCA",
        "line_num": target_array_decl.coord.line,
        "line_code": line_code,
        "line_code_def": line_code_def,
        "dimension": dim_value,
        "dimension_replacement": target_array_decl.dim.value
    }
    return annotation


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
    print("")


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
