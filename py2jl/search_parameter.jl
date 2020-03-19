function search_parameter_index()::Tuple{Array{Int64,1},Array{Int64,1}}
    # constant parameter
    search_idx_const::Vector{Int} = [
        C.PTEN,
        C.V10,
        C.Km10,
        #C.n10,
        C.V31,
        C.Km31,
        #C.n31,
        C.V57,
        C.Km57,
        #C.n57,
        C.KF31,
        #C.nF31,
    ]

    # initial values
    search_idx_init::Vector{Int} = [
        V.E1,
        V.E2,
        V.E3,
        V.E4,
        V.G,
        V.S,
        V.I,
        V.R,
        V.T,
        V.O,
        V.A,
        V.P2,
        V.Akt,
        V.RsD,
        V.Raf,
        V.MEK,
        #
        V.CREBn,
        V.ERKc,
        V.Elk1n,
        V.RSKc,
    ]

    return search_idx_const, search_idx_init
end


function get_search_region()::Matrix{Float64}
    p::Vector{Float64} = f_params()
    u0::Vector{Float64} = initial_values()

    search_idx::Tuple{Array{Int64,1},Array{Int64,1}} = search_parameter_index()

    search_param = zeros(length(search_idx[1])+length(search_idx[2]))
    for (i,j) in enumerate(search_idx[1])
        @inbounds search_param[i] = p[j]
    end
    for (i,j) in enumerate(search_idx[2])
        @inbounds search_param[i+length(search_idx[1])] = u0[j]
    end

    if any(x -> x == 0.0, search_param)
        message::String = "search_param must not contain zero."
        for (_, idx) in enumerate(search_idx[1])
            if p[idx] == 0.0
                error(
                    @sprintf(
                        "`C.%s` in search_idx_const: ", C.param_names[idx]
                    ) * message
                )
            end
        end
        for (_, idx) in enumerate(search_idx[2])
            if u0[idx] == 0.0
                error(
                    @sprintf(
                        "`V.%s` in search_idx_init: ", V.var_names[idx]
                    ) * message
                )
            end
        end
    end

    search_region::Matrix{Float64} = zeros(2,length(p)+length(u0))

    # Default: 0.1 ~ 10
    for (i, j) in enumerate(search_idx[1])
        search_region[1, j] = search_param[i] * 0.1  # lower bound
        search_region[2, j] = search_param[i] * 10.  # upper bound
    end

    # Default: 0.5 ~ 2
    for (i, j) in enumerate(search_idx[2])
        search_region[1, j+length(p)] =  search_param[i+length(search_idx[1])] * 0.1  # lower bound
        search_region[2, j+length(p)] =  search_param[i+length(search_idx[1])] * 10.  # upper bound
    end

    # search_region[:,C.param_name] = [lower_bound,upper_bound]
    # search_region[:,V.var_name+len(x)] = [lower_bound,upper_bound]

    search_region = lin2log!(
        search_idx,search_region,length(p),length(search_param)
    )
    return search_region

end


function lin2log!(search_idx::Tuple{Array{Int64,1},Array{Int64,1}}, search_region::Matrix{Float64},
                    n_param_const::Int, n_search_param::Int)::Matrix{Float64}
    for i=1:size(search_region,2)
        if minimum(search_region[:,i]) < 0.0
            message = "search_region[lb,ub] must be positive.\n"
            if i <= n_param_const
                error(
                    @sprintf(
                        "`C.%s` ", C.param_names[i]
                    ) * message
                )
            else
                error(
                    @sprintf(
                        "`V.%s` ", V.var_names[i-n_param_const]
                    ) * message
                )
            end
        elseif minimum(search_region[:,i]) == 0.0 && maximum(search_region[:,i]) != 0.0
            message = "lower_bound must be larger than 0.\n"
            if i <= n_param_const
                error(
                    @sprintf(
                        "`C.%s` ", C.param_names[i]
                    ) * message
                )
            else
                error(
                    @sprintf(
                        "`V.%s` ", V.var_names[i-n_param_const]
                    ) * message
                )
            end
        elseif search_region[2,i] - search_region[1,i] < 0.0
            message = "lower_bound < upper_bound\n"
            if i <= n_param_const
                error(
                    @sprintf(
                        "`C.%s` ", C.param_names[i]
                    ) * message
                )
            else
                error(
                    @sprintf(
                        "`V.%s` ", V.var_names[i-n_param_const]
                    ) * message
                )
            end
        end
    end

    nonzero_idx::Vector{Int} = []
    for i=1:size(search_region,2)
        if search_region[:,i] != [0.0,0.0]
            push!(nonzero_idx,i)
        end
    end
    difference::Vector{Int} = collect(
        symdiff(
            Set(nonzero_idx),
            Set(
                append!(
                    search_idx[1], n_param_const .+ search_idx[2]
                )
            )
        )
    )
    if length(difference) > 0
        for (i,j) in enumerate(difference)
            if j <= n_param_const
                print(
                    @sprintf(
                        "`C.%s`\n", C.param_names[Int(j)]
                    )
                )
            else
                print(
                    @sprintf(
                        "`V.%s`\n", V.var_names[Int(j)-n_param_const]
                    )
                )
            end
        end
        error(
            "Set these search_params in both search_idx_init and search_region."
        )
    end

    search_region = search_region[:,nonzero_idx]

    return log10.(search_region)
end