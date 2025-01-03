import re
import random
import time

print("Initializing...")

with open(r"code.txt", encoding="utf-8") as f:
    data = f.read()


def generate_id():
    return "".join([str(random.randint(0,9)) for _ in range(10)])

unpacked = []
packed = []

class Bool:
    def __init__(self,value,inside=False):
        if value in ["true","false"]:
            self.value = True if value == "true" else False
        else:
            self.value = True
        self.inside = inside
        self.id = generate_id()
        unpacked.append(self)

class String:
    def __init__(self, value, inside=None):
        self.value = value
        self.inside = inside
        self.id = generate_id()
        unpacked.append(self)

class Float:
    def __init__(self,value,inside=None):
        self.inside = inside
        self.value = value
        self.id = generate_id()
        unpacked.append(self)

class Integer:
    def __init__(self, value, inside=None):
        self.value = value
        self.inside = inside
        self.id = generate_id()
        unpacked.append(self)

class List:
    def __init__(self, value_items, inside=None):
        self.value = value_items
        self.id = generate_id()
        self.inside = inside
        unpacked.append(self)      

class Variable:
    def __init__(self, value, name):
        self.value = value
        self.name = name
        packed.append(self)

class Function:
    def __init__(self,name:str,lines:list,parameters:list):
        self.name = name
        self.lines = lines
        self.parameters = parameters
        packed.append(self)

    def add_line(self,line):
        self.lines.append(line)

    def run(self,parameters):
        fixed_parameters = []
        for parameter in parameters:
            fixed_parameters.append(parameter)
        for line in self.lines:
            run = True
            for parameter in self.parameters:
                line = line.replace(parameter,fixed_parameters[self.parameters.index(parameter)]) 
                if line.startswith("func"):
                    run = False
            if run:
                evaluate(line)
class RangeLoop:
    def __init__(self,fr,to):
        self.range = [fr,to]
        self.id = generate_id()
        self.lines = []
        unpacked.append(self)
    
    def add_line(self, line):
        self.lines.append(line)
    
    def run(self):

        for _ in range(self.range[0],self.range[1]):

            for line in self.lines[1:]:  
                evaluate(line.strip())
class Statement:
    def __init__(self,statement):
        self.statement = statement
        self.id = generate_id()
        self.lines = []
        unpacked.append(self)
    
    def add_line(self, line):
        self.lines.append(line)
    
    def run(self):
        if evaluate(self.statement):
            for line in self.lines[1:]:
                evaluate(line)
    

def print_whole_object(object):
    if isinstance(object, List):
        l = []
        for obj in object.value:
            # If the object is a string, integer, or float, we can print it directly
            while not isinstance((x := print_whole_object(obj)),str) or not isinstance((x := print_whole_object(obj)),int) or not isinstance((x := print_whole_object(obj)),float) or not isinstance((x := print_whole_object(obj)),bool):
                if isinstance(x,str) or isinstance(x,int) or isinstance(x,float) or isinstance(x,list) or isinstance(x,bool):
                    break
                x = print_whole_object(obj)
            l.append(x)
        return l         
    if isinstance(object, String):
        return object.value
    if isinstance(object, Integer):
        return object.value
    if isinstance(object, Float):
        return object.value
    if isinstance(object, Bool):
        return object.value
    else:
        return None
    
    
        

def tokenize(item: str, inside=None):
    if not type(item).__name__ in ["String","Integer","List","Float","Bool"]:
        item = str(item)
        if item.startswith('[') and item.endswith(']'):
            l = List([])
            items = []
            depth = 0
            current = ""
            for char in item[1:-1]:
                if char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
                if char == ',' and depth == 0:
                    items.append(tokenize(current.strip(),l))
                    current = ""
                else:
                    current += char
            if current:  
                items.append(tokenize(current.strip(),l))

            l.value = items
            return l
        elif (x:=re.match(r"(-?(\d+)\.(\d+))",item)):
            return Float(float(x.group(1)),inside)
        elif re.match(r"^-?\d+$", item): 
            return Integer(int(item),inside)
        elif re.match(r"(\"|\').*\1", item):  
            return String(item[1:-1],inside)
        elif re.match(r"(true|false)",item):
            return Bool(item,inside)  
        else:
            return None
    else:
        return item

def display_tree(item, indent=0, superprint=False):
    if isinstance(item, String) and not item.inside or superprint:
        print("  " * indent + f"String ID {item.id}: \"{item.value}\"")
    elif isinstance(item, Integer) and not item.inside or superprint:
        print("  " * indent + f"Integer ID {item.id}: {item.value}")
    elif isinstance(item, List) and not item.inside or superprint:
        print("  " * indent + f"List ID {item.id}:")
        for sub_item in item.value:
            display_tree(sub_item, indent + 1, True)

def packenize():
    for item in unpacked:
        display_tree(item)

def multiply(digit1, digit2):
    # Ensure both are tokenized
    digit1 = tokenize(digit1) if not isinstance(digit1, (String, Integer, Float, Bool, List)) else digit1
    digit2 = tokenize(digit2) if not isinstance(digit2, (String, Integer, Float, Bool, List)) else digit2
    
    if not digit1 is None and not digit2 is None:
        if isinstance(digit1, String) and isinstance(digit2, String):
            return String(digit1.value * digit2.value)
        elif isinstance(digit1, Integer) and isinstance(digit2, Integer):
            return Integer(digit1.value * digit2.value)
        elif isinstance(digit1, Float) or isinstance(digit2, Float):
            return Float(float(digit1.value) * float(digit2.value))
        else:
            raise ValueError(f"Unsupported addition between {type(digit1).__name__} and {type(digit2).__name__}")


def add(digit1, digit2):
    # Ensure both are tokenized
    digit1 = tokenize(digit1) if not isinstance(digit1, (String, Integer, Float, Bool, List)) else digit1
    digit2 = tokenize(digit2) if not isinstance(digit2, (String, Integer, Float, Bool, List)) else digit2
    
    if not digit1 is None and not digit2 is None:
        if isinstance(digit1, String) and isinstance(digit2, String):
            return String(digit1.value + digit2.value)
        elif isinstance(digit1, Integer) and isinstance(digit2, Integer):
            return Integer(digit1.value + digit2.value)
        elif isinstance(digit1, Float) or isinstance(digit2, Float):
            return Float(float(digit1.value) + float(digit2.value))
        else:
            raise ValueError(f"Unsupported addition between {type(digit1).__name__} and {type(digit2).__name__}")

def subtr(digit1, digit2):
    digit1 = tokenize(digit1) if not isinstance(digit1, (String, Integer, Float, Bool, List)) else digit1
    digit2 = tokenize(digit2) if not isinstance(digit2, (String, Integer, Float, Bool, List)) else digit2

    if isinstance(digit1, Integer) and isinstance(digit2, Integer):
        return Integer(digit1.value - digit2.value)
    elif isinstance(digit1, Float) or isinstance(digit2, Float):
        return Float(float(digit1.value) - float(digit2.value))
    else:
        raise ValueError(f"Unsupported subtraction between {type(digit1).__name__} and {type(digit2).__name__}")

def divide(digit1, digit2):
    digit1 = tokenize(digit1) if not isinstance(digit1, (String, Integer, Float, Bool, List)) else digit1
    digit2 = tokenize(digit2) if not isinstance(digit2, (String, Integer, Float, Bool, List)) else digit2

    return Float(digit1/digit2)

def floor_div(digit1, digit2):
    digit1 = tokenize(digit1) if not isinstance(digit1, (String, Integer, Float, Bool, List)) else digit1
    digit2 = tokenize(digit2) if not isinstance(digit2, (String, Integer, Float, Bool, List)) else digit2

    return Integer(digit1//digit2)


def evaluate(expression:str,silent=False):
    expression = str(expression).strip()

    for var in packed:
        if type(var).__name__ == "Variable":
            if var.value != None:
                expression = expression.replace("$"+var.name,str(var.value))
        
    addition = re.search(r"(.+) \+ (.+)",str(expression))
    varsubtract = re.search(r"(.+)\-=(.+)",str(expression))
    varadd = re.search(r"(.+)\+=(.+)",str(expression))
    varind = re.search(r"(.+)\+\+",str(expression))
    varnoind = re.search(r"(.+)\-\-",str(expression))
    subtraction = re.search(r"(.+) \- (.+)",str(expression))
    multiplication = re.search(r"(.+)\*(.+)",str(expression))
    division = re.search(r"(.+)\/(.+)",str(expression))
    floor_division = re.search(r"(.+)&\/(.+)",str(expression))
    boolean = re.search(r"(true|false)",str(expression))
    condition = re.search(r"if \((.+?)\) \{",str(expression))
    reassign = re.search(r"reassign (.+) \-> (.+)",str(expression))
    end = re.search(r"end main",str(expression))
    functions = re.search(r"func (.+) \((.+?)\) \{",str(expression))
    rloops = re.search(r"rloop \((.+?) to (.+?)\) \{",str(expression))
    endindent = re.search(r"\}",str(expression))
    name = re.search(r"((([a-z]?)([A-Z]?))*) = (.+)",str(expression))
    instances = re.search(r"(\w+)\.(.+)$", str(expression))
    callfunc = re.search(r"(.+)\(\) <\- (.+)",str(expression))
    greater = re.search(r"(.+)>(.+)",str(expression))
    less = re.search(r"(.+)<(.+)",str(expression))
    greater_equal = re.search(r"(.+)>=(.+)",str(expression))
    less_equal = re.search(r"(.+)<=(.+)",str(expression))
    equal = re.search(r"(.+)==(.+)",str(expression))
    not_equal = re.search(r"(.+)!=(.+)",str(expression))
    one_line_if = re.search(r"if \((.+?)\) \{(.+)\}",str(expression))
    if one_line_if:
        if evaluate(one_line_if.group(1)):
            for line in one_line_if.group(2).split(";"):
                evaluate(line)
        return None
    if condition:
        return "if"
    if varsubtract:
        n = varsubtract.group(1).strip()
        v = varsubtract.group(2).strip()
        for var in packed:
            if var.name == n:
                var.value = evaluate(var.value).value - evaluate(v).value
                return var.value
        print("Errno 002: No variable to reassign.")
    if varadd:
        n = varsubtract.group(1).strip()
        v = varsubtract.group(2).strip()
        for var in packed:
            if var.name == n:
                var.value = evaluate(var.value).value + evaluate(v).value
                return var.value
        print("Errno 002: No variable to reassign.")
    if varind:
        n = varind.group(1).strip()

        for var in packed:
            if var.name == n:
                var.value = evaluate(var.value).value + 1
                return var.value
        print("Errno 002: No variable to reassign.")
    if varnoind:
        n = varnoind.group(1).strip()
        for var in packed:
            if var.name == n:
                var.value = evaluate(var.value).value - 1
                return var.value
        print("Errno 002: No variable to reassign.")
    if rloops:
        return ["rloop",rloops.group(1),rloops.group(2)]
    if equal or greater_equal or less_equal or greater or less:
        left = evaluate((equal or greater_equal or less_equal or greater or less).group(1).strip())
        right = evaluate((equal or greater_equal or less_equal or greater or less).group(2).strip())

        # Unwrap the values if they are custom objects
        left_value = left.value if isinstance(left, (Integer, Float, Bool)) else left
        right_value = right.value if isinstance(right, (Integer, Float, Bool)) else right

        # Perform the comparison based on the operator
        if equal:
            return left_value == right_value
        elif greater_equal:
            return left_value >= right_value
        elif less_equal:
            return left_value <= right_value
        elif greater and not "-" in expression:
            return left_value > right_value
        elif less and not "-" in expression:
            return left_value < right_value


    if not_equal:
        return evaluate(not_equal.group(1)) != evaluate(not_equal.group(2))
    if division:
        return divide(evaluate(division.group(1)), evaluate(division.group(2)))
    if floor_division:
        return floor_div(evaluate(floor_division.group(1)), evaluate(floor_division.group(2)))
    

    
    if boolean:
        return Bool(boolean.group(1)).value
    if callfunc:
        for func in packed:
            if func.name == callfunc.group(1):
                func.run(callfunc.group(2).split(","))
    if functions:
        return ["function",Function(functions.group(1),[],functions.group(2).split(","))]
    if reassign:
        n = reassign.group(1).strip()
        v = reassign.group(2).strip()
        
        for var in packed:
            if var.name == n:
                var.value = evaluate(v)
                return var.value
        print("Errno 002: No variable to reassign.")
    

    if endindent:
        return "endind"
    if end:
        return "end"
    if instances:
        

        main = instances.group(1)
        sub = instances.group(2)

        func = re.search(r"(.+)\(\) <\- (.*)",sub)


        if func:

            ins = []

            
            if main == "console":
                
                ins = ["out","newl"]
                if func.group(1) == ins[0]:
                    value1 = func.group(2)
                    if not silent:
                        print(print_whole_object(evaluate(value1)))
                elif func.group(1) == ins[1]:
                    if func.group(2) == "":
                        print("\n")
            if main == "debug":
                ins = ["vars"]
                if func.group(1) == ins[0]:
                    for var in packed:
                        print(var.name)                  
    if name:
        vname = name.group(1)
        value1 = name.group(5)
        if tokenize(value1) == None:
            while tokenize(value1) == None:
                value1 = evaluate(value1)
        if len(packed) != 0:
            for item in packed:
                if item.name == vname:
                    print("Error: reassign variable expected (reassign x -> x2)")
                    quit()
                    return None

        return Variable(value1,vname)
        
    if addition:
        value1 = addition.group(1)
        value2 = addition.group(2)
        if tokenize(value1) == None or tokenize(value2) == None:
            if tokenize(value1) == None:
                value1 = evaluate(value1)
            if tokenize(value2) == None:
                value2 = evaluate(value2)
        
        
        return add(tokenize(value1), tokenize(value2))
    elif subtraction:
        if not "<" in expression:
            value1 = subtraction.group(1)
            value2 = subtraction.group(2)
            
            if tokenize(value1) == None or tokenize(value2) == None:
                return subtr(tokenize(value1), tokenize(value2))
    elif multiplication:
        value1 = multiplication.group(1)
        value2 = multiplication.group(2)
        
        return multiply(tokenize(value1), tokenize(value2))
    return tokenize(expression)

    

def code(data:str):
    inside = []
    insidevalues = []
    for line in data.splitlines():
        x = evaluate(line,"function" in inside or "if" in inside)
        if type(x).__name__ == "list":
            if x[0] == "function":
                inside.append("function")
                insidevalues.append(x[1])
            if x[0] == "rloop":
                inside.append("rloop")
                insidevalues.append(RangeLoop(evaluate(x[1]).value,evaluate(x[2]).value))

                
        elif x == "if":
            inside.append("if")
            get_statement = re.search(r"if (.+) {",line)
            insidevalues.append(Statement(get_statement.group(1)))

        elif x == "end":
            break

        if x == "endind":
            if len(inside) + len(insidevalues) >= 2:
                if type(insidevalues[-1]).__name__ == "Statement":
                    insidevalues[-1].run()
                if type(insidevalues[-1]).__name__ == "RangeLoop":
                    insidevalues[-1].run()
                inside.pop()
                insidevalues.pop()
            
        if len(insidevalues) > 0:
            for value in insidevalues:
                value.add_line(line)

time_start = time.time()
code(data)
time_end = time.time()
print(f"Ran in {round(time_end-time_start,3)} seconds")
