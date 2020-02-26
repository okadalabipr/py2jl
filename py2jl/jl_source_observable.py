def observable_header():
    return 'const observables = [\n'

def observable_body():
    return '\
];\n\
\n\
function obs_idx(observable_name::String)::Int\n\
\n\
    return findfirst(isequal(observable_name),observables)\n\
end\n\
\n\
function diff_sim_and_exp(sim_matrix::Matrix{Float64},exp_dict::Dict{String,Array{Float64,1}},\n\
                            exp_timepoint::Vector{Float64},conditions::Vector{String};\n\
                            sim_norm_max::Float64,exp_norm_max::Float64)\n\
    sim_result::Vector{Float64} = []\n\
    exp_result::Vector{Float64} = []\n\
    \n\
    for (i,condition) in enumerate(conditions)\n\
        append!(sim_result,sim_matrix[Int.(exp_timepoint.+1),i])\n\
        append!(exp_result,exp_dict[condition])\n\
    end\n\
\n\
    return (sim_result./sim_norm_max, exp_result./exp_norm_max)\n\
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
using SteadyStateDiffEq\n\
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
        prob = ODEProblem(diffeq,u0,(0.0,Inf),p)\n\
        prob = SteadyStateProblem(prob)\n\
        sol = solve(prob,DynamicSS(CVODE_BDF()),abstol=1e-9,reltol=1e-9,dt=1.0)\n\
        u0 = sol.u\n\
'

def simulation_body3():
    return '\n\
            prob = ODEProblem(diffeq,u0,tspan,p)\n\
            sol = solve(\n\
                prob,CVODE_BDF(),saveat=1.0,dtmin=1e-8,\n\
                abstol=1e-9,reltol=1e-9,verbose=false\n\
            )\n\
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
    return '\nfunction get_timepoint(observalbe::Int)\n'

def get_timepoint_footer():
    return '\
    end\n\
end\n\
\n\
end # module\
'

