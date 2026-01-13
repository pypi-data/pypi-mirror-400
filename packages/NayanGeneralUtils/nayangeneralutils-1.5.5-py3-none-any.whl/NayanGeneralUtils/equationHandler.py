#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 11:09:16 2025

@author: nayandusoruth
"""

import sympy as sy
#from sympy import *
from sympy import init_printing
import matplotlib as plt
init_printing()
from IPython.display import display
import numpy as np
import pandas as pd

"""
This module is intended to make symbolic maths handling via the sympy library easier

sympy docs:
    https://docs.sympy.org/latest/tutorials/intro-tutorial/features.html

module wishlist:
    - Error propagation calculator
    - PDE handler?
    
    
sympy library recap/summary:
    - object types:
    - symbols/variables - x, y, z = symbols('x y z')
    - main "object" of sympy is "expression" - expression = function(symbols)
    - Eq object - Eq(expression1, expression2) is equivilant to expression1 = expression2
    - also has set object
    useful functions:
        - simplification functions - expand(), factor()
        - limit function - limit(expression, x, 0)
        - derivative function - diff(expression, x)
        - integral functions - integrate(expression, x) and integrate(expression, (x, lowerBound, upperBound))
    useful solver functions:
        - algebraic solver - solve(expression, x) - apparently solveset(expression, x, domain=S.reals)
        - ODE solver:
            y = function('y') 
            dsolve(Eq(differentials(y(t)), inhomogenousTerm), y(t))
    matrix methods:
        - can construct matrices, perform simple matrix operations (I.E, addition, multiplication...), perform complex operations (I.E, RREF, eigenvectors...)
    

"""
# ====================================================================================================================
# general utility functions
# ====================================================================================================================

# sympy expression summation - </verified/>
def sumExpressions(expressions):
    """utility function - sums sympy expressions together"""
    returnable = 0
    for i in expressions:
        returnable = returnable + i
    return returnable

# computes single term in error propagation series - </verified/>
def errorPropagationTerm(expression, variable):
    """Error propagation term function - computes error expression due to 'variable' in 'expression' and returns error term"""
    standardDeviation = sy.symbols(str(str(variable) + "_err"))
    errorTerm = (standardDeviation * expression.diff(variable))**2
    return errorTerm
    
# computes all error terms in expression as a function of all variables - </verified/>
def errorPropagate(expression, returnSymbols=False):
    """Error propagation function - returns list of all error propagation terms in an expression for all variables"""
    symbols = list(expression.free_symbols)
    expressions = np.array([errorPropagationTerm(expression, symbols[0])])
    
    for i in range(1, len(symbols)):
        expressions = np.append(expressions, errorPropagationTerm(expression, symbols[i]))

    if(returnSymbols):
        return expressions, symbols
    return expressions

# computes all error terms in equation rhs of al variables and returns terms as equations -</verified/>
def errorPropagateEqs(equation, returnSummation = False, returnSummationSqrt = False):
    """Wrapper for errorPropagate() function - returns error terms in equation 'f = expression' as equations 'f_Var_Err = errorTerm' - returnSummation also returns a summation equation 'f_err**2 = sum(f_var_err)'  """
    errorTerms, symbols = errorPropagate(equation.rhs, returnSymbols=True)
    
    # reformat errorTerms into equation object - LHS symbols keeps track of LHS symbols of errorEquations
    equations = np.array([])
    LHSsymbols = np.array([])
    for i in range(0,len(errorTerms)):
        LHSterm = sy.symbols(str(str(list(equation.lhs.free_symbols)[0]) + "_" + str(symbols[i]) + "_Err"))**2
        LHSsymbols = np.append(LHSsymbols, LHSterm)
        equations = np.append(equations, sy.Eq(LHSterm, errorTerms[i]))
        
    # return summation of f_err^2 = sum(errorEquations)
    if(returnSummation):
        LHSsummation = sy.symbols(str(str(equation.lhs) + "_err"))**2
        summationEq = sy.Eq(LHSsummation, sumExpressions(LHSsymbols))
        return equations, summationEq
    
    # return summation of f_err = sqrt(sum(errorEquations))
    if(returnSummationSqrt):
        LHSsummation = sy.symbols(str(str(equation.lhs) + "_err"))
        summationEq = sy.Eq(LHSsummation, sy.sqrt(sumExpressions(LHSsymbols)))
        return equations, summationEq
    return equations
    

# evaluates RHS of equation from dictionary of inputs - </verified/>
def evalEquation(equation, inputs, evalNumeric=False):
    """Evaluates rhs of a sympy equation of form 'f = expression' - inputs is a symbols:values dictionary - returns new dictionary of {f:value} - evalNumeric determines if result is exact algebraic or numeric value"""
    # get rhs expression and left hand symbol
    rhs = equation.rhs
    lhsSymbol = equation.lhs

    # substitute in all values 
    for symbol, value in inputs.items():
        rhs = rhs.subs(symbol, value)
     
    # convert to numeric if desired
    if(evalNumeric):
        rhs = rhs.evalf()
    
    # return
    return {lhsSymbol:rhs}


# ====================================================================================================================
# equation flow class
# ====================================================================================================================

# setup class for "series of equations?" when inputs of equations follow each other from some inputted measurements - measurement A -> Eq1, Eq2 -> Eq3 -> Eq4 inc error propagation
class equationFlow():
    # constructor - assumes equations are of form 'f = expression' - formatting as equation instead of expression so that each expression has a LHS symbol
    def __init__(self, equations, constants={}):
        # temp
        self.equations = equations
        self.constants = constants # dictionary {symbol:value} for any constant values in equations
        

    # utility method - goes through list of equations and finds free input variables into flow - </verified/>
    def freeVariables(self):
        """Utility method - goes through all self.equations and finds all 'free input variables' - these represent all necessary inputs for evaluation"""
        # get list of all variables in RHS of all equations
        rhsVariables = np.array([])
        
        for equation in self.equations:
            rhsVariables = np.append(rhsVariables, list(equation.rhs.free_symbols))
                    
        # get list of all variables in LHS of all equations
        fixedVariables = np.array([])
        
        # append LHS symbols to fixed variables
        for equation in self.equations:
            fixedVariables = np.append(fixedVariables, list(equation.lhs.free_symbols))
        
        # append self.constants to fixed variables
        fixedVariables = np.append(fixedVariables, list(self.constants.keys()))
        
        # remove fixed variables from all variables in order to find free variables
        indices = np.array([])
        for symbol in fixedVariables:
            indices = np.append(indices, np.where(rhsVariables == symbol))
        indices = indices.astype(int)
        
        # assign free variables
        self.freeVariables = np.delete(rhsVariables, indices)
    
    # utility method - add error propagation equations to self.equations - adding to main equation list to ensure error calculations occur correctly - </verified/>
    def propagateErrors(self):
        """Utility method - adds all error propagation terms to self.equations so that error propagation is part of 'equation flow'"""
        errorTerms = np.array([])
        
        # Compute error equations and respective summations for all equations
        for equation in self.equations:
            errorEquations, summation = errorPropagateEqs(equation, returnSummationSqrt=True)
            errorTerms = np.append(errorTerms, errorEquations)
            errorTerms = np.append(errorTerms, summation)
        
        # append errorTerms to equations
        self.equations = np.append(self.equations, errorTerms)
    
    # evaluation method - evaluates equations given inputs - </verified/>
    def evalEquations(self, inputs):
        """Given inputs, will evaluate all equations in flow and return dictionary of all values"""
        values = inputs
        values.update(self.constants) # add constants to values

        for equation in self.equations:
            values.update(evalEquation(equation, values)) # add results of equation evaluation to values

        return values

    # evaluation method - evaluates quations given a pandas dataframe of inputs - </verified/>
    def bulkEvalEquations(self, inputs):
        """Given a pandas dataframe of inputs, will return a pandas dataframe of all values - note input headers need to be sympy symbols"""
        # setup list of output dictionaries, evaluate over all rows
        outputs = np.array([])
        for i in range(0, inputs.shape[0]):
            outputs = np.append(outputs, self.evalEquations(inputs.iloc[1].to_dict()))
        
        # return outputs as new pandas dataframe
        return pd.DataFrame.from_dict(outputs.tolist())

    # printing method - pretty print all equations - </verified/>
    def prettyPrintEqs(self):
        """pprint() all equations in flow"""
        for equation in self.equations:
            sy.pprint(equation)
            
    # printing method - latex print all equations - </verified/>
    def latexPrintEqs(self):
        """latex print all equations in flow"""
        for equation in self.equations:
            print(sy.latex(equation))



# ====================================================================================================================
# general testing and experimentation 
# ====================================================================================================================

"""
x, y, z = sy.symbols('x y z')
f = sy.symbols('f')
a, b, c = sy.symbols('a b c')
expression = x**2+y**3 + z
equation = sy.Eq(f,expression)
inputs = {x:2,y:4,z:1,a:-1,b:2}

sy.pprint(equation)
value = evalEquation(equation, inputs, evalNumeric=False)
print(value)
"""


"""
a,b,c = sy.symbols('a b c')
x,y,z = sy.symbols('x y z')
d = sy.symbols('d')
d_err = sy.symbols('d_err')
x_err, y_err, z_err = sy.symbols('x_err y_err z_err')

a_imp = sy.symbols('a')
equationA = sy.Eq(a,x+y)
equationB = sy.Eq(b,a+z)
equationC = sy.Eq(c, b+d)

equations = np.array([equationA, equationB, equationC])
"""
"""
inputs = {x:2, y:3, z:1, x_err:0.5, y_err:0, z_err:0.1}


flow = equationFlow(equations, constants={d:2, d_err:0})
flow.propagateErrors()
print(flow.equations)
flow.freeVariables()
results = flow.evalEquations(inputs)
print(results)"""

"""
flow = equationFlow(equations, constants={d:2, d_err:0})

flow.propagateErrors()
flow.prettyPrintEqs()
flow.latexPrintEqs()
data = {x:[1,2,3], y:[2,2,2],z:[3,2,1], x_err:[0.5, 0.4, 0], y_err:[0, 0.1, 0.2], z_err:[0.1, 0.2, 0.05]}
inputsBulk = pd.DataFrame(data)

flow.bulkEvalEquations(inputsBulk)
#print(row)
results = flow.bulkEvalEquations(inputsBulk)
#print(results)
"""
# algebraic solver experiment
"""
x, a = sy.symbols('x a')
expression = x**2

equation = sy.Eq(expression, -1)
print(sy.solveset(equation, x, domain=sy.S.Complexes))
pprint(expression.diff(x))
"""
# linsolve experiments


# dsolve experiment
"""
x = sy.symbols('x')
f = sy.symbols('f', cls=sy.Function)
diffEq = sy.Eq(f(x).diff(x, x) + f(x).diff(x),0)
sy.pprint(diffEq)
#display(diffEq)
initialCond = {f(0):0, f(x).diff(x).subs(x,0):1}
sol = sy.dsolve(diffEq, f(x), ics=initialCond)
sy.pprint(sol)
#print(sol)
"""



# PDE seperation experiment
"""
x, y = symbols('x y')
f = symbols('f', cls=Function)
diffEq = Eq(f(x, y).diff(x)+f(x,y).diff(y),0)
pprint(diffEq)
X, Y = map(Function, 'XY')
ODEs = sy.solvers.pde.pde_separate(diffEq, f(x,y), [X(x),Y(y)])
print(ODEs)
c = symbols('c')
diffEq0 = Eq(ODEs[0], c)
diffEq1 = Eq(ODEs[1], c)
#pprint(diffEq0)
#pprint(diffEq1)
sol0 = sy.dsolve(diffEq0, X(x))
sol1 = sy.dsolve(diffEq1, Y(y))
#pprint(sol0)
#pprint(sol1)
#sol = dsolve(diffEq)
#pprint(sol)
#print(sol0.rhs)
fullSol = sol0.rhs * sol1.rhs
C_1=list(fullSol.free_symbols)[1]
A = symbols('A')
fullSol = fullSol.subs(C_1**2, A)
pprint(fullSol)
fullSol = simplify(fullSol)
pprint(fullSol)
"""

# PDE solver """experiment
"""
x, y = symbols('x y')
f = symbols('f',cls=Function)
u = f(x,y)
ux = u.diff(x)
uy = u.diff(y)
diffEq = Eq(ux+uy, u)
sol =sy.solvers.pde.pdsolve(diffEq, u)
print(sol)
"""

# matrix testing
"""
M = Matrix([[1,2],[2,1]])
N = Matrix([[0,1],[1,1]])
pprint(M)
print(M.eigenvals())
pprint( M.eigenvects())
"""
