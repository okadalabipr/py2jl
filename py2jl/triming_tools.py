def lines_triming(lines, space_num=4):

    lines = convert_comment_out(lines)
    lines = remove_backslash(lines)
    lines = normalize_blanks(lines, space_num)
    lines = replace_characters(lines)

    return lines


def remove_backslash(lines):
    for i, line in enumerate(lines):
        # processing exceptions
        if (line.find('param_names = [\\') != -1
                or line.find('var_names = [\\') != -1
                or line.find('\'len_f_params\'\\') != -1
                or line.find('\'len_f_vars\'\\') != -1
                ):
            lines[i] = lines[i].replace('\\', ' ')
        else:
            while(lines[i][-3:].find('\\\n') != -1):
                lines[i] = lines[i].rstrip().replace(
                    '\\', ' '
                ) + lines[i+1].lstrip()
                lines.pop(i+1)
    return lines


def normalize_blanks(lines, space_num):
    for i, line in enumerate(lines):
        lines[i] = line.replace('\t', '    ')
        if line.strip(' ') == '':
            lines[i] = '\n'

    for i, line in enumerate(lines):
        lines[i] = normalize_indent(line, space_num)

    return lines


def normalize_indent(line, space_num):
    indent = '    '
    indents = ''
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
    for i, line in enumerate(lines):
        rep_line = line

        if (rep_line.find('for ') != -1
                and rep_line.find(' in ')
                and rep_line.find(':') != -1
                ):
            rep_line = rep_line[:rep_line.find('for ')] + 'for (' + \
                rep_line[rep_line.find('for ')+4:rep_line.find(' in ')] + ')' + \
                rep_line[rep_line.find(' in '):]

        if (rep_line.find('if ') != -1
            or rep_line.find('elif ') != -1
            or rep_line.find('else') != -1
                or rep_line.find('for ') != -1) and rep_line.find(':') != -1:
            rep_line = rep_line.replace(':', '')

        rep_line = rep_line.replace(']:', ']')
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
    # print(end_lines)
    for i, end_line in enumerate(end_lines):
        ind = ''
        for j in range(end_line[1]):
            ind += '    '
        ind += 'end\n'
        lines.insert(end_line[0] + i, ind)
    # for i in range(len(lines)):
    #    print(lines[i])
    return lines


def search_end(lines):
    indents = []
    end_lines = []

    prev = 0
    bracket1 = 0
    bracket2 = 0
    bracket3 = 0

    # count not normalized indents
    for i, line in enumerate(lines):
        if line.strip() == '':
            ind = prev
            #print(i,' is blank line')
        elif bracket1 > 0 or bracket2 > 0 or bracket3 > 0:
            ind = prev
        else:
            c = 0
            ind = 0
            while(line[c] == ' '):
                c += 1
            ind = line[:c].count('    ')

            if (line.find('else') != -1
                    or line.find('elif') != -1
                    or line.find('elif') != -1
                    ):
                ind = ind + 1
            prev = ind

        # ditict bracket
        if line.count('(') - line.count(')') > 0:
            bracket1 += line.count('(') - line.count(')')
        else:
            bracket1 -= line.count(')') - line.count('(')
        if line.count('{') - line.count('}') > 0:
            bracket2 += line.count('{') - line.count('}')
        else:
            bracket2 -= line.count('}') - line.count('{')
        if line.count('[') - line.count(']') > 0:
            bracket3 += line.count('[') - line.count(']')
        else:
            bracket3 -= line.count(']') - line.count('[')

        indents.append(ind)

    # count normalized indents
    for i in range(len(lines)):
        if i > 0:
            diff = indents[i-1] - indents[i]
            if diff > 0:
                # processing blank
                j = 1
                while lines[i-j].strip() == '':
                    #print('line',i-j+2,'is blank')
                    j = j + 1
                #print('endline is ',i-j+1,indents[i-1]-1,lines[i-j])
                for k in range(diff):
                    end_lines.append([i-j+1, indents[i-1]-1-k])

            # processing the last of sentences
            if i == len(lines)-1:
                j = 0
                while indents[i] - indents[0] != j:
                    j = j + 1
                    end_lines.append([i, indents[i]-j])

    # for i,line in enumerate(lines):
    #     print(indents[i],line.rstrip())
    # print(end_lines)

    # for i,line in enumerate(lines):
    #    print(indents[i],line.replace('\n',''))
    return end_lines


def convert_comment_out(lines):
    count_single = 0
    count_double = 0
    for i, line in enumerate(lines):
        if line.find('\'\'\'') != -1:
            count_single += 1
        if count_single % 2 == 1:
            lines[i] = line.replace('\'\'\'', '#=')
        else:
            lines[i] = line.replace('\'\'\'', '=#')
    for i, line in enumerate(lines):
        if line.find('\"\"\"') != -1:
            count_double += 1
        if count_double % 2 == 1:
            lines[i] = line.replace('\"\"\"', '#=')
        else:
            lines[i] = line.replace('\"\"\"', '=#')
    return lines


def insert_after_indent(line, string):
    rep_line = string + line.lstrip(' ')
    for i in range(space_counter(line)):
        rep_line = ' ' + rep_line

    return rep_line


def indent_remover(line, num, space_num=4):
    if len(line) > 4*num:
        line = line[4*num:]
    else:
        line = '\n'

    return line


def cut_out_line(lines, keyword):
    for i, line in enumerate(lines):
        if line.replace(' ', '').find(keyword.replace(' ', '')) != -1:
            return line
    return ''


def cut_out_lines(lines, start_keyword='', end_keyword='', mode=0):
    # mode 0 : start is the last line including start_keyword of lines
    # mode 1 : start is the first line including start_keyword of lines

    start = -1
    end = -1
    escape = False
    find = False

    for i, line in enumerate(lines):
        line = line.replace(' ', '')
        if line.find(start_keyword.replace(' ', '')) != -1 and not escape:
            if start_keyword != '':
                start = i
                find = True
                if mode == 1:
                    escape = True
        elif line.find(end_keyword.replace(' ', '')) != -1:
            if find and end_keyword != '':
                end = i
                break

    if end == -1:
        return lines[start:]
    else:
        return lines[start:end]


def copy_list(line):
    if line.find('[:]') == -1:
        return line

    params = line[line.find('=')+1:line.find('[:]')].replace(' ', '')
    copy = line[:line.find('=')+1] + ' copy(' + params + \
        ')' + line[line.find('[:]')+3:]

    return copy


def list_adder(line):
    rep_line = line
    bra = -1
    ket = -1
    for i,letter in enumerate(line):
        if letter == '[':
            bra = i
        if letter == ']' or letter == ',':
            ket = i
            if bra < ket:
                if line[bra+1:ket].isnumeric():
                    added = str(int(line[bra+1:ket]) + 1)
                    rep_line = rep_line[:bra+1] + added +  line[ket:]
            bra = i
    return rep_line

            