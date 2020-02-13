def lines_triming(lines, space_num=4):

    lines = remove_backslash(lines)
    lines = normalize_blanks(lines,space_num)
    lines = replace_characters(lines)
    lines = convert_comment_out(lines)

    return lines


def remove_backslash(lines):
    for i,line in enumerate(lines):
        if line.find('param_names = [\\')!=-1 or line.find('var_names = [\\')!=-1 \
            or line.find('\'len_f_params\'\\') != -1 or line.find('\'len_f_vars\'\\') != -1:
            lines[i] = lines[i].replace('\\',' ')
    
        else:
            while(lines[i][-3:].find('\\\n') != -1):
                lines[i] = lines[i].rstrip().replace('\\',' ') + lines[i+1].lstrip()
                lines.pop(i+1)
    
    return lines


def normalize_blanks(lines,space_num):
    for i, line in enumerate(lines):
        lines[i] = line.replace('\t', '    ')
        if line.strip(' ') == '':
            lines[i] = '\n'

    for i, line in enumerate(lines):
        lines[i] = normalize_indent(line,space_num)

    return lines


def normalize_indent(line,space_num):
    indent='    '
    indents=''
    for i in range(space_counter(line)//space_num):
        indents += indent
    line = indents + line.lstrip(' ')
    return line


def space_counter(line):
    count = 0
    for i, char in enumerate(line):
        if char == ' ':
            count += 1
        else:
            break
    return count


def replace_characters(lines):
    for i,line in enumerate(lines):
        rep_line = line
        if (rep_line.find('if ') != -1
            or rep_line.find('elif ') != -1
            or rep_line.find('else ') != -1
            or rep_line.find('for ') != -1) \
            and rep_line.find(':') != -1:
            rep_line = rep_line.replace(':', '')

        rep_line = rep_line.replace('x[C.', 'p[C.')
        rep_line = rep_line.replace('y[V.', 'u[V.')
        rep_line = rep_line.replace('dydt[V.', 'du[V.')
        rep_line = rep_line.replace('y0[V.', 'u0[V.')
        rep_line = rep_line.replace('**', '^')
        rep_line = rep_line.replace('elif ', 'elseif ')
        rep_line = rep_line.replace('\'', '\"')

        lines[i] = rep_line
    return lines


def insert_end(lines):
    end_lines = search_end(lines)
    for i, end_line in enumerate(end_lines):
        ind = ''
        for j in range(end_line[1]):
            ind += '    '
        ind += 'end\n'
        lines.insert(end_line[0] + i, ind)
    # for i in range(len(lines)):
    #    print(lines[i])
    lines.append('end\n')
    return lines


def search_end(lines):
    indents = []
    end_lines = []

    prev = 0
    bracket1 = 0
    bracket2 = 0
    bracket3 = 0
    
    for i, line in enumerate(lines):
        if line.strip() == '':
            ind = prev
            #print(i,' is blank line')
        elif bracket1> 0 or bracket2> 0 or bracket3> 0:
            ind = prev
        else:
            c = 0
            ind = 0
            while(line[c]==' '):
                c+=1
            ind = line[:c].count('    ')

            if line.find('else') != -1 or line.find('elif') != -1:
                ind = ind + 1
            prev = ind

        if line.count('(') - line.count(')') > 0:
            bracket1 += line.count('(') - line.count(')')
        else:
            bracket1 -=  line.count(')') - line.count('(')
        if line.count('{') - line.count('}') > 0:
            bracket2 += line.count('{') - line.count('}')
        else:
            bracket2 -=  line.count('}') - line.count('{')
        if line.count('[') - line.count(']') > 0:
            bracket3 += line.count('[') - line.count(']')
        else:
            bracket3 -=  line.count(']') - line.count('[')
        indents.append(ind)

    for i in range(len(lines)):
        diff = indents[i-1] - indents[i]
        if diff > 0:
            j = 1
            while lines[i-j].strip() == '':
                #print('line',i-j+2,'is blank')
                j = j + 1
            #print('endline is ',i-j+1,indents[i-1]-1,lines[i-j])
            for k in range(diff):
                end_lines.append([i-j+1, indents[i-1]-1-k])
    # for i,line in enumerate(lines):
        # print(indents[i],line.rstrip())
    # print(end_lines)

    #for i,line in enumerate(lines):
    #    print(indents[i],line.replace('\n',''))
    return end_lines


def convert_comment_out(lines):
    count=0
    for i,line in enumerate(lines):
        if line.find('\'\'\'') != -1:
            count += 1
        if count%2 == 1:
            lines[i] = line.replace('\'\'\'','#=')
        else:
            lines[i] = line.replace('\'\'\'','=#')
    return lines