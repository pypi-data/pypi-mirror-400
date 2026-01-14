import ast, _ast
import inspect
from types import ModuleType
from typing import Any
from copy import deepcopy


class BaseParsed(ast.NodeVisitor):
    """
    A class containing information about parsed data
    """
    name: str
    body: list[ast.AST]

    def __init__(self, node: ast.AST) -> None:
        """Initialize this BaseParsed"""
        self.name = node.name
        self.body = node.body


class ParsedFunction(BaseParsed):
    """
    A class containing information about a parsed function
    """
    called_functions: set[str]
    called_methods: set[str]

    def __init__(self, node: ast.AST) -> None:
        """Initialize this ParsedFunction"""
        super().__init__(node)
        self.called_functions = set()
        self.called_methods = set()
        self.visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            self.called_methods.add(method_name)
            # FIXME: This does not record which class the method belongs to, as
            #        AST does not have that information
        elif isinstance(node.func, ast.Name):
            self.called_functions.add(node.func.id)

    def uses_ast(self, ast_checks: set[type]) -> bool:
        """Return True iff this ParsedFunction's body uses any of the
        ASTs in ast_checks.
        """
        return any(any(isinstance(node, t) for t in ast_checks)
                   for node in self.body)

    def is_implemented(self) -> bool:
        """Return True iff this function is implemented"""
        return any(not ((isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Constant))
                        or isinstance(node, ast.Pass)
                        )
                   for node in self.body)


class ParsedMethod(ParsedFunction):
    """
    A class containing information about a parsed method
    """
    containing_class: str

    def __init__(self, node: ast.AST, containing_class: str) -> None:
        """Initialize this ParsedMethod"""
        super().__init__(node)
        self.containing_class = containing_class


class ParsedClass(BaseParsed):
    """
    A class containing information about a parsed Class
    """
    bases: set[str]
    methods: dict[str, ParsedMethod]

    def __init__(self, node: ast.AST) -> None:
        """Initialize this ParsedClass
        """
        super().__init__(node)
        self.bases = {base.id for base in node.bases if hasattr(base, 'id')}
        self.methods = {}
        self.visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        # All FunctionDefs here are actually methods
        pm = ParsedMethod(node, self.name)
        self.methods[node.name] = pm

    def get_unimplemented(self) -> set:
        """Return a set of unimplemented methods"""
        unimplemented = set()
        for method in self.methods:
            if not self.methods[method].is_implemented():
                unimplemented.add(f"{self.name}.{method}")
        return unimplemented


class ASTParser(ast.NodeVisitor):
    """
    NodeVisitor that records all function dependencies.

    Usage:
    >>> ap = ASTParser()
    >>> ap.parse('test/example_code.py')  # Accepts a module or a path name
    >>> ap.get_functions_using({ast.For}) == {'ExampleClass.loop_calls_for',
    ... 'ExampleSubclass.loop_for', 'loop_for', 'loop_calls_for',
    ... 'ExampleSubclass.loop_calls_for', 'ExampleClass.loop_for'}
    True
    """
    _functions: dict[str, ParsedFunction]
    _classes: dict[str, ParsedClass]
    _function_dependencies: dict[str, set]

    def __init__(self) -> None:
        """Initialize this DependencyBuilder."""
        self._functions = {}
        self._classes = {}
        self._dependencies = {}

    def parse(self, to_parse: str | ModuleType | ast.AST):
        """Parse the given to_parse into an AST and add all defined functions
        and methods to this DependencyBuilder.

        mod_or_path can be either an object, filename, or an AST node.
        """
        if isinstance(to_parse, str):
            with open(to_parse) as file:
                source = file.read()
            parsed_ast = ast.parse(source)
        elif isinstance(to_parse, ast.AST):
            parsed_ast = to_parse
        else:
            source = inspect.getsource(to_parse)
            parsed_ast = ast.parse(source)

        self.visit(parsed_ast)

        # When done, update any function call dependencies
        self._update_dependencies()

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        # Prefix the results with the class name and add it to this dictionary
        parsed_class = ParsedClass(node)
        self._classes[parsed_class.name] = parsed_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        parsed_function = ParsedFunction(node)
        self._functions[parsed_function.name] = parsed_function

    def _update_dependencies(self) -> None:
        """Update self._dependencies to include all function and method
        dependencies.

        Does not include indirect dependencies, but does include inherited
        dependencies
        """
        # Add all of the functions in
        for fn in self._functions:
            if fn not in self._dependencies:
                self._dependencies[fn] = set()
            self._dependencies[fn].update(self._functions[fn].called_functions)

            # FIXME: All methods are added in without a prefix for the parent
            #        class
            self._dependencies[fn].update(self._functions[fn].called_methods)

        # Add all of the methods in
        for cls in self._classes:
            class_methods = self._classes[cls].methods
            for method in class_methods:
                full_key = f"{cls}.{method}"
                if full_key not in self._dependencies:
                    self._dependencies[full_key] = set()

                # Add functions
                self._dependencies[full_key].update(
                    class_methods[method].called_functions
                )

                # Add methods
                # FIXME: This currently assumes the method belongs to the
                #        same class.
                self._dependencies[full_key].update(
                    {
                        f"{cls}.{method_name}" for method_name in
                        class_methods[method].called_methods
                    }
                )

        # Add any inherited methods
        for cls in self._classes:
            for parent in self._classes[cls].bases:
                class_methods = self._classes[parent].methods
                # Add all the parent methods to this child class if it does not
                # already exist, and make it refer to the parent method
                for method in class_methods:
                    full_key = f"{cls}.{method}"
                    if full_key not in self._dependencies:
                        # Add all the dependencies of the parent, but replace
                        # <parent>. prefix with the current class.
                        self._dependencies[full_key] = \
                            {
                                method.replace(f"{parent}.", f"{cls}.")
                                for method in self._dependencies[f"{parent}.{method}"]
                            }

                        # Add the method into the subclass as well
                        inherited_method = deepcopy(class_methods[method])
                        inherited_method.containing_class = cls
                        self._classes[cls].methods[method] = inherited_method

    def get_dependencies(self, indirect: bool = True, current: dict = None) -> dict:
        if not indirect:
            return deepcopy(self._dependencies)

        # Otherwise, build dependencies
        if current is None:
            current = deepcopy(self._dependencies)
        original = deepcopy(current)

        for function_name in current:
            # Go through all functions that this function called
            originally_called_functions = list(current[function_name])
            for called_function in originally_called_functions:
                if called_function in current:
                    for indirectly_called in current[called_function]:
                        current[function_name].add(indirectly_called)

        if original == current:
            return current

        return self.get_dependencies(current=current)

    def get_recursive(self, indirect: bool = True) -> set:
        """Return a set of recursive functions and methods.
        """
        dependencies = self.get_dependencies(indirect=indirect)

        # A function/method is recursive if it calls itself
        recursive = set()
        for fn in dependencies:
            if fn in dependencies[fn]:
                recursive.add(fn)

        if indirect is False:
            return recursive

        # Otherwise: a function/method is recursive if it calls on a
        # recursive function/method
        indirectly_recursive = set()
        for fn in dependencies:
            if any(called in recursive for called in dependencies[fn]):
                indirectly_recursive.add(fn)

        return recursive.union(indirectly_recursive)

    def get_unimplemented(self) -> set:
        """Return a set of unimplemented functions/methods.
        """
        unimplemented = set()
        for function in self._functions:
            if not self._functions[function].is_implemented():
                unimplemented.add(function)

        # FIXME: Ignores any inherited methods
        for cls in self._classes:
            unimplemented.update(self._classes[cls].get_unimplemented())

        return unimplemented

    def get_functions_using(self, ast_checks: set[type],
                            indirect: bool = True) -> set:
        """Return a set of functions that use any of the ASTs in ast_checks.
        """
        dependencies = self.get_dependencies(indirect=True)

        initial = set()
        for fn in dependencies:
            if "." in fn:
                cls, method = fn.split(".")
                if self._classes[cls].methods[method].uses_ast(ast_checks):
                    initial.add(fn)
            else:
                if self._functions[fn].uses_ast(ast_checks):
                    initial.add(fn)

        if indirect is False:
            return initial

        indirect = set()
        for fn in dependencies:
            if any(called in initial for called in dependencies[fn]):
                indirect.add(fn)

        return initial.union(indirect)


def _get_path(obj_or_path: str | ModuleType) -> str:
    """Return the path given an object, module, or path.
    """
    if isinstance(obj_or_path, str):
        path = obj_or_path
    elif inspect.ismodule(obj_or_path) or inspect.isclass(obj_or_path):
        path = inspect.getfile(obj_or_path)
    elif inspect.isfunction(obj_or_path):
        path = inspect.getfile(obj_or_path)
    else:
        path = getattr(obj_or_path, '__file__', f'{obj_or_path.__name__}.py')

    return path


def is_empty(mod_or_path: str | ModuleType, function_name: str) -> bool:
    """
    Return True if the body of the function <function_name> in filename is empty.

    Ignores all comments.
    """
    ap = ASTParser()
    path = _get_path(mod_or_path)
    ap.parse(path)
    empty_functions = ap.get_unimplemented()

    return function_name in empty_functions


def is_unimplemented(obj_or_path: str | ModuleType, function_name: str = "") -> bool:
    """
    Return True if the body of the function <function_name> in the given object
    or path is not implemented (empty).

    Ignores all comments.
    """
    ap = ASTParser()

    if inspect.isfunction(obj_or_path):
        function_name = function_name or obj_or_path.__name__
    path = _get_path(obj_or_path)

    ap.parse(path)
    empty_functions = ap.get_unimplemented()

    if not function_name:
        return len(empty_functions) > 0

    return function_name in empty_functions


def get_recursive(obj_or_path: str | ModuleType | list,
                  indirect: bool = True) -> set[str]:
    """Return a set of recursive functions and methods in obj_or_path.

    If obj_or_path is a list of elements, all of them are parsed before checking.
    """
    ap = ASTParser()
    if isinstance(obj_or_path, list):
        for item in obj_or_path:
            ap.parse(item)
    else:
        path = _get_path(obj_or_path)
        ap.parse(path)

    return ap.get_recursive(indirect=indirect)


def get_functions_using(obj_or_path: str | ModuleType | list,
                        ast_types: set[type],
                        indirect: bool = True) -> set[str]:
    """Return a set of functions/methods defined in obj_or_path that use
    any of the AST types in ast_types (e.g. ast.For, ast.While).

    If obj_or_path is a list of elements, all of them are parsed before checking.
    """
    ap = ASTParser()
    if isinstance(obj_or_path, list):
        for item in obj_or_path:
            ap.parse(item)
    else:
        path = _get_path(obj_or_path)
        ap.parse(path)

    return ap.get_functions_using(ast_types, indirect=indirect)


def get_functions_that_call(obj_or_path: str | ModuleType | list,
                            function_names: set[str],
                            indirect: bool = True) -> set[str]:
    """Return a set of functions/methods defined in obj_or_path that call
    any of the functions or methods in function_names.

    If obj_or_path is a list of elements, all of them are parsed before checking.
    """
    ap = ASTParser()
    if isinstance(obj_or_path, list):
        for item in obj_or_path:
            ap.parse(item)
    else:
        path = _get_path(obj_or_path)
        ap.parse(path)

    dependencies = ap.get_dependencies(indirect=indirect)
    called = set()
    for fn in dependencies:
        if any(name in dependencies[fn] for name in function_names):
            called.add(fn)

    return called
