from .gk_solver_extension import GKConverter, solve


def solver_extension_pyomo(gekko_model, disp=True):
    try:
        import pyomo
    except:
        raise ImportError("Pyomo not installed. Run `$ pip install Pyomo` to install Pyomo in order to use solver extension to access more solvers.")
    solve(gekko_model, PyomoConverter, disp)


def create_pyomo_object(self):
    """
    returns the Pyomo equivalent object of the GEKKO model
    """
    # create a converter
    converter = PyomoConverter(self)
    # create pyomo equivalent model
    converter.convert()
    # return the pyomo model
    return converter._pyomo_model


class PyomoConverter(GKConverter):
    """
    Class for holding data relating to the pyomo model
    """

    from pyomo.environ import (
        ConcreteModel, 
        Var,
        Param,
        Integers,
        Reals,
        Objective, 
        Constraint, 
        SolverFactory,
        SolverStatus,
        TerminationCondition,
        value
    )

    def __init__(self, gekko_model) -> None:
        super().__init__(gekko_model)
        from pyomo.environ import value
        self.value = value


    def convert(self) -> None:
        """
        Convert the GEKKO model to a Pyomo model
        """
        # create a new pyomo model object
        self._pyomo_model = self.ConcreteModel()
        # call base class convert method
        super().convert()


    def add_constant(self, constant) -> None:
        """
        add a constant to the pyomo model
        """
        pyomo_obj = self.Param(initialize=constant["value"])
        self._pyomo_model.add_component(constant["name"], pyomo_obj)


    def add_parameter(self, parameter) -> None:
        """
        add a parameter to the pyomo model
        """
        # we will just consider the parameter as a variable
        self.add_variable(parameter)
    

    def add_variable(self, variable) -> None:
        """
        add a variable to the pyomo model
        """
        domain = self.Integers if variable["integer"] else self.Reals
        pyomo_obj = self.Var(initialize=variable["value"], bounds=(variable["lower"], variable["upper"]), domain=domain)
        self._pyomo_model.add_component(variable["name"], pyomo_obj)

    
    def add_intermediate(self, intermediate) -> None:
        """
        add an intermediate variable to the pyomo model
        """
        # add a new variable
        # constraints are added later
        self.add_variable(intermediate)

    
    def add_constraint(self, constraint) -> None:
        """
        add a constraint to the pyomo model
        """
        super().add_constraint(constraint)
        
        # Gekko equations are stored as strings, so we need to convert this to pyomo's declarative
        # expression format. Gekko does all the preprocessing, so within each bracket we should just have
        # two variables/constants separated by an operator.

        # reset the expression index
        self._expr_index = 0
        # find the expression
        expression = self.expression(constraint)
        # create a pyomo constraint object
        pyomo_obj = self.Constraint(expr=expression)
        self._pyomo_model.add_component("constraint" + str(self._equations_num), pyomo_obj)


    def expression(self, expr):
        """
        find a sub-expression
        """
        left = self.expr_var(expr, left=True)
        if self._expr_index == len(expr) or expr[self._expr_index] == ")":
            return left
        operator = expr[self._expr_index]
        self._expr_index += 1
        right = self.expr_var(expr, left=False)
        return self.expr_operators()[operator](left, right)
    

    def expr_var(self, expr, left=True):
        """
        find a variable in an expression
        """
        if expr[self._expr_index] == "(":
            # sub-expression
            self._expr_index += 1
            subexp = self.expression(expr)
            self._expr_index += 1
            return subexp
        var = ""
        # loop until we reach an operator, a closing bracket or the end of the expression
        while self._expr_index < len(expr) and not (left and expr[self._expr_index] in self.expr_operators()):
            if expr[self._expr_index] == ")":
                break
            var += expr[self._expr_index]
            self._expr_index += 1
        # now we have the variable as a string, we need to find the component in the pyomo object
        pyomo_obj = self._pyomo_model.find_component(var)
        if pyomo_obj is None:
            # if the variable is not found, it is a constant
            return float(var)
        return pyomo_obj


    def expr_operators(self):
        """
        return a dictionary of operators
        """
        return {
            "=": lambda x, y: x == y,
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y,
            "^": lambda x, y: x ** y
        }
    

    def add_objective(self, objective) -> None:
        """
        add an objective to the pyomo model
        """
        super().add_objective(objective)
        sense = 1 if objective.startswith("minimize") else -1
        # find the expression
        self._expr_index = 0
        expression = self.expression(objective[objective.find(" ") + 1:])
        # create a pyomo objective object
        pyomo_obj = self.Objective(expr=expression, sense=sense)
        self._pyomo_model.add_component("objective" + str(self._equations_num), pyomo_obj)


    def add_prebuilt_object(self, prebuilt_object) -> None:
        pass


    def get_parameter_value(self, name) -> float:
        """
        get the value of a parameter
        """
        return self._pyomo_model.find_component(name).value
    

    def get_variable_value(self, name) -> float:
        """
        get the value of a variable
        """
        return self._pyomo_model.find_component(name).value
    

    def get_intermediate_value(self, name) -> float:
        """
        get the value of an intermediate variable
        """
        return self.get_variable_value(name)
    

    def get_objective_values(self) -> list[int]:
        """
        get the values of the objectives
        """
        objective_values = []
        objective_names = self._pyomo_model.component_objects(self.Objective)
        for objective in objective_names:
            objective_obj = self._pyomo_model.find_component(objective)
            objective_values.append(self.value(objective_obj))
        return objective_values
    

    def set_options(self) -> None:
        """
        set the options for the pyomo model
        """
        pass
    

    def solve(self):
        """
        solve the pyomo model
        """
        solver_name = self._gekko_model.options.SOLVER
        if isinstance(solver_name, int):
            raise ValueError("Solver extension requires a string for m.options.SOLVER for the solver you want to use")
        # create a solver object
        solver = self.SolverFactory(self._gekko_model.options.SOLVER)
        # solve the model
        results = solver.solve(self._pyomo_model)
        # check the results
        solver_status = results.solver.status
        solution_status = results.solver.termination_condition

        if solver_status != self.SolverStatus.ok:
            raise Exception("Solver did not exit normally. Solver status: %s" % solver_status)
        if solution_status != self.TerminationCondition.optimal:
            raise Exception("The solver did not find an optimal solution.")