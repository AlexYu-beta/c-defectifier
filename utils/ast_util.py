from pycparser import c_ast, c_parser


def parse_fileAST_exts(ast):
    """
    parsing file ast to extensions
    :param ast:
    :return:
    """
    global_ids = []
    global_funcs = []
    for ext in ast.ext:
        if type(ext) == c_ast.Decl:
            global_ids.append(ext)
        elif type(ext) == c_ast.FuncDef:
            global_funcs.append(ext)
        else:
            print("something else")
    return global_ids, global_funcs


def get_main(ast):
    """
    get main() from ast
    :param ast:
    :return:
    """
    main_func = None
    for ext in ast.ext:
        if type(ext) == c_ast.FuncDef and ext.decl.name == "main":
            main_func = ext
    return main_func


if __name__ == '__main__':
    exp_src = "/home/alex/PycharmProjects/c-defectifier/exp_src/test.c"
    src_file = open(exp_src, 'r')
    code = src_file.read()
    src_file.close()
    parser = c_parser.CParser()
    ast = parser.parse(code)
    global_ids, global_funcs= parse_fileAST_exts(ast)

