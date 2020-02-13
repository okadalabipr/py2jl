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
    # initial values\n\
    search_idx_init::Vector{Int} = [\n\
        # V.(variableName)\n\
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
