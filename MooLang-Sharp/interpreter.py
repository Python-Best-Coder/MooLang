import re
import colorama

path = "code.ml2" # Switch to any moo-lang-2 file (.ml2) inside the folder.

class Forl:
    def __init__(self,replacementvar,inside):
        self.var = replacementvar     
        self.lines = []
        self.ins = inside

    def add_line(self,line):
        self.lines.append(line)

    def run(self):
        
        for x in self.ins:
           variables[self.var] = x
           for line in self.lines:
                interpret(line)
        variables.pop(self.var)
        

class Statement:
    def __init__(self,condition):
        self.condition = condition
        self.lines = []
    
    def add_line(self,line):
        self.lines.append(line)

    def run(self):
        if interpret(self.condition):
            for line in self.lines:
                interpret(line)


variables = {}
global_scope = 0
inside = []

def err_syntax(m):
    return colorama.Fore.RED + m + colorama.Fore.RESET

def is_name(s):
    return re.search(r"^[a-zA-Z_][a-zA-Z0-9_]*$",s)

def interpret(line):
    global variables,inside

    makevar = re.search(r"(.+): (.+) = (.+)",line)
    indexation = re.search(r"(.+)\[(.+)\]",line)
    out = re.search(r"console.out\((.+)\)",line)
    sub = re.search(r"(.+)-(.+)",line)
    add = re.search(r"(.+)\+(.+)",line)
    mul = re.search(r"(.+)\*(.+)",line)
    div = re.search(r"(.+)\/(.+)",line)
    eq = re.search(r"(.+) == (.+)",line)
    ifst = re.search(r"if (.+) then \{",line)
    forloop = re.search(r"for (.+) in (.+) \{",line)
    if out:
        print(interpret(out.group(1)))
    elif makevar:
        if is_name(makevar.group(1)):
            variables[makevar.group(1)] = eval(f"{makevar.group(2)}({interpret(makevar.group(3))})")
        else:
            print(f"Moo Error: {makevar.group(2)} \n{err_syntax('Name cannot be used as a variable')}")
            return "Terminate_*"
    elif indexation:
        return variables[interpret(indexation.group(1))][int(interpret(indexation.group(2)))]
    
    elif sub:
        return int(interpret(sub.group(1))) - int(interpret(sub.group(2)))
    elif add:
        return int(interpret(sub.group(1))) + int(interpret(sub.group(2)))
    elif mul:
        return int(interpret(sub.group(1))) / int(interpret(sub.group(2)))
    elif div:
        return int(interpret(sub.group(1))) * int(interpret(sub.group(2)))
    elif eq:
        return interpret(eq.group(1)) == interpret(eq.group(2))
    elif ifst:
        inside.append(Statement(interpret(ifst.group(1))))
    elif forloop:
        inside.append(Forl(forloop.group(1),interpret(forloop.group(2))))
    elif line in variables:
        return variables[line]
    elif line.startswith("$") and line[1:] in variables:
        return line[1:]
    elif len(line) >= 2 and line[0] in ['"',"'"] and line[-1] in ['"',"'"]:
        return str(line[1:-1])
    
    return line



def work(p):
    with open(p,"r") as file:
        for line in file.read().splitlines():
            if inside == [] or not isinstance(inside[-1],Statement) and not isinstance(inside[-1],Forl):
                x = interpret(line)
            else:
                if len(inside) >= 1:
                    if isinstance(inside[-1],Statement):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    if isinstance(inside[-1],Forl):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()


            if x == "Terminate_*":
                break

work(path)
