import re
import colorama
import time
import random

path = "code.ml2" # Switch to any moo-lang-2 file (.ml2) inside the folder.
debugmode = False

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
        while interpret(self.c):
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
            print(line)
            if not line.split(" ")[0] == "return":
                interpret(line)
            else:
                mo = interpret("".join(line.split(" ")[1:]))
                for p in self.param:
                    if p in variables:
                        variables.pop(p)
                for p in self.extravars:
                    if p in variables:
                        variables.pop(p)
                return mo

        for p in self.param:
            if p in variables:
                variables.pop(p)
        for p in self.extravars:
            if p in variables:
                variables.pop(p)


variables = {"pi":3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348,"moo":"all_praise_moo"}
typeroo = {}
functions = []
global_scope = 0
inside = []

def err_syntax(m):
    return colorama.Fore.RED + m + colorama.Fore.RESET

def is_name(s):
    return re.search(r"^[a-zA-Z_][a-zA-Z0-9_]*$",s) and s.upper() not in ["MOO","pi"]

def moocleanup():
    try:
        for var in typeroo:
            if not var in variables:
                typeroo.pop(var)
    except Exception:
        pass



def interpret(line):
    global variables,inside
    line = str(line).strip()
    if line.endswith(";"):
        line = line[:-1]
    if debugmode:
        print(line)

    makevar = re.search(r"\s*(\w+)\s*:\s*(\w+)\s*=\s*(\S+)\s*", line) 
    indexation = re.search(r"(.+)\[(.+)\]",line)
    out = re.search(r"console.out\((.+)\)",line)
    add = re.search(r"(.+)\+(.+)", line)
    removevar = re.search(r"rmv (.+)",line)
    sub = re.search(r"^\s*(\S+)\s*\-\s*(\S+)\s*$", line)
    mul = re.search(r"^\s*(\S+)\s*\*\s*(\S+)\s*$", line)
    div = re.search(r"^\s*(\S+)\s*/\s*(\S+)\s*$", line)
    eq  = re.search(r"^\s*(\S+)\s*\=\=\s*(\S+)\s*$", line)
    addeq  = re.search(r"^\s*(\S+)\s*\+=\s*(\S+)\s*$", line)
    subeq  = re.search(r"^\s*(\S+)\s*\-=\s*(\S+)\s*$", line)
    gr  = re.search(r"^\s*(\S+)\s*>\s*(\S+)\s*$", line)
    ls  = re.search(r"^\s*(\S+)\s*<\s*(\S+)\s*$", line)
    gre  = re.search(r"^\s*(\S+)\s*>=\s*(\S+)\s*$", line)
    lse  = re.search(r"^\s*(\S+)\s*<=\s*(\S+)\s*$", line)
    inputs = re.search(r"inp\[(.+)\]",line)
    no_t = re.search(r"not (.+)",line)
    ct = re.search(r"#(.+)#\[(.+)\]",line)
    autols = re.search(r"range\{(.+)\}",line)
    ifst = re.search(r"if \((.+)\) then \{",line)
    forloop = re.search(r"for (.+) in \((.+)\) \{",line)
    whileloop = re.search(r"while \((.+)\) do \{",line)
    funct = re.search(r"define (.+) with (.+) \{",line)
    wait_cmd = re.search(r"wait\((.+)\)", line)
    clear_cmd = re.search(r"clear\(\)", line)
    rand_cmd = re.search(r"rand\((.+),(.+)\)", line)
    len_cmd = re.search(r"len\((.+)\)", line)
    append_cmd = re.search(r"append\((.+),(.+)\)", line)
    remove_cmd = re.search(r"remove\((.+),(.+)\)", line)
    reverse_cmd = re.search(r"reverse\((.+)\)", line)
    exit_cmd = re.search(r"exit\(\)", line)
    type_cmd = re.search(r"type\((.+)\)", line)
    uppercase_cmd = re.search(r"uppercase\((.+)\)", line)
    lowercase_cmd = re.search(r"lowercase\((.+)\)", line)
    an_d = re.search(r"(.+) and (.+)",line)
    if out:
        print(interpret(out.group(1)))
        return interpret(out.group(1))
    if len(line) >= 2 and line[0] in ['"',"'"] and line[-1] in ['"',"'"]:
        return str(line[1:-1])
    elif makevar:
        if is_name(makevar.group(1).strip()):
            mooey = interpret(makevar.group(3))
            if isinstance(mooey,list):
                mooey = mooey[-1]


            variables[makevar.group(1).strip()] = eval(f"{makevar.group(2)}(\"{mooey}\")")
            
            typeroo[makevar.group(1).strip()] = makevar.group(2)
        else:
            print(f"Moo Error: {makevar.group(1)} \n{err_syntax('Name cannot be used as a variable')}")
            return "Terminate_*"
    elif removevar:
        if removevar.group(1) in variables:
            variables.pop(removevar.group(1))
    elif inputs:
        
        return input(interpret(inputs.group(1)))
    elif ifst:
        inside.append(Statement(interpret(ifst.group(1))))
    elif forloop:
        inside.append(Forl(forloop.group(1),interpret(forloop.group(2))))
    elif whileloop:
        inside.append(Whilel(whileloop.group(1)))
    elif funct:
        if is_name(funct.group(1)):
            inside.append(Function(funct.group(1),funct.group(2).split(",")))
    elif no_t:
        return not interpret(no_t.group(1))
    elif eq:
        print(interpret(eq.group(1)),interpret(eq.group(2)))
        return interpret(eq.group(1)) == interpret(eq.group(2))
    elif gr:
        return interpret(gr.group(1)) > interpret(gr.group(2))
    elif ls:
        return interpret(ls.group(1)) < interpret(ls.group(2))
    elif gre:
        return interpret(gre.group(1)) >= interpret(gre.group(2))
    elif lse:
        return interpret(lse.group(1)) <= interpret(lse.group(2))
    elif an_d:
        return interpret(an_d.group(1)) and interpret(an_d.group(2))
    elif ct:
        return eval(f"{ct.group(1)}({ct.group(2)})")
    elif indexation:
        return variables[interpret(indexation.group(1))][int(interpret(indexation.group(2)))]
    elif autols:
        x = []
        for i in range(int(interpret(autols.group(1).strip()))):
            x.append(i)
        return x
    elif subeq:
        variables[subeq.group(1)] -= eval(f"{typeroo[subeq.group(1)]}({interpret(subeq.group(2))})")
    elif addeq:
        variables[addeq.group(1)] += eval(f"{typeroo[addeq.group(1)]}({interpret(addeq.group(2))})")
    elif sub:
        return interpret(sub.group(1)) - interpret(sub.group(2))
    elif add:
        return interpret(add.group(1)) + interpret(add.group(2))
    elif div:
        return interpret(div.group(1)) / interpret(div.group(2))
    elif mul:
        return interpret(mul.group(1)) * interpret(mul.group(2))

    elif line in variables:
        return variables[line]
    elif line.startswith("$") and line[1:] in variables:
        return line[1:]
    
    if wait_cmd:
        time.sleep(float(interpret(wait_cmd.group(1))))
        return
    if clear_cmd:
        print("\033c", end="")
        return
    if rand_cmd:
        return random.randint(int(interpret(rand_cmd.group(1))), int(interpret(rand_cmd.group(2))))
    if len_cmd:
        return len(interpret(len_cmd.group(1)))
    if append_cmd:
        variables[append_cmd.group(1)].append(interpret(append_cmd.group(2)))
        return
    if remove_cmd:
        variables[remove_cmd.group(1)].pop(int(interpret(remove_cmd.group(2))))
        return
    if reverse_cmd:
        return interpret(reverse_cmd.group(1))[::-1]
    if exit_cmd:
        exit()
    if type_cmd:
        return str(type(interpret(type_cmd.group(1))).__name__)
    if uppercase_cmd:
        return interpret(uppercase_cmd.group(1)).upper()
    if lowercase_cmd:
        return interpret(lowercase_cmd.group(1)).lower()
    
    for name in functions:
        if name[0] in line:
            call = re.search(name[0]+r"\((.+)\)",line)
            if call:
                p = []
                for itex in call.group(1).split(","):
                    p.append(interpret(itex))
                sc = name[1].run(p)
                if type(sc) == list:
                    sc = sc[0]
                
                return sc
    
    moocleanup()

    return line



def work(txt:str):
        lnn = 1
        for line in open(txt,"r").read().splitlines():
            
            line = line.strip()
            if inside == [] or not isinstance(inside[0],Statement) and not isinstance(inside[0],Forl) and not isinstance(inside[0],Function) and not isinstance(inside[0],Whilel):
                try:
                    x = interpret(line)
                except Exception as e:
                    print(f"{colorama.Fore.GREEN + "Error at line" + colorama.Fore.RESET} {colorama.Fore.BLUE + str(lnn) + colorama.Fore.RESET}: {colorama.Fore.RED + str(e) + colorama.Fore.RESET}")
                    moocleanup()
                    return

            else:
                if len(inside) >= 1:
                    if isinstance(inside[0],Statement):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    elif isinstance(inside[0],Forl):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    elif isinstance(inside[0],Whilel):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            inside[-1].run()
                            inside.pop()
                    elif isinstance(inside[0],Function):
                        if line != "}":
                            inside[-1].add_line(line)
                        else:
                            functions.append((inside[-1].name,inside[-1]))
                            inside.pop()

            lnn += 1

rfke = time.time()

work(path)

print(f"Ran in {round(time.time() - rfke,4)} secs")
