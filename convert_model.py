import os
import re

jl_dir = 'converted'
py_dir = '.'


def convert_model(jl_dir):
    os.makedirs(jl_dir+'/model', exist_ok=True)
    os.makedirs(jl_dir+'/model/name2idx', exist_ok=True)

    make_name2idx(jl_dir)
    make_model(jl_dir)
    make_parameters(jl_dir, py_dir)
    make_variables(jl_dir, py_dir)
    make_param_const(jl_dir, py_dir)
    make_initial_condition(jl_dir, py_dir)
    make_differential_equation(jl_dir, py_dir)


def make_name2idx(jl_dir):
    jl_dir = jl_dir + '/model/name2idx/name2idx.jl'

    name2idx = "\
module Name2Idx\n\
\n\
export C, V\n\
\n\
include(\"parameters.jl\")\n\
include(\"variables.jl\")\n\
\n\
end # module\
"

    with open(jl_dir, mode='w') as f:
        f.write(name2idx)


def make_model(jl_dir):
    jl_dir = jl_dir + '/model/model.jl'
    model = "\
module Model\n\
\n\
export C, V, f_params, initial_values, diffeq\n\
\n\
include(\"name2idx/name2idx.jl\");\n\
using .Name2Idx\n\
\n\
include(\"param_const.jl\");\n\
include(\"initial_condition.jl\");\n\
include(\"differential_equation.jl\");\n\
\n\
end # module\
"

    with open(jl_dir, mode='w') as f:
        f.write(model)


def make_parameters(jl_dir, py_dir):
    jl_dir = jl_dir + '/model/name2idx/parameters.jl'
    py_dir = py_dir + '/model/name2idx/parameters.py'

    data_start = 0
    data_end = 0
    with open(py_dir, mode='r') as f:
        data = f.readlines()
        for i, d in enumerate(data):
            if d.find('param_names = [\\') != -1:
                data_start = i
                #print('\n\n\ntest:param_start find')
            if d.find(']') != -1:
                data_end = i
                #print('test:param_end find\n\n\n\n')

    parameters = "\
module C\n\
\n\
const param_names = [\n\
"

# 範囲は'param_names = [\および'len_f_params'\を除くためそれぞれ+-1
    for i in range(data_start+1, data_end-1):
        parameters += data[i].replace('\'', '\"')

    parameters = parameters + "\
]\n\
\n\
for (idx,name) in enumerate(param_names)\n\
    eval(Meta.parse(\"const $name = $idx\"))\n\
end\n\
\n\
const len_f_params = length(param_names)\n\
\n\
end  # module"

    # print(parameters)

    with open(jl_dir, mode='w') as f:
        f.write(parameters)


def make_variables(jl_dir, py_dir):
    jl_dir = jl_dir + '/model/name2idx/variables.jl'
    py_dir = py_dir + '/model/name2idx/variables.py'

    data_start = 0
    data_end = 0
    with open(py_dir, mode='r') as f:
        data = f.readlines()
        for i, d in enumerate(data):
            if d.find('var_names = [\\') != -1:
                data_start = i
                #print('\n\n\ntest:var_start find')
            if d.find(']') != -1:
                data_end = i
                #print('test:var_end find\n\n\n\n')

    variables = "\
module V\n\
\n\
const var_names = [\n"

# 範囲は'param_names = [\および'len_f_vars'\を除くためそれぞれ+-1
    for i in range(data_start+1, data_end-1):
        variables += data[i].replace('\'', '\"')

    variables = variables + "\
]\n\
\n\
for (idx,name) in enumerate(var_names)\n\
    eval(Meta.parse(\"const $name = $idx\"))\n\
end\n\
\n\
const len_f_vars = length(var_names)\n\
\n\
end  # module"

    # print(variables)

    with open(jl_dir, mode='w') as f:
        f.write(variables)


def make_param_const(jl_dir, py_dir):
    jl_dir = jl_dir + '/model/param_const.jl'
    py_dir = py_dir + '/model/param_const.py'

    param_const = '\
function f_params()::Vector{Float64}\n\
    p::Vector{Float64} = zeros(C.len_f_params)\n\n\
'

    with open(py_dir) as f:
        data = f.readlines()

    for i, d in enumerate(data):
        if d.find('x[C.') != -1:
            param_const += d.replace('x[C.', 'p[C.')

    param_const += '\
    \n\
    return p\n\
end'

    with open(jl_dir, mode='w') as f:
        f.write(param_const)


def make_initial_condition(jl_dir, py_dir):
    jl_dir = jl_dir + '/model/initial_condition.jl'
    py_dir = py_dir + '/model/initial_condition.py'

    initial_condition = '\
function initial_values()::Vector{Float64}\n\
    u0::Vector{Float64} = zeros(V.len_f_vars)\n\n\
'

    with open(py_dir) as f:
        data = f.readlines()

    for i, d in enumerate(data):
        if d.find('y0[') != -1:
            initial_condition += d.replace('y0[V.', 'u0[V.')

    initial_condition += '\
    \n\
    return u0\n\
end'

    with open(jl_dir, mode='w') as f:
        f.write(initial_condition)


def make_differential_equation(jl_dir, py_dir):
    jl_dir = jl_dir + '/model/differential_equation.jl'
    py_dir = py_dir + '/model/differential_equation.py'

    with open(py_dir) as f:
        data = f.readlines()

    differential_equation = '\
function diffeq(du,u,p,t)\n\
    v::Vector{Float64} = zeros(\
'
    for i, d in enumerate(data):
        if d.replace(' ', '').find('v=') != -1:
            differential_equation += re.sub("\\D", "", d[d.find('*'):])
            data.pop(i)
            break

    differential_equation += ')\n'

    data_start = 0
    data_end = 0

    for i, d in enumerate(data):
        if d.find('def diffeq(t,y,x):') != -1:
            data_start = i
            #print('\n\n\ntest:param_start find:',data_start)
        if d.find('return dydt') != -1:
            data_end = i
            #print('test:param_end find:',data_end,'\n\n\n\n')

    for i, d in enumerate(data):
        data[i] = d.strip('\n')

    for i in range(data_start+1, data_end):
        data[i] = data[i].replace('x[C.', 'p[C.')
        data[i] = data[i].replace('y[V.', 'u[V.')
        data[i] = data[i].replace('dydt[V.', 'du[V.')
        data[i] = data[i].replace('**', '^')
        data[i] = data[i].replace('elif ', 'elseif ')
        if (data[i].find('if') != -1 and data[i].find(':') != -1
            or data[i].find('else') != -1):
            data[i] = data[i].strip(':')
    data = insert_end(data, search_end(data))

    for i in range(data_start+1, data_end):
        differential_equation += data[i] + '\n'
    differential_equation += '\
    \n\
end'

    with open(jl_dir, mode='w') as f:
        f.write(differential_equation)


def search_end(data):
    indents = []
    end_line = []

    prev = 0
    for i, d in enumerate(data):
        if d.strip() == '':
            ind = prev
        else:
            ind = d.count('    ')
            if d.find('else') != -1:
                ind = ind + 1
            prev = ind
        indents.append(ind)

    start = 0
    for i in range(len(data)):
        if indents[i] < indents[i-1] and i > 0:
            j = 1
            while data[i-j].strip(' ') == '':
                j = j + 1
            #print('endline is ',i-j+1,indents[i-1]-1,data[i-j])
            end_line.append([i-j+1, indents[i-1]-1])
    return end_line


def insert_end(data, end_line):
    for i, line in enumerate(end_line):
        ind = ''
        for j in range(line[1]):
            ind += '    '
        ind += 'end'
        data.insert(line[0]+i, ind)

    # for i in range(len(data)):
        # print(data[i])
    return data


if __name__ == '__main__':
    convert_model(jl_dir)
