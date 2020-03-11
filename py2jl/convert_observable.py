import os
from py2jl import jl_source
from py2jl import triming_tools


def convert_observable(jl_dir, py_dir):
    os.makedirs(
        jl_dir, exist_ok=True
    )
    make_observable(jl_dir, py_dir)
    make_simulation(jl_dir, py_dir)
    make_experimental_data(jl_dir, py_dir)


def make_observable(jl_dir, py_dir):
    with open(py_dir+'/observable.py') as f:
        lines = f.readlines()

    observable = jl_source.observable_header()

    observables = triming_tools.cut_out_lines(lines,'observables=[',']')[1:]
    for i,line in enumerate(observables):
        observable += line.replace(',','').replace('\'','\"')

    observable += jl_source.observable_body()

    with open(jl_dir+'/observable.jl',mode='w')as f:
        f.write(observable)


def make_simulation(jl_dir, py_dir):
    with open(py_dir+'/observable.py') as f:
        lines = f.readlines()

    lines = triming_tools.cut_out_lines(lines,'class NumericalSimulation','class ExperimentalData')
    lines = triming_tools.lines_triming(lines)

    simulation = jl_source.simulation_header()

    line_tspan = triming_tools.cut_out_line(lines,'tspan=')
    line_tspan = line_tspan.replace('[','(').replace(']',')')
    line_tspan = triming_tools.indent_remover(line_tspan,1)

    line_t = triming_tools.cut_out_line(lines,'t=')

    simulation += triming_tools.insert_after_indent(line_tspan, 'const ')

    if line_t.find('/')!=-1:
        line_t = line_t[line_t.find('/')+1:]
        simulation += 'const t = collect(tspan[1]:1.0:tspan[end])./' + line_t + '\n'
    else:
        line_t = line_t[line_t.find(')')+1:]
        simulation += 'const t = collect(tspan[1]:1.0:tspan[end])' + line_t + '\n'

    line_conditions = triming_tools.cut_out_line(lines,'conditions=')

    simulation += triming_tools.indent_remover(
        triming_tools.insert_after_indent(line_conditions, 'const ') + '\n',1
    )

    simulation += jl_source.simulation_body1()

    conditions1 = triming_tools.cut_out_lines(lines,'def simulate(','enumerate(self.conditions)')


    conditions1_1 = triming_tools.cut_out_lines(conditions1,'def simulate(','_get_steady_state')[1:]
    conditions1_2 = triming_tools.cut_out_lines(conditions1,'y0','enumerate(self.conditions)')[1:]
    for i,line in enumerate(conditions1_1):
        simulation += line
    simulation += jl_source.simulation_body2()
    for i,line in enumerate(conditions1_2):
        simulation += line

    conditions2 = triming_tools.cut_out_lines(lines,'for(i,condition)','self._solveode')
    
    conditions2 = triming_tools.insert_end(conditions2)[:-2]

    for i,line in enumerate(conditions2):
        simulation += line.replace('self.','')
    
    simulation += jl_source.simulation_body3()

    get_timepoint = triming_tools.cut_out_lines(lines,'simulations[','class ExperimentalData',mode=1)
    for i,line in enumerate(get_timepoint):
        rep_line = line
        if rep_line.find('class ExperimentalData')!=-1:
            break
        rep_line = rep_line.replace('self.','')
        rep_line = rep_line.replace('observables.index','obs_idx')
        if rep_line.find('Y[:, ')!=-1:
            rep_line = rep_line.replace('Y[:, ','sol.u[j][')
        else:
            rep_line = rep_line.replace('Y[:,','sol.u[j][')
        if rep_line.find('simulations[')!=-1:
            rep_line = rep_line.replace(':,','j,')
        simulation += rep_line

    simulation += jl_source.simulation_footer()
    
    with open(jl_dir+'/simulation.jl',mode='w')as f:
        f.write(simulation)
    

def make_experimental_data(jl_dir, py_dir):
    with open(py_dir+'/observable.py') as f:
        lines = f.readlines()
    for i,line in enumerate(lines):
        if line.find('class ExperimentalData')!=-1:
            lines = lines[i:]
            break

    lines = triming_tools.replace_characters(lines)

    bracket = False
    for i,line in enumerate(lines):
        rep_line=line
        rep_line = rep_line.replace('observables.index','obs_idx')

        if 0 < rep_line.find('=') < rep_line.find('[') < rep_line.find(']'):
            rep_line = triming_tools.insert_after_indent(rep_line,'const ')

        key = line.replace(' ','')
        if key.find('={')!=-1:
            rep_line = rep_line.replace('{','Dict(')
            bracket = True
        if bracket:
            rep_line = rep_line.replace(':',' =>')
            if line.find('}')!=-1:
                rep_line = rep_line.replace('}',')')
                bracket = False
        lines[i]=rep_line

    experimental_data = jl_source.experimental_data_header()

    experiments = triming_tools.cut_out_lines(lines,'len(observables)','def get_timepoint',mode=1)[1:-1]
    for i,line in enumerate(experiments):
        experimental_data += triming_tools.indent_remover(line,1)
    
    experimental_data += jl_source.get_timepoint_header()

    get_timepoint = triming_tools.cut_out_lines(lines,'def get_timepoint','return')[1:]
    for i,line in enumerate(get_timepoint):
        rep_line = line
        rep_line = rep_line.replace('observables.index','obs_idx')
        if line.find('return')!=-1:
            break
        if line.replace(' ','').find('exp_t=self.')!=-1:
            rep_line = ''
            for j in range(triming_tools.space_counter(line)):
                rep_line += ' '
            rep_line += line.replace(' ','').replace('exp_t=self.','return ')
        experimental_data += triming_tools.indent_remover(rep_line,1)
    
    experimental_data += jl_source.get_timepoint_footer()

    with open(jl_dir+'/experimental_data.jl',mode='w')as f:
        f.write(experimental_data)