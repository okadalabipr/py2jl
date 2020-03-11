import os
import sys
import numpy as np

from biomass.model.name2idx import parameters as C
from biomass.model.name2idx import variables as V
from biomass.model.param_const import f_params
from biomass.model.initial_condition import initial_values

def search_parameter_index():

    # Write param index for optimization
    search_idx_const = np.array([\
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
        C.KF31\
        #C.nF31\
    ])

    # initialvalues
    search_idx_init= np.array([
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
        V.RSKc\
    ])

    return search_idx_const, search_idx_init


def get_search_region():
    x = f_params()
    y0 = initial_values()

    search_idx = search_parameter_index()

    if len(search_idx[0]) != len(set(search_idx[0])):
        print('Error: Duplicate param name.')
        sys.exit()
    elif len(search_idx[1]) != len(set(search_idx[1])):
        print('Error: Duplicate var name.')
        sys.exit()
    else:
        pass

    search_param = np.empty(len(search_idx[0])+len(search_idx[1]))
    for i,j in enumerate(search_idx[0]):
        search_param[i] = x[j]
    for i,j in enumerate(search_idx[1]):
        search_param[i+len(search_idx[0])] = y0[j]

    if np.any(search_param == 0.):
        print('Error: search_param must not contain zero.')
        sys.exit()

    search_region = np.zeros((2,len(x)+len(y0)))

    # Default: 0.1 ~ 10
    for i,j in enumerate(search_idx[0]):
        search_region[0,j] = search_param[i]*0.1 # lower bound
        search_region[1,j] = search_param[i]*10. # upper bound

    # Default: 0.5 ~ 2
    for i,j in enumerate(search_idx[1]):
        search_region[0,j+len(x)] = \
            search_param[i+len(search_idx[0])]*0.1 # lower bound
        search_region[1,j+len(x)] = \
            search_param[i+len(search_idx[0])]*10. # upper bound

    # search_region[:,C.param_name] = [lower_bound,upper_bound]
    # search_region[:,V.var_name+len(x)] = [lower_bound,upper_bound]

    search_region = lin2log(search_idx,search_region,len(x),len(search_param))

    return search_region


def lin2log(search_idx,search_region,n_param_const,n_search_param):
    for i in range(search_region.shape[1]):
        if np.min(search_region[:,i]) < 0.0:
            message = 'search_region[lb,ub] must be positive.'
            if i <= n_param_const:
                raise ValueError(
                    '"C.%s": '%(C.param_names[i]) + message
                )
            else:
                raise ValueError(
                    '"V.%s": '%(V.var_names[i-n_param_const]) + message
                )
        elif np.min(search_region[:,i]) == 0.0 and np.max(search_region[:,i]) != 0:
            message = 'lower_bound must be larger than 0.'
            if i <= n_param_const:
                raise ValueError(
                    '"C.%s": '%(C.param_names[i]) + message
                )
            else:
                raise ValueError(
                    '"V.%s": '%(V.var_names[i-n_param_const]) + message
                )
        elif search_region[1,i] - search_region[0,i] < 0.0:
            message = 'lower_bound < upper_bound'
            if i <= n_param_const:
                raise ValueError(
                    '"C.%s": '%(C.param_names[i]) + message
                )
            else:
                raise ValueError(
                    '"V.%s": '%(V.var_names[i-n_param_const]) + message
                )
    difference = list(
        set(np.where(np.any(search_region != 0.,axis=0))[0])^
        set(np.append(search_idx[0],n_param_const+search_idx[1]))
    )
    if len(difference) > 0:
        message = 'in both search_idx_const and search_region'
        for i,j in enumerate(difference):
            if j <= n_param_const:
                print(
                    'Set "C.%s" '%(C.param_names[int(j)]) + message
                )
            else:
                print(
                    'Set "V.%s" '%(V.var_names[int(j-n_param_const)]) + message
                )
        sys.exit()

    search_region = search_region[:,np.any(search_region != 0.,axis=0)]

    return np.log10(search_region)
