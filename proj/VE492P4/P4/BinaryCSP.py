# Hint: from collections import deque
from Interface import *
from queue import Queue


# = = = = = = = QUESTION 1  = = = = = = = #


def consistent(assignment, csp, var, value):
    """
    Checks if a value assigned to a variable is consistent with all binary constraints in a problem.
    Do not assign value to var.
    Only check if this value would be consistent or not.
    If the other variable for a constraint is not assigned,
    then the new value is consistent with the constraint.

    Args:
        assignment (Assignment): the partial assignment
        csp (ConstraintSatisfactionProblem): the problem definition
        var (string): the variable that would be assigned
        value (value): the value that would be assigned to the variable
    Returns:
        boolean
        True if the value would be consistent with all currently assigned values, False otherwise
    """
    # TODO: Question 1
    for constraint in csp.binaryConstraints:
        if constraint.affects(var):
            other_variable = constraint.otherVariable(var)
            if other_variable in assignment.assignedValues.keys() \
                    and not constraint.isSatisfied(value, assignment.assignedValues[other_variable]):
                return False
    return True


def recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod):
    """
    Recursive backtracking algorithm.
    A new assignment should not be created.
    The assignment passed in should have its domains updated with inferences.
    In the case that a recursive call returns failure or a variable assignment is incorrect,
    the inferences made along the way should be reversed.
    See maintainArcConsistency and forwardChecking for the format of inferences.

    Examples of the functions to be passed in:
    orderValuesMethod: orderValues, leastConstrainingValuesHeuristic
    selectVariableMethod: chooseFirstVariable, minimumRemainingValuesHeuristic
    inferenceMethod: noInferences, maintainArcConsistency, forwardChecking

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
        orderValuesMethod (function<assignment, csp, variable> returns list<value>):
            a function to decide the next value to try
        selectVariableMethod (function<assignment, csp> returns variable):
            a function to decide which variable to assign next
        inferenceMethod (function<assignment, csp, variable, value> returns set<variable, value>):
            a function to specify what type of inferences to use
    Returns:
        Assignment
        A completed and consistent assignment. None if no solution exists.
    """
    # TODO: Question 1
    if assignment.isComplete():
        return assignment
    var = selectVariableMethod(assignment, csp)
    if var is None:
        return assignment
    for value in orderValuesMethod(assignment, csp, var):
        if consistent(assignment, csp, var, value):
            inferences = inferenceMethod(assignment, csp, var, value)
            if inferences is not None:
                assignment.assignedValues[var] = value
                result = \
                    recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
                if result is not None:
                    return result

                assignment.assignedValues[var] = None
                for variable, inference_value in inferences:
                    assignment.varDomains[variable].add(inference_value)
    return None


def eliminateUnaryConstraints(assignment, csp):
    """
    Uses unary constraints to eleminate values from an assignment.

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
    Returns:
        Assignment
        An assignment with domains restricted by unary constraints. None if no solution exists.
    """
    domains = assignment.varDomains
    for var in domains:
        for constraint in (c for c in csp.unaryConstraints if c.affects(var)):
            for value in (v for v in list(domains[var]) if not constraint.isSatisfied(v)):
                domains[var].remove(value)
                # Failure due to invalid assignment
                if len(domains[var]) == 0:
                    return None
    return assignment


def chooseFirstVariable(assignment, csp):
    """
    Trivial method for choosing the next variable to assign.
    Uses no heuristics.
    """
    for var in csp.varDomains:
        if not assignment.isAssigned(var):
            return var


# = = = = = = = QUESTION 2  = = = = = = = #


def minimumRemainingValuesHeuristic(assignment, csp):
    """
    Selects the next variable to try to give a value to in an assignment.
    Uses minimum remaining values heuristic to pick a variable. Use degree heuristic for breaking ties.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        the next variable to assign
    """
    nextVar = None
    domains = assignment.varDomains

    # TODO: Question 2
    selections_dict = {}
    for var, value in domains.items():
        if not assignment.isAssigned(var):
            selections_dict[var] = len(value)
    selections = sorted(selections_dict.items(), key=lambda pair: pair[1])

    min_values = [item for item in selections if item[1] == selections[0][1]]
    if len(min_values) == 1:
        return min_values[0][0]

    maximum = -float('inf')
    for var, _ in min_values:
        count = 0
        for constraint in csp.binaryConstraints:
            if constraint.affects(var) and not assignment.isAssigned(constraint.otherVariable(var)):
                count += 1
        if maximum < count:
            maximum = count
            nextVar = var
    return nextVar


def orderValues(assignment, csp, var):
    """
    Trivial method for ordering values to assign.
    Uses no heuristics.
    """
    return list(assignment.varDomains[var])


# = = = = = = = QUESTION 3  = = = = = = = #


def leastConstrainingValuesHeuristic(assignment, csp, var):
    """
    Creates an ordered list of the remaining values left for a given variable.
    Values should be attempted in the order returned.
    The least constraining value should be at the front of the list.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable to be assigned the values
    Returns:
        list<values>
        a list of the possible values ordered by the least constraining value heuristic
    """
    # TODO: Question 3 fix it
    domain = assignment.varDomains[var]
    value_dict = {}
    for value in domain:
        constraint_count = 0
        assignment.assignedValues[var] = value
        for other_var in csp.varDomains:
            if other_var != var:
                for other_value in assignment.varDomains[var]:
                    if consistent(assignment, csp, var, other_value):
                        constraint_count += 1
        value_dict[value] = constraint_count
        assignment.assignedValues[var] = None
    if value_dict:
        value_list = sorted(value_dict.items(), key=lambda pair: pair[1], reverse=True)
        return [_[0] for _ in value_list]
    return None


def noInferences(assignment, csp, var, value):
    """
    Trivial method for making no inferences.
    """
    return set([])


# = = = = = = = QUESTION 4  = = = = = = = #


def forwardChecking(assignment, csp, var, value):
    """
    Implements the forward checking algorithm.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set< tuple<variable, value> >
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    # TODO: Question 4
    domains = assignment.varDomains

    for constraint in csp.binaryConstraints:
        if constraint.affects(var):
            other_var = constraint.otherVariable(var)
            if not assignment.isAssigned(other_var):
                other_domain = domains[other_var]
                check_domain = set([])
                for other_value in other_domain:
                    if not consistent(assignment, csp, other_var, other_value):
                        check_domain.add(other_var)
                        inferences.add((other_var, other_value))
                if check_domain == other_domain:
                    return None

    for other_var, value in inferences:
        assignment.varDomains[other_var].remove(value)
    return inferences


# = = = = = = = QUESTION 5  = = = = = = = #


def revise(assignment, csp, var1, var2, constraint):
    """
    Helper function to maintainArcConsistency and AC3.
    Remove values from var2 domain if constraint cannot be satisfied.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var1 (string): the variable with consistent values
        var2 (string): the variable that should have inconsistent values removed
        constraint (BinaryConstraint): the constraint connecting var1 and var2
    Returns:
        set<tuple<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])
    # TODO: Question 5

    for x in assignment.varDomains[var1]:
        constraint_satisfied = False
        for y in assignment.varDomains[var2]:
            if constraint.isSatisfied(x, y):
                constraint_satisfied = True
                break
        if not constraint_satisfied:
            inferences.add((var1, x))

    if len(inferences) == len(assignment.varDomains[var1]):
        return None
    for var, value in inferences:
        assignment.varDomains[var].remove(value)
    return inferences


def maintainArcConsistency(assignment, csp, var, value):
    """
    Implements the maintaining arc consistency algorithm.
    Inferences take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    and inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set<<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    # inferences = set([])
    # domains = assignment.varDomains
    #
    # # TODO: Question 5
    # #  Hint: implement revise first and use it as a helper function"""
    # while not queue.empty():
    #     x_i, x_j = queue.get()
    #     for constraint in csp.binaryConstraints:
    #         if constraint.affects(x_i) and constraint.affects(x_j):
    #             revise_interference = revise(assignment, csp, x_i, x_j, constraint)
    #             if revise_interference is None:
    #                 for _var, _value in inferences:
    #                     domains[_var].add(_value)
    #                 return None
    #             else:
    #                 for _constraint in csp.binaryConstraints:
    #                     if _constraint.affects(x_j):
    #                         queue.put((x_j, _constraint.otherVariable(x_j)))
    #                 for _var, _value in revise_interference:
    #                     inferences.add((_var, _value))
    # return inferences
    inferences = set([])
    domains = assignment.varDomains
    """Hint: implement revise first and use it as a helper function"""
    """Question 5"""
    queue = Queue()
    for constraint in csp.binaryConstraints:
        if constraint.affects(var) and not assignment.isAssigned(constraint.otherVariable(var)):
            queue.put((var, constraint.otherVariable(var)))
    while not queue.empty():
        (x_i, x_j) = queue.get()
        for constraint in csp.binaryConstraints:
            if constraint.affects(x_i) and constraint.affects(x_j):
                revise_inference = revise(assignment, csp, x_j, x_i, constraint)
                if revise_inference is None:
                    for _var, _value in inferences:
                        assignment.varDomains[_var].add(_value)
                    return None
                if len(revise_inference):
                    for _constraint in csp.binaryConstraints:
                        if _constraint.affects(x_j):
                            queue.put((x_j, _constraint.otherVariable(x_j)))

                    for _revise in revise_inference:
                        inferences.add(_revise)
                break
    return inferences

    # = = = = = = = QUESTION 6  = = = = = = = #


def AC3(assignment, csp):
    """
    AC3 algorithm for constraint propagation.
    Used as a pre-processing step to reduce the problem
    before running recursive backtracking.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        Assignment
        the updated assignment after inferences are made or None if an inconsistent assignment
    """

    # TODO: Question 6
    #  Hint: implement revise first and use it as a helper function"""
    """Hint: implement revise first and use it as a helper function"""
    """Question 6"""
    queue = Queue()
    for key in csp.varDomains.keys():
        for constraint in csp.binaryConstraints:
            if constraint.affects(key):
                queue.put((key, constraint.otherVariable(key)))
    while not queue.empty():
        (x_i, x_j) = queue.get()
        for constraint in csp.binaryConstraints:
            if constraint.affects(x_i) and constraint.affects(x_j):
                revise_inference = revise(assignment, csp, x_j, x_i, constraint)
                if revise_inference is None:
                    return None
                if len(revise_inference):
                    for _constraint in csp.binaryConstraints:
                        if _constraint.affects(x_j):
                            queue.put((x_j, _constraint.otherVariable(x_j)))
    return assignment


def solve(csp, orderValuesMethod=leastConstrainingValuesHeuristic,
          selectVariableMethod=minimumRemainingValuesHeuristic,
          inferenceMethod=forwardChecking, useAC3=True):
    """
    Solves a binary constraint satisfaction problem.

    Args:
        csp (ConstraintSatisfactionProblem): a CSP to be solved
        orderValuesMethod (function): a function to decide the next value to try
        selectVariableMethod (function): a function to decide which variable to assign next
        inferenceMethod (function): a function to specify what type of inferences to use
        useAC3 (boolean): specifies whether to use the AC3 pre-processing step or not
    Returns:
        dictionary<string, value>
        A map from variables to their assigned values. None if no solution exists.
    """
    assignment = Assignment(csp)

    assignment = eliminateUnaryConstraints(assignment, csp)
    if assignment is None:
        return assignment

    if useAC3:
        assignment = AC3(assignment, csp)
        if assignment is None:
            return assignment

    assignment = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
    if assignment is None:
        return assignment

    return assignment.extractSolution()
