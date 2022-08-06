import re
from copy import copy

variables = {}
thetable = 'Undefined'
def sub_var(exp):
    var = variables
    for x in re.finditer('(?<!\w)([a-z]\w*)(?!\w)', exp):
        match = x.group()
        if match in var.keys():
            exp = re.sub(r'(?<!\w|["]){}(?!\w|["])'.format(match), var[match], exp)
    return exp

def normalize_bracket(exp):
    while '[' in exp:
        brac = [re.findall(r'(\[[^\]]*\])', exp)[0].strip(']').strip('['), re.findall(r'(\[[^\]]*\])', exp)[1].strip(']').strip('[')]
        match = ''.join([re.findall(r'(\[[^\]]*\])', exp)[0], re.findall(r'(\[[^\]]*\])', exp)[1]])
        brac[0] = brac[0].strip('_')
        brac[1] = brac[1].strip('_')
        brac[0] = eval(brac[0])
        brac[1] = eval(brac[1])
        if brac[0] == 'unsupported operand' or brac[1] == 'unsupported operand':
            return 'unsupported operand'
        if re.search(r'^\"[A-Z]+\"$', brac[0]) is None or re.search('^\d+$', brac[1]) is None:
            return 'unsupported operand'
        brac[0] = brac[0].strip('"')
        exp = exp.replace(match, brac[0] + brac[1])
    return exp

def sub_cell(exp):
    global thetable
    for x in re.finditer('(?<![-+/*])?([A-Z]+\d+)(?<![-+/*])?', exp):
        if thetable == 'Undefined':
            print('Error')
            exit(0)
        exp = re.sub('(?<![-+/*])?{}(?<![-+/*])?'.format(x.group(1)), Table.tables[thetable].get_cell(x.group(1)), exp)
    return exp

def eval(s):
    def calc(exp):
        res = ''
        flag = False
        for j in range(1, len(exp) - 1):
            if exp[j] == '*':
                exp = re.split(r'[*]', exp)
                res = int(exp[0]) * int(exp[-1])
                break

            elif exp[j] == '/':
                exp = re.split(r'[/]', exp)
                res = str(int(exp[0]) // int(exp[-1]))
                break

            elif exp[j] == '+':
                exp = re.split(r'[+]', exp)
                exp[0] = defType(exp[0])
                exp[-1] = defType(exp[-1])
                if type(exp[0]) is int and type(exp[-1]) is str:
                    if (exp[-1].upper() != exp[-1] or re.search(r'\d', exp[-1]) is not None):
                        res = 'unsup'
                        break
                    else:
                        exp[-1] = exp[-1].strip('"')
                        exp[-1] = s2n(exp[-1])
                elif type(exp[-1]) is int and type(exp[0]) is str:
                    if (exp[0].upper() != exp[0] or re.search(r'\d', exp[0]) is not None):
                        res = 'unsup'
                        break
                    else:
                        exp[0] = exp[0].strip('"')
                        exp[0] = s2n(exp[0])
                        flag = True
                res = exp[0] + exp[-1]
                if type(res) is str:
                    if exp[0][0] == '"' and exp[-1][0] == '"' and '"' in res.strip('"'):
                        res = '"' + re.sub(r'["]', '', res) + '"'

                if flag is True:
                    res = '"' + n2s(res) + '"'
                break

            elif exp[j] == '-':
                searchnegat = re.search(r'(["][-]\w+["])', s)
                if searchnegat is not None:
                    if j - 1 == searchnegat.span()[0]:
                        continue

                negat = False
                if exp[0] == '-':
                    exp = exp[1:]
                    negat = True
                exp = re.split(r'[-]', exp)

                if negat is True:
                    exp[0] = '-' + exp[0]

                exp[0] = defType(exp[0])
                exp[-1] = defType(exp[-1])

                if type(exp[0]) is str and type(exp[-1]) is str:
                    res = 'unsup'
                    break
                if type(exp[0]) is int and type(exp[-1]) is str:
                    if (exp[-1].upper() != exp[-1] or re.search(r'\d', exp[-1]) is not None):
                        res = 'unsup'
                        break
                    else:
                        exp[-1] = exp[-1].strip('"')
                        exp[-1] = s2n(exp[-1])
                elif type(exp[-1]) is int and type(exp[0]) is str:
                    if (exp[0].upper() != exp[0] or re.search(r'\d', exp[0]) is not None):
                        res = 'unsup'
                        break
                    else:
                        exp[0] = exp[0].strip('"')
                        exp[0] = s2n(exp[0])
                        flag = True

                res = exp[0] - exp[-1]
                if flag is True:
                    res = '"' + n2s(res) + '"'
                break

            if res is str:
                if exp[0][0] == '"' and exp[-1][0] == '"' and '"' in res.strip('"'):
                    res = '"' + re.sub(r'["]', '', res) + '"'
        return str(res)

    s = PerfectStr(s)
    s = sub_var(s)
    s = normalize_bracket(s)
    s = sub_cell(s)
    if 'None' in s:
        return 'None'

    while '*' in s or '/' in s:
        mul = re.findall(r"\w+[/*]\w+", s)
        if mul == []:
            return 'unsupported operand'
        for item in mul:
            s = s.replace(item, calc(item))
    if len(s) == 1:
        return s
    if s[0:2] == '"-' and re.search(r'\d', s[0]) is not None:
        sm = re.findall(r'["]?\w+[!?]?["]?[+-]["]?\w+[!?]?["]?', s)
        if sm != []:
            s = s.replace(sm[0], calc(sm[0]))
        else:
            s = 'unsup'
    else:
        while '+' in s or '-' in s[1:]:
            sm = re.findall(r'["]?\w+["]?[+-]["]?\w+["]?', s)
            if sm != []:
                s = s.replace(sm[0], calc(sm[0]))
            else:
                s = 'unsup'
                break
            if 'unsup' in s:
                break

    if 'unsup' in s:
        return ('unsupported operand')
    elif s[0] == '"':
        s = re.sub('_', ' ', s)
        s = re.sub(r'["]', '', s)
        return (f'"{s}"')
    else:
        return (s)

def defType(s):
    if re.search('[a-zA-z]+', s) is not None:
        s = str(s)
    if re.search('"', s) is not None:
        s = str(s)
    else:
        s = int(s)
    return s

def s2n(s):
    n = ord(s[-1]) - 65
    if len(s) > 1:
        s = s[:-1]
        i = -1
        while i >= -len(s):
            n += 26 ** (-i) * (ord(s[i]) - 64)
            i -= 1
    return int(n)

def n2s(a):
    n = int(a)
    s = chr(n % 26 + 65)
    n = n - (n % 26)
    if n == 0:
        return s
    else:
        while n >= 26:
            n //= 26
            r = n % 26
            if r == 0:
                s += 'Z'
                n -= 26
            else:
                s += chr(r - 1 + 65)
        return ''.join(reversed(s))

def PerfectStr(s):
    s = re.sub(r'(\s+)?[+](\s+)?', '+', s)
    s = re.sub(r'(\s+)?[/](\s+)?', '/', s)
    s = re.sub(r'(\s+)?[*](\s+)?', '*', s)
    s = re.sub(r'(\s+)?[-](\s+)?', '-', s)
    s = re.sub(r'(\s+)?[+](\s+)?("")?(\s+)?[+](\s+)?', '+', s)
    s = re.sub(r'\s', '_', s)
    s = re.sub(r'^[_]*', '', s)
    s = re.sub(r'("")\s?[+]?', '', s)
    s = re.sub(r'[+]$', '', s)
    return s


class Table:
    tables = {}

    def __init__(self, name, n, m):
        self.name = name
        self.n = n
        self.m = m
        self.mat = [['None' for _ in range(int(n))] for _ in range(int(m))]
        Table.tables[name] = self

    def set_cell(self, cell, value):
        mat = self.mat

        chr_num = re.split('(\d+)', cell)
        if s2n(chr_num[0]) < len(mat[0]) and int(chr_num[1]) <= len(mat):
            mat[int(chr_num[1]) - 1][s2n(chr_num[0])] = value
        else:
            print('Error')
            exit(0)

    def get_cell(self, exp):
        mat = self.mat
        chr_num = re.split('(\d+)', exp)
        if s2n(chr_num[0]) < len(mat[0]) and int(chr_num[1]) <= len(mat):
            mat_value = mat[int(chr_num[1]) - 1][s2n(chr_num[0])]
            return eval(mat_value)
        else:
            print('Error')
            exit(0)

    def display(self):
        matrix = self.mat
        mat = [['0' for _ in range(int(self.n) + 1)] for _ in range(int(self.m) + 1)]
        for i in range(1, int(self.n) + 1):
            mat[0][i] = n2s(i - 1)
        for j in range(1, int(self.m) + 1):
            mat[j][0] = str(j)
        for i in range(int(self.m)):
            for j in range(int(self.n)):
                mat[i + 1][j + 1] = eval(matrix[i][j])

        lens = [max(map(len, col)) for col in zip(*mat)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in mat]
        print('\n'.join(table))


def condition(bool_str):
    def BoolCompare(s):
        for x in re.finditer(r'(false|true)(\s)+(or|and)(\s)+(false|true)', s):
            if x.group(1) == 'false' and x.group(5) == 'true' or x.group(5) == 'false' and x.group(1) == 'true':
                if x.group(3) == 'or':
                    s = re.sub(x.group(), 'true', s)
                    return BoolCompare(s)
                if x.group(3) == 'and':
                    s = re.sub(x.group(), 'false', s)
                    return BoolCompare(s)
            else:
                s = re.sub(x.group(), x.group(1), s)
                return BoolCompare(s)
        return s

    exp_list = re.split('and|or', bool_str)
    exp_bool = []
    for i in exp_list:
        if '==' in i:
            x, y = i.split('==')
            x = eval(x.strip(' '))
            y = eval(y.strip(' '))
            x = defType(x)
            y = defType(y)
            if (x == 'unsupported operand' and y != 'unsupported operand') or (
                    y == 'unsupported operand' and x != 'unsupported operand'):
                print('unsupported operand')
                exit(0)
            if (type(x) is str and type(y) is int) or (type(x) is int and type(y) is str):
                print('typeError')
                exit(0)
            if x == y:
                exp_bool.append('true')
            else:
                exp_bool.append('false')

        elif '>' in i:
            x, y = i.split('>')
            x = eval(x.strip(' '))
            y = eval(y.strip(' '))
            x = defType(x)
            y = defType(y)

            if (x == 'unsupported operand' and y != 'unsupported operand') or (
                    y == 'unsupported operand' and x != 'unsupported operand'):
                print('unsupported operand')
                exit(0)
            if (type(x) is str and type(y) is int) or (type(x) is int and type(y) is str):
                print('typeError')
                exit(0)
            if x > y:
                exp_bool.append('true')
            else:
                exp_bool.append('false')

        elif '<' in i:
            x, y = i.split('<')
            x = eval(x.strip(' '))
            y = eval(y.strip(' '))
            x = defType(x)
            y = defType(y)
            if (x == 'unsupported operand' and y != 'unsupported operand') or (
                    y == 'unsupported operand' and x != 'unsupported operand'):
                print('unsupported operand')
                exit(0)
            if (type(x) is str and type(y) is int) or (type(x) is int and type(y) is str):
                print('typeError')
                exit(0)
            if x < y:
                exp_bool.append('true')
            else:
                exp_bool.append('false')
        else:
            exp_bool.append(i.strip())

    for i in range(len(exp_list)):
        bool_str = bool_str.replace(exp_list[i].strip(), exp_bool[i])
    return BoolCompare(bool_str)


def jump(start):
    global cmd
    cnt = 0
    end = start
    for x in cmd[start:]:
        end += 1
        if '{' in x:
            cnt += 1
        elif x == '}':
            cnt -= 1
            if cnt == 0:
                break
    return end



line = int(input())
cmd = []
jp = []
for i in range(line):
    command = input().strip()
    if '$' in command:
        comment = re.search(r'\s*\$\s*', command).span()[0]
        command = command[:comment]
    cmd.append(command)
    jp.append(-1)

pc = 0
while pc < len(cmd):
    x = cmd[pc]
    if jp[pc] != -1:
        pc = jp[pc]
        continue
    if len(x) == 0:
        pass
    elif re.search(r'create\(.+,\d+,\d+\)', x):
        for i in re.finditer(r'create\((.+),(\d+),(\d+)\)', x):
            Table(i.group(1), i.group(2), i.group(3))
    elif re.search(r'context\(.+\)', x):
        for i in re.finditer(r'context\((.+)\)', x):
            thetable = i.group(1)
            if thetable not in Table.tables:
                print('Error')
                exit(0)
    elif re.search(r'display\(.+\)', x):
        for i in re.finditer(r'display\((.+)\)', x):
            Table.tables[i.group(1)].display()

    elif re.search(r'setFunc\((.+),(.+)\)', x):
        for i in re.finditer(r'setFunc\((.+),(.+)\)', x):
            x = i.group(1)
            y = i.group(2)
            x = normalize_bracket(sub_var(x))
            Table.tables[thetable].set_cell(x, sub_var(y))

    elif re.search(r'print\(.+\)', x):
        for i in re.finditer(r'print\((.+)\)', x):
            if i.group(1) == '""':
                print(f'out:""')
            else:
                print(f'out:{eval(i.group(1))}')

    elif re.search(r'if\(.+\)\{', x):
        cont = False
        for i in re.finditer(r'if\((.+)\)\{', x):
            if condition(i.group(1)) == 'false':
                pc = jump(pc)
                cont = True
                break
        if cont:
            continue

    elif re.search(r'while\(.+\)\{', x):
        cont = False
        jp[jump(pc)-1] = pc
        for i in re.finditer(r'while\((.+)\)\{', x):
            if condition(i.group(1)) == 'false':
                pc = jump(pc)
                cont = True
                break
        if cont:
            continue

    elif x[0].isupper() or x[0] == "[":
        cell, value = x.split('=')
        cell = cell.strip()
        value = value.strip()
        cell = normalize_bracket(cell)
        value = eval(value)
        if thetable == 'Undefined':
            print('Error')
            exit(0)
        Table.tables[thetable].set_cell(cell, value)

    elif x[0].islower():
        var, value = x.split('=')
        var = var.strip()
        value = value.strip()
        variables[var] = eval(value)

    pc += 1
