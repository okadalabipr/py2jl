def lines_triming(lines,space_num):
    for i ,line in enumerate(lines):
        if line.find('dydt =')!=-1:
            lines.pop(i)
            break
    for i,line in enumerate(lines):
        if line.strip(' ') == '':
            line = '\n'

        space_counter = 0
        for j,char in enumerate(line):
            if char == ' ':
                space_counter += 1
            else:
                break
        
        if space_counter != 0:
            line = line.strip(' ')
            for j in range(space_counter//space_num):
                line = '    ' + line


        if (line.find('if ')!=-1  or line.find('else ')!=-1 or line.find('else ')!=-1) \
        and line.find(':')!=-1:
            line = line.replace(':','')

        line = line.replace('x[C.','p[C.')
        line = line.replace('\t','    ')
        line = line.replace('y[V.','u[V.')
        line = line.replace('dydt[V.','du[V.')
        line = line.replace('**','^')
        line = line.replace('elif ','elseif ')
        line = line.replace('\'','\"')

        lines[i] = line

    return lines

## indentの数が４なら動作する、違うならエラー
def search_end(lines,space_num):
    indents=[]
    end_lines=[]

    prev=0
    for i,line in enumerate(lines):
        if line.strip() =='':
            ind = prev
            #print(i,' is blank line')
        else:
            ind = line.count('    ')
            if line.find('else')!=-1:
                ind = ind +1
            prev = ind
        indents.append(ind)

    for i in range(len(lines)):
        if indents[i] < indents[i-1] and i>0:
            j=1
            while lines[i-j].strip()=='':
                #print('line',i-j+2,'is blank')
                j=j+1
            #print('endline is ',i-j+1,indents[i-1]-1,lines[i-j])
            end_lines.append([i-j+1,indents[i-1]-1])
    #print(end_lines)
    return end_lines


def insert_end(lines,end_lines):
    for i,end_line in enumerate(end_lines):
        ind = ''
        for j in range(end_line[1]):
            ind += '    '
        ind += 'end\n'
        lines.insert(end_line[0]+i,ind)

    #for i in range(len(lines)):
    #    print(lines[i])
    return lines