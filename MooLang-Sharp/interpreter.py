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
        
class Whilel:
    def __init__(self,condition):  
        self.c = condition 
        self.lines = []

    def add_line(self,line):
        self.lines.append(line)

    def run(self):
        while True:
            if not interpret(self.c):
                break
            for line in self.lines:
                interpret(line)
   

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

class Function:
    def __init__(self,name,parameters):
        self.name = name
        self.param = parameters
        self.extravars = []
        self.lines = []
    
    def add_line(self,line):
        self.lines.append(line)
        makevar = re.search(r"\s*(\w+)\s*:\s*(\w+)\s*=\s*(\S+)\s*", line) 
        if makevar:
            if is_name(makevar.group(1).strip()):
                self.extravars.append(makevar.group(1).strip())

    def run(self,param):
        for index,parameter in enumerate(self.param):
            variables[parameter] = param[index]
        for line in self.lines:
            interpret(line)
        for p in self.param:
            variables.pop(p)
        for p in self.extravars:
            variables.pop(p)


variables = {}
functions = []
global_scope = 0
inside = []

def err_syntax(m):
    return colorama.Fore.RED + m + colorama.Fore.RESET

def is_name(s):
    return re.search(r"^[a-zA-Z_][a-zA-Z0-9_]*$",s)

def interpret(line):
    global variables,inside
    line = line.strip()

    makevar = re.search(r"\s*(\w+)\s*:\s*(\w+)\s*=\s*(\S+)\s*", line) 
    indexation = re.search(r"(.+)\[(.+)\]",line)
    out = re.search(r"console.out\((.+)\)",line)
    add = re.search(r"\s*(\S+)\s*\+\s*(\S+)\s*", line) 
    sub = re.search(r"\s*(\S+)\s*\-\s*(\S+)\s*", line)
    mul = re.search(r"\s*(\S+)\s*\*\s*(\S+)\s*", line)
    div = re.search(r"\s*(\S+)\s*/\s*(\S+)\s*", line)
    eq  = re.search(r"\s*(\S+)\s*==\s*(\S+)\s*", line)
    gr  = re.search(r"\s*(\S+)\s*\>\s*(\S+)\s*", line)
    ls  = re.search(r"\s*(\S+)\s*\<\s*(\S+)\s*", line)
    gre  = re.search(r"\s*(\S+)\s*\>=\s*(\S+)\s*", line)
    lse  = re.search(r"\s*(\S+)\s*\<=\s*(\S+)\s*", line)
    no_t = re.search(r"not (.+)",line)
    ct = re.search(r"(.+)#\((.+)\)",line)
    autols = re.search(r"range\{(.+)\}",line)
    ifst = re.search(r"if \((.+)\) then \{",line)
    forloop = re.search(r"for (.+) in \((.+)\) \{",line)
    whileloop = re.search(r"while \((.+)\) do \{",line)
    funct = re.search(r"define (.+) with (.+) \{",line)
    an_d = re.search(r"(.+) and (.+)",line)
    if out:
        print(interpret(out.group(1)))
        return interpret(out.group(1))
    elif makevar:
        if is_name(makevar.group(1).strip()):
            variables[makevar.group(1).strip()] = eval(f"{makevar.group(2)}({interpret(makevar.group(3))})")
        else:
            print(f"Moo Error: {makevar.group(1)} \n{err_syntax('Name cannot be used as a variable')}")
            return "Terminate_*"
    elif ifst:
        inside.append(Statement(interpret(ifst.group(1))))
    elif forloop:
        inside.append(Forl(forloop.group(1),interpret(forloop.group(2))))
    elif whileloop:
        inside.append(Whilel(whileloop.group(1)))
    elif funct:
        if is_name(funct.group(1)):
            inside.append(Function(funct.group(1),funct.group(2).split(",")))
    elif indexation:
        return variables[interpret(indexation.group(1))][int(interpret(indexation.group(2)))]
    elif autols:
        x = []
        for i in range(int(autols.group(1))):
            x.append(i)
        return x
        
    elif sub:
        return interpret(sub.group(1)) - interpret(sub.group(2))
    elif add:
        return interpret(add.group(1)) + interpret(add.group(2))
    elif div:
        return interpret(div.group(1)) / interpret(div.group(2))
    elif mul:
        return interpret(mul.group(1)) * interpret(mul.group(2))
    elif eq:
        return interpret(eq.group(1)) == interpret(eq.group(2))
    elif gr:
        return interpret(gr.group(1)) > interpret(gr.group(2))
    elif ls:
        return interpret(ls.group(1)) < interpret(ls.group(2))
    elif gre:
        return interpret(gre.group(1)) >= interpret(gre.group(2))
    elif lse:
        return interpret(lse.group(1)) <= interpret(lse.group(2))
    elif no_t:
        return not interpret(no_t.group(1))
    elif an_d:
        return interpret(an_d.group(1)) and interpret(an_d.group(2))
    elif line in variables:
        return variables[line]
    elif line.startswith("$") and line[1:] in variables:
        return line[1:]
    elif len(line) >= 2 and line[0] in ['"',"'"] and line[-1] in ['"',"'"]:
        return str(line[1:-1])
    for name in functions:
        if name[0] in line:
            call = re.search(name[0]+r"\((.+)\)",line)
            if call:
                p = []
                for itex in call.group(1).split(","):
                    p.append(interpret(itex))
                name[1].run(p)
                return name[1]
    if ct:
        return eval(f"{ct.group(1)}({ct.group(2)})")

    
    return line



def work(p):
    with open(p,"r") as file:
        for line in file.read().splitlines():
            line = line.strip()
            if inside == [] or not isinstance(inside[-1],Statement) and not isinstance(inside[-1],Forl) and not isinstance(inside[-1],Function) and not isinstance(inside[-1],Whilel):
                x = interpret(line)
            else:
                if len(inside) >= 1:
                    if isinstance(inside[-1],Statement):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    elif isinstance(inside[-1],Forl):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    elif isinstance(inside[-1],Whilel):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    elif isinstance(inside[-1],Function):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            functions.append((inside[-1].name,inside[-1]))
                            inside.pop()



            if x == "Terminate_*":
                break

work(path)
