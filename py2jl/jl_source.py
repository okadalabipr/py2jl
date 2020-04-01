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
include(\"name2idx/name2idx.jl\")\n\
using .Name2Idx\n\
\n\
include(\"param_const.jl\")\n\
include(\"initial_condition.jl\")\n\
include(\"differential_equation.jl\")\n\
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
"


def differential_equation_header2(vector_name,elements_num):
    return "    %s::Vector{Float64} = zeros(%s)\n" % (vector_name,elements_num)


def differential_equation_footer():
    return "\
end\
"

def observable_header():
    return 'const observables = [\n'

def observable_body():
    return '\
];\n\
\n\
function observables_index(observable_name::String)::Int\n\
\n\
    return findfirst(isequal(observable_name),observables)\n\
end\
'

def experimental_data_header():
    return '\
module Exp\n\
include("./observable.jl")\n\
\n\
experiments = Array{Dict{String,Array{Float64,1}},1}(undef, length(observables))\n\
standard_error = Array{Dict{String,Array{Float64,1}},1}(undef, length(observables))\n\
'

def simulation_header():
    return '\
module Sim\n\
include("./observable.jl")\n\
using ..Model\n\
\n\
using Sundials\n\
# using SteadyStateDiffEq\n\
const STEADY_STATE_EPS = 1e-6n\n\
\n\
'

def simulation_body1():
    return '\
simulations = Array{Float64,3}(\n\
    undef, length(observables), length(t), length(conditions)\n\
)\n\
function simulate!(p::Vector{Float64}, u0::Vector{Float64})\n\
    try\n\
'

def simulation_body2():
    return '\
        iter::Int8 = 0\n\
        while iter < 10\n\
            prob = ODEProblem(diffeq,u0,tspan,p)\n\
            sol = solve(\n\
                prob,CVODE_BDF(),\n\
                abstol=1e-9,reltol=1e-9,dtmin=1e-8,verbose=false\n\
            )\n\
            if all(abs.(sol.u[end] - u0) .< STEADY_STATE_EPS)\n\
                break\n\
            else\n\
                u0 .= sol.u[end]\n\
                iter += 1\n\
            end\n\
        end\n\
'

def simulation_body3():
    return '\n\
            @inbounds @simd for j in eachindex(t)\n\
'

def simulation_footer():
    return '\
            end\n\
        end\n\
    catch\n\
        return false\n\
    end\n\
end\n\
end # module\
'



def get_timepoint_header():
    return '\nfunction get_timepoint(obs_idx::Int)\n'

def get_timepoint_footer():
    return '\
    end\n\
end\n\
\n\
end # module\
'

def header():
    return '\
function search_parameter_index()::Tuple{Array{Int64,1},Array{Int64,1}}\n\
'

def search_idx_const_header():
    return '\
    # constant parameter\n\
    search_idx_const::Vector{Int} = [\n\
'

def search_idx_const_footer():
    return '\
    ]\n\
\n\
'

def search_idx_init_header():
    return '\
    # initial values\n\
    search_idx_init::Vector{Int} = [\n\
'

def search_idx_init_footer():
    return '\
    ]\n\
\n\
    return search_idx_const, search_idx_init\n\
end\n\
\n\
'

def get_search_region_header():
    return '\
\n\
function get_search_region()::Matrix{Float64}\n\
    p::Vector{Float64} = f_params()\n\
    u0::Vector{Float64} = initial_values()\n\
\n\
    search_idx::Tuple{Array{Int64,1},Array{Int64,1}} = search_parameter_index()\n\
\n\
    search_param = zeros(length(search_idx[1])+length(search_idx[2]))\n\
    for (i,j) in enumerate(search_idx[1])\n\
        @inbounds search_param[i] = p[j]\n\
    end\n\
    for (i,j) in enumerate(search_idx[2])\n\
        @inbounds search_param[i+length(search_idx[1])] = u0[j]\n\
    end\n\
\n\
    if any(x -> x == 0.0, search_param)\n\
        message::String = "search_param must not contain zero."\n\
        for (_, idx) in enumerate(search_idx[1])\n\
            if p[idx] == 0.0\n\
                error(\n\
                    @sprintf(\n\
                        "`C.%s` in search_idx_const: ", C.param_names[idx]\n\
                    ) * message\n\
                )\n\
            end\n\
        end\n\
        for (_, idx) in enumerate(search_idx[2])\n\
            if u0[idx] == 0.0\n\
                error(\n\
                    @sprintf(\n\
                        "`V.%s` in search_idx_init: ", V.var_names[idx]\n\
                    ) * message\n\
                )\n\
            end\n\
        end\n\
    end\n\
\n\
    search_region::Matrix{Float64} = zeros(2,length(p)+length(u0))\
\n\
'

def get_search_region_footer():
    return '\
    search_region = lin2log!(\n\
        search_idx,search_region,length(p),length(search_param)\n\
    )\n\
    return search_region\n\
\n\
end\
\n\
\n\
\n\
'


def lin2log():
    return '\
function lin2log!(search_idx::Tuple{Array{Int64,1},Array{Int64,1}}, search_region::Matrix{Float64},\n\
                    n_param_const::Int, n_search_param::Int)::Matrix{Float64}\n\
    for i=1:size(search_region,2)\n\
        if minimum(search_region[:,i]) < 0.0\n\
            message = "search_region[lb,ub] must be positive.\\n"\n\
            if i <= n_param_const\n\
                error(\n\
                    @sprintf(\n\
                        "`C.%s` ", C.param_names[i]\n\
                    ) * message\n\
                )\n\
            else\n\
                error(\n\
                    @sprintf(\n\
                        "`V.%s` ", V.var_names[i-n_param_const]\n\
                    ) * message\n\
                )\n\
            end\n\
        elseif minimum(search_region[:,i]) == 0.0 && maximum(search_region[:,i]) != 0.0\n\
            message = "lower_bound must be larger than 0.\\n"\n\
            if i <= n_param_const\n\
                error(\n\
                    @sprintf(\n\
                        "`C.%s` ", C.param_names[i]\n\
                    ) * message\n\
                )\n\
            else\n\
                error(\n\
                    @sprintf(\n\
                        "`V.%s` ", V.var_names[i-n_param_const]\n\
                    ) * message\n\
                )\n\
            end\n\
        elseif search_region[2,i] - search_region[1,i] < 0.0\n\
            message = "lower_bound < upper_bound\\n"\n\
            if i <= n_param_const\n\
                error(\n\
                    @sprintf(\n\
                        "`C.%s` ", C.param_names[i]\n\
                    ) * message\n\
                )\n\
            else\n\
                error(\n\
                    @sprintf(\n\
                        "`V.%s` ", V.var_names[i-n_param_const]\n\
                    ) * message\n\
                )\n\
            end\n\
        end\n\
    end\n\
\n\
    nonzero_idx::Vector{Int} = []\n\
    for i=1:size(search_region,2)\n\
        if search_region[:,i] != [0.0,0.0]\n\
            push!(nonzero_idx,i)\n\
        end\n\
    end\n\
    difference::Vector{Int} = collect(\n\
        symdiff(\n\
            Set(nonzero_idx),\n\
            Set(\n\
                append!(\n\
                    search_idx[1], n_param_const .+ search_idx[2]\n\
                )\n\
            )\n\
        )\n\
    )\n\
    if length(difference) > 0\n\
        for (i,j) in enumerate(difference)\n\
            if j <= n_param_const\n\
                print(\n\
                    @sprintf(\n\
                        "`C.%s`\\n", C.param_names[Int(j)]\n\
                    )\n\
                )\n\
            else\n\
                print(\n\
                    @sprintf(\n\
                        "`V.%s`\\n", V.var_names[Int(j)-n_param_const]\n\
                    )\n\
                )\n\
            end\n\
        end\n\
        error(\n\
            "Set these search_params in both search_idx_init and search_region."\n\
        )\n\
    end\n\
\n\
    search_region = search_region[:,nonzero_idx]\n\
\n\
    return log10.(search_region)\n\
end\
'
