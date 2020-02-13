import os
import re
from py2jl import triming_tools
from py2jl import jl_source_sp


def convert_search_parameter(jl_dir, py_dir):

    space_num=4
    with open(py_dir+'/search_parameter.py') as f:
        lines = f.readlines()

    search_parameter = jl_source_sp.header()
    search_parameter += jl_source_sp.search_idx_const_header()

    search_idx_const=[]
    is_keyword=False
    for i,line in enumerate(lines):
        key = line.replace(' ','')
        if key.find('search_idx_const=np.array([') != -1:
            is_keyword=True
        elif is_keyword:
            if line.find(']') != -1:
                break
            search_parameter += line.replace(',','')    
    search_parameter += jl_source_sp.search_idx_const_footer()

    search_parameter += jl_source_sp.get_search_region_header()

    lines = triming_tools.convert_comment_out(lines)
    lines = triming_tools.lines_triming(lines, space_num)
    lines = triming_tools.insert_end(lines)
    #for i,line in enumerate(lines):
    #    print(line.replace('\n',''))

    is_keyword = False
    for i,line in enumerate(lines):
        key = line.replace(' ','')
        if key.find('search_region=np.zeros') != -1:
            is_keyword=True
        elif is_keyword:
            line = line.replace('for i, j', 'for (i,j)')
            line = line.replace('np.','')
            if line.find('lin2log') != -1:
                break
            search_parameter += line

    search_parameter += jl_source_sp.get_search_region_footer()
    search_parameter += jl_source_sp.lin2log()

    with open(jl_dir+'/search_params.jl',mode='w')as f:
        f.write(search_parameter)

    