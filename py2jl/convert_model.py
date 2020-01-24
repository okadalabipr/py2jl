import os
import re
from py2jl import jl_source
from py2jl import triming_tools


def convert_model(jl_dir, py_dir):
    """
    space_num = int(
        input(
            'How many spaces do you use for indentation? (input integer):'
        )
    )
    """
    os.makedirs(
        jl_dir + '/model', exist_ok=True
    )
    os.makedirs(
        jl_dir + '/model/name2idx', exist_ok=True
    )
    make_name2idx(jl_dir)
    make_model(jl_dir)
    make_parameters(jl_dir, py_dir, space_num=4)
    make_variables(jl_dir, py_dir, space_num=4)
    make_param_const(jl_dir, py_dir, space_num=4)
    make_initial_condition(jl_dir, py_dir, space_num=4)
    make_differential_equation(jl_dir, py_dir, space_num=4)


def make_name2idx(jl_dir):
    jl_dir = jl_dir + '/model/name2idx/name2idx.jl'

    name2idx = jl_source.make_name2idx_header()

    with open(jl_dir, mode='w') as f:
        f.write(name2idx)


def make_model(jl_dir):
    jl_dir = jl_dir + '/model/model.jl'\

    model = jl_source.model_header()

    with open(jl_dir, mode='w') as f:
        f.write(model)


def make_parameters(jl_dir, py_dir, space_num):
    jl_dir = jl_dir + '/model/name2idx/parameters.jl'
    py_dir = py_dir + '/model/name2idx/parameters.py'

    with open(py_dir, mode='r') as f:
        lines = f.readlines()
    lines = triming_tools.lines_triming(lines, space_num)

    parameters = jl_source.parameters_header()

    keywords = False
    for i, line in enumerate(lines):
        if lines[i-1].find('param_names') != -1:
            keywords = True
            #print('\n\n\ntest:start of values is found')
        elif keywords and line.find('len_f_params') != -1:
            break
            #print('test:end of values is found\n\n\n\n')
        if keywords:
            parameters += line

    parameters = parameters + jl_source.parameters_footer()

    with open(jl_dir, mode='w') as f:
        f.write(parameters)


def make_variables(jl_dir, py_dir, space_num):
    jl_dir = jl_dir + '/model/name2idx/variables.jl'
    py_dir = py_dir + '/model/name2idx/variables.py'

    with open(py_dir, mode='r') as f:
        lines = f.readlines()
    lines = triming_tools.lines_triming(lines, space_num)

    variables = jl_source.variables_header()

    keywords = False
    for i, line in enumerate(lines):
        if lines[i-1].find('var_names') != -1:
            keywords = True
            #print('\n\n\ntest:start of values is found')
        elif keywords and line.find('len_f_vars') != -1:
            break
            #print('test:end of values is found\n\n\n\n')
        if keywords:
            variables += line

    variables = variables + jl_source.variables_footer()

    with open(jl_dir, mode='w') as f:
        f.write(variables)


def make_param_const(jl_dir, py_dir, space_num):
    jl_dir = jl_dir + '/model/param_const.jl'
    py_dir = py_dir + '/model/param_const.py'

    with open(py_dir, mode='r') as f:
        lines = f.readlines()
    lines = triming_tools.lines_triming(lines, space_num)

    param_const = jl_source.param_const_header()

    keywords = False
    for i, line in enumerate(lines):
        if lines[i-1].find('len_f_params') != -1:
            keywords = True
            #print('\n\n\ntest:start of values is found')
        elif keywords and line.find('return x') != -1:
            break
            #print('test:end of values is found\n\n\n\n')
        if keywords:
            param_const += line

    param_const += jl_source.param_const_footer()

    with open(jl_dir, mode='w') as f:
        f.write(param_const)


def make_initial_condition(jl_dir, py_dir, space_num):
    jl_dir = jl_dir + '/model/initial_condition.jl'
    py_dir = py_dir + '/model/initial_condition.py'

    with open(py_dir, mode='r') as f:
        lines = f.readlines()
    lines = triming_tools.lines_triming(lines, space_num)

    initial_condition = jl_source.initial_condition_header()

    keywords = False
    for i, line in enumerate(lines):
        if lines[i-1].find('len_f_vars') != -1:
            keywords = True
            #print('\n\n\ntest:start of values is found')
        elif keywords and line.find('return y0') != -1:
            break
            #print('test:end of values is found\n\n\n\n')
        if keywords:
            initial_condition += line

    initial_condition += jl_source.initial_condition_footer()

    with open(jl_dir, mode='w') as f:
        f.write(initial_condition)


def make_differential_equation(jl_dir, py_dir, space_num):
    jl_dir = jl_dir + '/model/differential_equation.jl'
    py_dir = py_dir + '/model/differential_equation.py'

    with open(py_dir, mode='r') as f:
        lines = f.readlines()
    lines = triming_tools.lines_triming(lines, space_num)
    lines = triming_tools.insert_end(
        lines, triming_tools.search_end(lines, space_num))

    differential_equation = jl_source.differential_equation_header1()
    for i, line in enumerate(lines):
        if line.replace(' ', '').find('v=') != -1:
            differential_equation += str(
                int(
                    re.sub(
                        "\\D", "", line[line.find('*'):]
                    )
                ) - 1
            )
            lines.pop(i)
            break
    differential_equation += jl_source.differential_equation_header2()

    keywords = False
    for i, line in enumerate(lines):
        if lines[i-1].find('def diffeq(t,y,x):') != -1:
            keywords = True
            #print('\n\n\ntest:start of values is found')
        elif keywords and line.find('return dydt') != -1:
            break
            #print('test:end of values is found\n\n\n\n')
        if keywords:
            differential_equation += line

    differential_equation += jl_source.differential_equation_footer()

    with open(jl_dir, mode='w') as f:
        f.write(differential_equation)
