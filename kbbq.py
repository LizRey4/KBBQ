# checks for correct data type
def typeCheck(var, val, rightType):
        try:
            val = rightType(val)
            s[var] = val
        except ValueError:
            wrongType = str(type(val)).split("'")[1]
            rightType = str(rightType).split("'")[1]
            print("ERROR: Expected a(n) " + rightType + ", instead got a(n) " + wrongType)
            quit()

# checks if variable has been defined
def varmap(var_name, s):
    if var_name in s:
        return s[var_name]
    else:
        print("ERROR: Variable referenced but has not been defined: " + var_name)
        quit()

# checks if condition has a valid format
def invalidCondition(line, s):
    operator = {"==", "!=", ">", "<", ">=", "<="}
    isOp = False
    for op in operator:
        if op in line:
            isOp = True
            break
    if isOp == False and line not in s:
            print("ERROR: Statement missing comparison operator: " + line)
            quit()

# checks if conditions are true or false
def conditionCheck(condition, s) -> bool:
    if condition in s:
        return s[condition]

    operation = {
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
        "<=": operator.le,
        "<": operator.lt
    }

    for symbol, op in operation.items():
        if symbol in condition:
            left, right = condition.split(symbol)

            left = evaluate(left, s)

            if right == "True" or right == "False":
                right = right.replace(" ","")
            else:   
                right = evaluate(right, s)

            return op(left, right)

# does all math and concatenation for variable values and conditions
def evaluate(val, s) -> int:
    expr = ""
    chars = val.split()
    typeCheck = chars[0]
    isStr = False

    # variables and bool
    if typeCheck.isalpha() or "_" in typeCheck:
        if typeCheck == "True":
            return True
        elif typeCheck == "False":
            return False
        
        else:
            term = varmap(typeCheck, s)
            if term == "True" or term == "False":
                return term
            elif str(term).isalpha() or term == "":
                isStr = True
            else:
                isStr = False

    # strings
    if "\"" in val or isStr == True:
        if "+" not in val:
            if isStr == True:
                return term
            else:
                expr = val.strip().replace("\"", "")
                return expr
        else:
            # val = val.replace(" ", "", 1)
            strings = val.split(" + ")
            fullStr = ""
            for string in strings:
                if "\"" in string:
                    string = string.strip().replace("\"", "")
                    fullStr += string
                else:
                    term = varmap(string, s)
                    fullStr += str(term)

        return fullStr

    # numbers (int, float, etc)
    for char in chars:
        if char.isalpha() or "_" in char:
            term = varmap(char, s)
            expr += str(term) + " "
        else:
            expr += char + " "
    
    # mathematical parser
    operators = {
        "*": (2, operator.mul),
        "/": (2, operator.truediv),
        "%": (2, operator.mod),
        "+": (1, operator.add),
        "-": (1, operator.sub)
    }

    output = []       # queue
    stack = []  
    index = expr.split()

    for i in index:
        try:
            output.append(float(i))
        except:
            if i in operators:
                while (stack and stack[-1] in operators and operators[i][0] <= operators[stack[-1]][0]):
                    output.append(stack.pop())

                stack.append(i)
            

    while stack:
        output.append(stack.pop())

    for i in output:
        if isinstance(i, (int, float)):
            stack.append(i)

        elif i in operators:
            y = stack.pop()
            x = stack.pop()

            result = operators[i][1](x,y)
            stack.append(result)
    
    if not stack:
        raise ValueError(f"Invalid expression: {val}")
    return stack[0]

class KBBQ:
    def __init__(self):
        self.grill = [
            [False, False],
            [False, False]
        ]

        self.grillFoods = {
            "0,0": (None, None),
            "0,1": (None, None),
            "1,0": (None, None),
            "1,1": (None, None)
        }

    def interpret(self, model, s):
        prev_stmt = None
        for stmt in model.stmts:

            # variable assignment and checking data types
            if stmt.__class__.__name__ == "Variable":
                val = evaluate(stmt.value, s)

                if stmt.type == "rare":               # rare(int)
                    typeCheck(stmt.var_name, val, int)
                    
                elif stmt.type == "medium_rare":      # medium_rare(float)
                    typeCheck(stmt.var_name, val, float)

                elif stmt.type == "medium":           # medium(str)
                    typeCheck(stmt.var_name, val, str)

                else:                                 # medium_well(bool)
                    if stmt.value != "True" and stmt.value != "False":
                        wrongType = str(type(val)).split("'")[1]
                        print("ERROR: Expected a bool, instead got a(n) " + wrongType)
                        quit()
                    s[stmt.var_name] = val

            # if statement
            if stmt.__class__.__name__ == "If":
                expr = stmt.condition

                if not expr == "True" and not expr == "False":
                    invalidCondition(expr, s)
                    expr = conditionCheck(expr, s)
                else:
                    if expr == "True":
                        expr = True
                    else:
                        expr = False

                if expr:
                    block = KBBQ()
                    block.interpret(stmt.block, s)

                prev_stmt_val = expr
            
            # if else
            if stmt.__class__.__name__ == "IfElse":
                if not prev_stmt.__class__.__name__ == "If" and not prev_stmt.__class__.__name__ == "IfElse":
                    print("ERROR: marinate statement cannot be used without a marinate or cook statement before")
                    quit()

                if prev_stmt_val == False:
                    expr = stmt.condition

                    if not expr == "True" and not expr == "False":
                        invalidCondition(expr, s)
                        expr = conditionCheck(expr, s)
                    else:
                        if expr == "True":
                            expr = True
                        else:
                            expr = False

                    if expr:
                        block = KBBQ()
                        block.interpret(stmt.block, s)

                    prev_stmt_val = expr

            # else
            if stmt.__class__.__name__ == "Else":
                if not prev_stmt.__class__.__name__ == "If" and not prev_stmt.__class__.__name__ == "IfElse":
                    print("ERROR: flip statement cannot be used without a marinate or cook statement before")
                    quit()

                if prev_stmt_val == False:
                    block = KBBQ()
                    block.interpret(stmt.block, s)

            # print
            if stmt.__class__.__name__ == "Print":
                val = evaluate(stmt.value, s)
                print(val)

            # while
            if stmt.__class__.__name__ == "While":
                expr = stmt.condition
                invalidCondition(expr, s)

                block = KBBQ()
                while conditionCheck(expr, s):
                    block.interpret(stmt.block, s)

            # food placement
            if stmt.__class__.__name__ == "FoodPlacement":
                x = stmt.xVal
                y = stmt.yVal

                if x != 1 and x != 0 or y != 1 and y != 0:
                    print("ERROR: This spot doesn't exist on the grill. Only put (0,0), (0,1), (1,0), or (1,1)")
                    quit()

                if self.grill[x][y] == True:
                    print("ERROR: This spot is already filled. Please place in an open spot or do a grill change")
                    quit()

                val = varmap(stmt.value, s)
        
                self.grill[x][y] = True
                self.grillFoods[str(x) + "," + str(y)] = (stmt.value, val)

                print("**************************")
                print(str(self.grillFoods["0,0"]) + ", " + str(self.grillFoods["0,1"]))
                print(str(self.grillFoods["1,0"]) + ", " + str(self.grillFoods["1,1"]))
                print("**************************")
                

            # grill change
            # all spots on grill have been used and now need a grill change
            if stmt.__class__.__name__ == "GrillChange":
                for row in range(len(self.grill)):           
                    for col in range(len(self.grill[row])):  
                        self.grill[row][col] = False

                for coordinate in self.grillFoods:
                    self.grillFoods[coordinate] = (None, None)

                print("**************************")
                print(str(self.grillFoods["0,0"]) + ", " + str(self.grillFoods["0,1"]))
                print(str(self.grillFoods["1,0"]) + ", " + str(self.grillFoods["1,1"]))
                print("**************************")

            prev_stmt = stmt

#main
import textx
import operator
from textx import metamodel_from_file

kbbq_mm = metamodel_from_file('kbbq.tx')
kbbq_model = kbbq_mm.model_from_file('p1.kbbq')

kbbq = KBBQ()
s = dict()
kbbq.interpret(kbbq_model, s)