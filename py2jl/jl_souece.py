def make_name2idx_header():
    return "\
module Name2Idx\n\
\n\
export C, V\n\
\n\
include(\"parameters.jl\")\n\
include(\"variables.jl\")\n\
\n\
end # module\
"

def model_header():
    return "\
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


def parameters_header():
    return "\
module C\n\
\n\
const param_names = [\n\
"

def parameters_footer():
    return "\
]\n\
\n\
for (idx,name) in enumerate(param_names)\n\
    eval(Meta.parse(\"const $name = $idx\"))\n\
end\n\
\n\
const len_f_params = length(param_names)\n\
\n\
end  # module\
"

def variables_header():
    return "\
module V\n\
\n\
const var_names = [\n\
"

def variables_footer():
    return "\
]\n\
\n\
for (idx,name) in enumerate(var_names)\n\
    eval(Meta.parse(\"const $name = $idx\"))\n\
end\n\
\n\
const len_f_vars = length(var_names)\n\
\n\
end  # module\
"

def param_const_header():
    return "\
function f_params()::Vector{Float64}\n\
    p::Vector{Float64} = zeros(C.len_f_params)\n\
"

def param_const_footer():
    return "\
    return p\n\
end\
"

def initial_condition_header():
    return "\
function initial_values()::Vector{Float64}\n\
    u0::Vector{Float64} = zeros(V.len_f_vars)\n\
"

def initial_condition_footer():
    return "\
    return u0\n\
end\
"

def differential_equation_header1():
    return "\
function diffeq(du,u,p,t)\n\
    v::Vector{Float64} = zeros(\
"

def differential_equation_header2():
    return ")"

def differential_equation_footer():
    return "\
\n\
end\
"