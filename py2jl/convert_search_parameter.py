import os
import re
from py2jl import triming_tools
from py2jl import jl_source


def convert_search_parameter(jl_dir, py_dir):

    space_num=4
    with open(py_dir+'/search_parameter.py') as f:
        lines = f.readlines()

    search_parameter = jl_source.header()

    search_parameter += jl_source.search_idx_const_header()
    search_idx_const = triming_tools.cut_out_lines(lines, 'search_idx_const=np.array([',']')[1:]
    for i,line in enumerate(search_idx_const):
        search_parameter += line
    search_parameter += jl_source.search_idx_const_footer()

    search_parameter += jl_source.search_idx_init_header()
    search_idx_init = triming_tools.cut_out_lines(lines, 'search_idx_init',']')[1:]
    for i,line in enumerate(search_idx_init):
        search_parameter += line
    search_parameter += jl_source.search_idx_init_footer()

    search_parameter += jl_source.get_search_region_header()

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

    search_parameter += jl_source.get_search_region_footer()
    search_parameter += jl_source.lin2log()

    with open(jl_dir+'/search_parameter.jl',mode='w')as f:
        f.write(search_parameter)

    