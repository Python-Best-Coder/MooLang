import re
import colorama
import time
import random
import sys
from io import StringIO

path = "code.ml2"  # Switch to any moo-lang-2 file (.ml2) inside the folder.
debugmode = False

class Forl:
    def __init__(self, replacementvar, inside):
        self.var = replacementvar
        self.lines = []
        self.ins = inside

    def add_line(self, line):
        self.lines.append(line)

    def run(self):
        for x in self.ins:
            variables[self.var] = x
            for line in self.lines:
                interpret(line)
        if self.var in variables:
            variables.pop(self.var)

class Whilel:
    def __init__(self, condition):
        self.c = condition
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def run(self):
        while interpret(self.c):
            for line in self.lines:
                interpret(line)

class Statement:
    def __init__(self, condition):
        self.condition = condition
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def run(self):
        if interpret(self.condition):
            for line in self.lines:
                interpret(line)

class Function:
    def __init__(self, name, parameters):
        self.name = name
        self.param = parameters
        self.extravars = []
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)
        makevar = re.match(r"^\s*(\w+)\s*:\s*(\w+)\s*=\s*(.+)$", line)
        if makevar and is_name(makevar.group(1)):
            self.extravars.append(makevar.group(1))

    def run(self, param):
        if len(param) != len(self.param):
            raise ValueError(f"Function '{self.name}' expected {len(self.param)} arguments, got {len(param)}")
        for index, parameter in enumerate(self.param):
            variables[parameter] = param[index]
        for line in self.lines:
            if line.strip().startswith("return"):
                mo = interpret(" ".join(line.split()[1:]))
                self._cleanup()
                return mo
            interpret(line)
        self._cleanup()
        return None

    def _cleanup(self):
        for p in self.param + self.extravars:
            variables.pop(p, None)  # Safe removal

variables = {"pi": 3.141592653589793, "moo": "all_praise_moo"}
imports = []
typeroo = {}
functions = []
inside = []

def err_syntax(m):
    return colorama.Fore.RED + m + colorama.Fore.RESET

def is_name(s):
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", s)) and s.upper() not in ["MOO", "PI"]

def moocleanup():
    for var in list(typeroo.keys()):  # Use list to avoid runtime dict modification
        if var not in variables:
            typeroo.pop(var, None)

def interpret(line):
    global variables, inside
    line = str(line).strip()
    if line.endswith(";"):
        line = line[:-1]
    if debugmode:
        print(f"DEBUG: {line}")

    # Updated regex patterns
    makevar = re.match(r"^\s*(\w+)\s*:\s*(\w+)\s*=\s*(.+)$", line)
    indexation = re.match(r"^\s*(.+?)\[(.+?)\]$", line)
    out = re.match(r"^\s*console\.out\((.+)\)$", line)
    add = re.match(r"^\s*(.+?)\s*\+\s*(.+)$", line)
    removevar = re.match(r"^\s*rmv\s+(.+)$", line)
    useimp = re.match(r"^\s*(\w+)\.(.+)$", line)
    impo = re.match(r"^\s*use\s+<(.+)>$", line)
    sub = re.match(r"^\s*(.+?)\s*-\s*(.+)$", line)
    mul = re.match(r"^\s*(.+?)\s*\*\s*(.+)$", line)
    div = re.match(r"^\s*(.+?)\s*/\s*(.+)$", line)
    eq = re.match(r"^\s*(.+?)\s*==\s*(.+)$", line)
    addeq = re.match(r"^\s*(\w+)\s*\+=\s*(.+)$", line)
    subeq = re.match(r"^\s*(\w+)\s*-=\s*(.+)$", line)
    gr = re.match(r"^\s*(.+?)\s*>\s*(.+)$", line)
    ls = re.match(r"^\s*(.+?)\s*<\s*(.+)$", line)
    gre = re.match(r"^\s*(.+?)\s*>=\s*(.+)$", line)
    lse = re.match(r"^\s*(.+?)\s*<=\s*(.+)$", line)
    inputs = re.match(r"^\s*inp\[(.+)\]$", line)
    no_t = re.match(r"^\s*not\s+(.+)$", line)
    ct = re.match(r"^\s*#(.+)#\[(.+)\]$", line)
    autols = re.match(r"^\s*range\{(.+)\}$", line)
    ifst = re.match(r"^\s*if\s*\((.+)\)\s*then\s*\{$", line)
    forloop = re.match(r"^\s*for\s+(\w+)\s+in\s*\((.+)\)\s*\{$", line)
    whileloop = re.match(r"^\s*while\s*\((.+)\)\s*do\s*\{$", line)
    funct = re.match(r"^\s*define\s+(\w+)\s+with\s+(.+)\s*\{$", line)
    wait_cmd = re.match(r"^\s*wait\((.+)\)$", line)
    clear_cmd = re.match(r"^\s*clear\(\)$", line)
    rand_cmd = re.match(r"^\s*rand\((.+),(.+)\)$", line)
    len_cmd = re.match(r"^\s*len\((.+)\)$", line)
    append_cmd = re.match(r"^\s*append\((.+),(.+)\)$", line)
    remove_cmd = re.match(r"^\s*remove\((.+),(.+)\)$", line)
    reverse_cmd = re.match(r"^\s*reverse\((.+)\)$", line)
    exit_cmd = re.match(r"^\s*exit\(\)$", line)
    type_cmd = re.match(r"^\s*type\((.+)\)$", line)
    uppercase_cmd = re.match(r"^\s*uppercase\((.+)\)$", line)
    lowercase_cmd = re.match(r"^\s*lowercase\((.+)\)$", line)
    an_d = re.match(r"^\s*(.+?)\s+and\s+(.+)$", line)

    if out:
        result = interpret(out.group(1))
        print(result)
        return result
    if len(line) >= 2 and line[0] in ['"', "'"] and line[-1] in ['"', "'"]:
        return line[1:-1]
    elif impo:
        module = impo.group(1)
        imports.append(module)
        return module
    elif makevar:
        var_name = makevar.group(1)
        var_type = makevar.group(2)
        value = interpret(makevar.group(3))
        if not is_name(var_name):
            print(f"Moo Error: {var_name} \n{err_syntax('Invalid variable name')}")
            return "Terminate_*"
        if isinstance(value, str) and var_type in ["int", "float"]:
            value = eval(f"{var_type}({value.strip()})")
        variables[var_name] = value
        typeroo[var_name] = var_type
        return value
    elif removevar:
        var = removevar.group(1)
        variables.pop(var, None)
        typeroo.pop(var, None)
    elif inputs:
        return input(interpret(inputs.group(1)))
    elif ifst:
        inside.append(Statement(ifst.group(1)))
    elif forloop:
        inside.append(Forl(forloop.group(1), interpret(forloop.group(2))))
    elif whileloop:
        inside.append(Whilel(whileloop.group(1)))
    elif funct:
        if is_name(funct.group(1)):
            inside.append(Function(funct.group(1), [p.strip() for p in funct.group(2).split(",")]))
    elif no_t:
        return not interpret(no_t.group(1))
    elif eq:
        return interpret(eq.group(1)) == interpret(eq.group(2))
    elif gr:
        return interpret(gr.group(1)) > interpret(gr.group(2))
    elif ls:
        return interpret(ls.group(1)) < interpret(ls.group(2))
    elif gre:
        return interpret(gre.group(1)) >= interpret(gr.group(2))
    elif lse:
        return interpret(lse.group(1)) <= interpret(lse.group(2))
    elif an_d:
        return interpret(an_d.group(1)) and interpret(an_d.group(2))
    elif ct:
        return eval(f"{ct.group(1)}({ct.group(2)})")
    elif indexation:
        return variables[interpret(indexation.group(1))][int(interpret(indexation.group(2)))]
    elif autols:
        return list(range(int(interpret(autols.group(1)))))
    elif subeq:
        var = subeq.group(1)
        if var in variables:
            variables[var] -= interpret(subeq.group(2))
    elif addeq:
        var = addeq.group(1)
        if var in variables:
            variables[var] += interpret(addeq.group(2))
    elif sub:
        return interpret(sub.group(1)) - interpret(sub.group(2))
    elif add:
        return interpret(add.group(1)) + interpret(add.group(2))
    elif div:
        return interpret(div.group(1)) / interpret(div.group(2))
    elif mul:
        return interpret(mul.group(1)) * interpret(mul.group(2))
    elif wait_cmd:
        time.sleep(float(interpret(wait_cmd.group(1))))
    elif clear_cmd:
        print("\033c", end="")
    elif rand_cmd:
        return random.randint(int(interpret(rand_cmd.group(1))), int(interpret(rand_cmd.group(2))))
    elif len_cmd:
        return len(interpret(len_cmd.group(1)))
    elif append_cmd:
        variables[append_cmd.group(1)].append(interpret(append_cmd.group(2)))
    elif remove_cmd:
        variables[remove_cmd.group(1)].pop(int(interpret(remove_cmd.group(2))))
    elif reverse_cmd:
        return interpret(reverse_cmd.group(1))[::-1]
    elif exit_cmd:
        sys.exit(0)
    elif type_cmd:
        return str(type(interpret(type_cmd.group(1))).__name__)
    elif uppercase_cmd:
        return str(interpret(uppercase_cmd.group(1))).upper()
    elif lowercase_cmd:
        return str(interpret(lowercase_cmd.group(1))).lower()
    elif useimp:
        if useimp.group(1) in imports:
            old_stdout = sys.stdout
            new_stdout = StringIO()
            sys.stdout = new_stdout
            try:
                exec(f"import {useimp.group(1)}\nprint({useimp.group(1)}.{useimp.group(2)})")
                output = new_stdout.getvalue().strip()
                return output if output.isdigit() else output  # Return as int if numeric
            except Exception as e:
                print(f"Moo Error: {err_syntax(str(e))}")
                return "Terminate_*"
            finally:
                sys.stdout = old_stdout
        else:
            print(f"Moo Error: Module '{useimp.group(1)}' not imported")
            return "Terminate_*"
    elif line in variables:
        return variables[line]
    elif line.startswith("$") and line[1:] in variables:
        return line[1:]

    for name, func in functions:
        if re.match(rf"^{name}\((.*)\)$", line):
            call = re.match(rf"^{name}\((.*)\)$", line)
            params = [interpret(p.strip()) for p in call.group(1).split(",")] if call.group(1) else []
            return func.run(params)

    moocleanup()
    try:
        return eval(line)  # Fallback for simple expressions
    except:
        return line  # Return as-is if not interpretable

def work(txt: str):
    lnn = 1
    try:
        with open(txt, "r") as f:
            for line in f.read().splitlines():
                line = line.strip()
                if not line:
                    continue
                if inside:
                    if line == "}":
                        inside[-1].run()
                        inside.pop()
                    else:
                        inside[-1].add_line(line)
                else:
                    result = interpret(line)
                    if result == "Terminate_*":
                        return
                lnn += 1
    except FileNotFoundError:
        print(f"Moo Error: File '{txt}' not found")
    except Exception as e:
        print(f"{colorama.Fore.GREEN}Error at line {colorama.Fore.BLUE}{lnn}{colorama.Fore.RESET}: {err_syntax(str(e))}")

rfke = time.time()
work(path)
print(f"Ran in {round(time.time() - rfke, 4)} secs")
