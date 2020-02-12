def lines_triming(lines, space_num):
    #processing backslash
    for i,line in enumerate(lines):
        if line.find('param_names = [\\')!=-1 or line.find('var_names = [\\')!=-1 \
            or line.find('\'len_f_params\'\\')!=-1 or line.find('\'len_f_vars\'\\')!=-1:
            lines[i] = lines[i].replace('\\',' ')
        
        else:
            while(lines[i][-3:].find('\\\n')!=-1):
                lines[i] = lines[i].rstrip().replace('\\',' ') + lines[i+1].lstrip()
                lines.pop(i+1)

    #replace characters
    for i, line in enumerate(lines):
        #make br with space into simple br
        if line.strip(' ') == '':
            rep_line = '\n'
        else:
            rep_line = line

            if (rep_line.find('if ') != -1 or rep_line.find('elif ') != -1 or rep_line.find('else ') != -1) \
                and rep_line.find(':') != -1:
                rep_line = rep_line.replace(':', '')

            rep_line = rep_line.replace('x[C.', 'p[C.')
            rep_line = rep_line.replace('y[V.', 'u[V.')
            rep_line = rep_line.replace('dydt[V.', 'du[V.')
            rep_line = rep_line.replace('y0[V.', 'u0[V.')
            rep_line = rep_line.replace('**', '^')
            rep_line = rep_line.replace('elif ', 'elseif ')
            rep_line = rep_line.replace('\'', '\"')
            rep_line = rep_line.replace('\t', '    ')
            rep_line = normalize_indent(rep_line,space_num)

        lines[i] = rep_line
    return lines


def search_end(lines, space_num):
    indents = []
    end_lines = []

    prev = 0
    for i, line in enumerate(lines):
        if line.strip() == '':
            ind = prev
            #print(i,' is blank line')
        else:
            c=0
            ind = 0
            while(line[:3+4*c].find('    ')!=-1):
                ind += 1
                c+=1
            
            if line.find('else') != -1:
                ind = ind + 1
            prev = ind
        indents.append(ind)

    for i, _ in enumerate(lines):
        if indents[i] < indents[i-1] and i > 0:
            j = 1
            while lines[i-j].strip() == '':
                #print('line',i-j+2,'is blank')
                j = j + 1
            #rint('endline is ',i-j+1,indents[i-1]-1,lines[i-j])
            end_lines.append([i-j+1, indents[i-1]-1])
    # print(end_lines)
    return end_lines


def insert_end(lines, end_lines):
    for i, end_line in enumerate(end_lines):
        ind = ''
        for j in range(end_line[1]):
            ind += '    '
        ind += 'end\n'
        lines.insert(end_line[0] + i, ind)

    # for i in range(len(lines)):
    #    print(lines[i])
    return lines

def space_counter(line):
    counter = 0
    for j, char in enumerate(line):
        if char == ' ':
            counter += 1
        else:
            break
    return counter

def normalize_indent(line,space_num):
    indent='    '
    indents=''
    for i in range(space_counter(line)//space_num):
        indents += indent
    line = indents + line.strip(' ')
    return line