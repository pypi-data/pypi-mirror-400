import ast
import operator as op

# --- AST SECURITY CONFIGURATION ---
class NttError(Exception):
    """Base exception for NTT errors."""
    pass

class NttSecurityError(NttError):
    """Raised when an unsafe operation is detected in a template."""
    pass

# Map safe AST operators to built-in Python functions for secure execution
_SAFE_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.USub: op.neg, ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, 
    ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge, ast.And: op.and_, ast.Or: op.or_
}

def _safe_eval_ast(expression_str):
    """
    Parses and securely executes a simple mathematical or conditional expression 
    string using AST, replacing the direct use of eval().
    """
    try:
        # 1. Parse the expression string into an AST tree
        node = ast.parse(expression_str, mode='eval').body
    except SyntaxError as e:
        raise NttSecurityError(f"Invalid expression syntax for secure parsing: {expression_str}") from e

    # 2. Define a recursive executor that validates every node type
    def _execute(node):
        # Allow only safe literal values (numbers, strings)
        if isinstance(node, (ast.Constant, ast.Num)):
            return node.value if isinstance(node, ast.Constant) else node.n
        
        # Allow only safe arithmetic/logical operations (BinOp, UnaryOp, BoolOp)
        elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp)):
            if isinstance(node.op, (ast.Not, ast.In, ast.NotIn, ast.Is, ast.IsNot, ast.Pow)):
                raise NttSecurityError(f"Unsupported operator type: {type(node.op).__name__}")
            
            # Handle Boolean operators (And/Or)
            if isinstance(node, ast.BoolOp):
                left_operand = _execute(node.values[0])
                right_operand = _execute(node.values[1])
                op_func = op.and_ if isinstance(node.op, ast.And) else op.or_
                return op_func(left_operand, right_operand)
            
            # Simple Unary/Binary ops
            op_func = _SAFE_OPS.get(type(node.op))
            if op_func is None:
                raise NttSecurityError(f"Unsupported operation type: {type(node.op).__name__}")
            
            if isinstance(node, ast.UnaryOp):
                return op_func(_execute(node.operand))
            else: # ast.BinOp
                return op_func(_execute(node.left), _execute(node.right))

        # Allow safe comparisons (e.g., 5 > 3)
        elif isinstance(node, ast.Compare):
            left = _execute(node.left)
            
            # Check for chained comparisons and validate operators
            for op_ast, comparator in zip(node.ops, node.comparators):
                op_func = _SAFE_OPS.get(type(op_ast))
                if op_func is None:
                    raise NttSecurityError(f"Unsupported comparison operator: {type(op_ast).__name__}")
                
                right = _execute(comparator)
                if not op_func(left, right):
                    return False
                left = right # For chained comparisons (a > b > c)
            return True

        # CRITICAL: Deny all other node types (Call, Name, Attribute, Lambda, etc.)
        else:
            raise NttSecurityError(f"Illegal operation: {type(node).__name__} is forbidden.")

    # 3. Start execution from the top node
    return _execute(node)

# --------------------- SiaNTT Class Implementation --------------------- #

class ntt:
    """
    SiaObj: Ultra-simple, declarative entity module for students.
    Features: Secure AST-based evaluation for conditionals and validation.
    """

    # Reserved names
    _RESERVED = {'set', 'computed', 'validate', 'inherit', 'operator', '__call__', '__getitem__'}

    def __init__(self, *attrs, **methods):
        if any(name in self._RESERVED for name in methods):
             raise NttError(f"Method names conflict with reserved keywords: {self._RESERVED}")
        
        self._names = list(attrs)
        self._methods = methods.copy() if methods else {}
        self._computed = {}
        self._validators = {}
        self._defaults = {n: None for n in attrs}
        self._parents = []
        self._polymorphic_methods = {}
        self._operators = {}
        
    def _create_method_wrapper(self, template):
        def method_wrapper():
            return self._execute_conditional_template(template, self)
        return method_wrapper

    def _execute_conditional_template(self, template, inst):
        parts = [p.strip() for p in template.split('|')]
        
        # 1. Handle simple template
        if len(parts) == 1:
            return self._apply_template(template, inst)

        # 2. Handle conditional templates
        for part in parts:
            prefix, *rest = part.lower().split(':', 1)
            
            if prefix.startswith('if ') or prefix.startswith('elif '):
                # Determine where the condition starts
                start_index = 3 if prefix.startswith('if ') else 5
                condition_part = prefix[start_index:].strip()
                result_part = rest[0].strip()
                
                condition_expr = self._apply_template(condition_part, inst)
                
                # --- SECURITY FIX: Using AST instead of eval() ---
                try:
                    if _safe_eval_ast(condition_expr):
                        return self._apply_template(result_part, inst)
                except NttSecurityError as e:
                    raise NttError(f"Security error in condition '{condition_expr}': {e}") from e
                except Exception as e:
                    raise NttError(f"Evaluation error in condition '{condition_expr}': {e}") from e
            
            elif prefix == 'else':
                return self._apply_template(rest[0].strip(), inst)
        
        return None

    # --- Standard Bracket Access (p1['name'] or p1[0]) ---
    def __getitem__(self, key):
        """Allows access by index (int) or attribute name (str)."""
        if isinstance(key, str):
            return getattr(self, key)
        elif isinstance(key, int):
            if key < 0 or key >= len(self._names):
                raise IndexError(f"Index {key} is out of bounds.")
            name = self._names[key]
            return getattr(self, name)
        elif isinstance(key, slice):
            indices = range(*key.indices(len(self._names)))
            return tuple(getattr(self, self._names[i]) for i in indices)
        else:
            raise TypeError("Key must be an integer, string, or slice.")

    # --------------- Template Definition Methods ---------------- #
    def inherit(self, *parents):
        for p in parents:
            if isinstance(p, ntt):
                self._parents.append(p)
                for n in p._names:
                    if n not in self._names:
                        self._names.append(n)
                        self._defaults[n] = p._defaults.get(n, None)
                for k, v in p._methods.items():
                    if k not in self._methods: self._methods[k] = v
                for n, v in p._computed.items():
                    if n not in self._computed: self._computed[n] = v
                for n, v in p._validators.items():
                    if n not in self._validators: self._validators[n] = v
                if p._parents:
                    self.inherit(*p._parents)
        return self

    def polymorphic(self, method_name, template):
        if method_name not in self._polymorphic_methods:
            self._polymorphic_methods[method_name] = {}
        self._polymorphic_methods[method_name][id(self)] = template
        setattr(self, method_name, self._create_method_wrapper(template))
        return self

    def operator(self, symbol, template):
        self._operators[symbol] = template
        return self

    def computed(self, name, template):
        self._computed[name] = template
        return self

    def validate(self, name, template):
        self._validators[name] = template
        return self
    
    # --------------- Instance Creation ---------------- #
    def __call__(self, *args, **kwargs):
        inst = object.__new__(self.__class__)
        inst._names = self._names.copy()
        inst._methods = self._methods.copy()
        inst._computed = self._computed.copy()
        inst._validators = self._validators.copy()
        inst._defaults = self._defaults.copy()
        inst._parents = self._parents.copy()
        inst._polymorphic_methods = {k: v.copy() for k, v in self._polymorphic_methods.items()}
        inst._operators = self._operators.copy()

        # Bind methods
        setattr(inst, '_create_method_wrapper', self._create_method_wrapper.__get__(inst, self.__class__))
        setattr(inst, '_apply_template', self._apply_template.__get__(inst, self.__class__))
        setattr(inst, '_execute_conditional_template', self._execute_conditional_template.__get__(inst, self.__class__))
        setattr(inst, '__getitem__', self.__getitem__.__get__(inst, self.__class__))

        # Set attributes
        for i, v in enumerate(args): setattr(inst, inst._names[i], v)
        for k, v in kwargs.items(): setattr(inst, k, v)
        for n in inst._names:
            if not hasattr(inst, n): setattr(inst, n, inst._defaults[n])

        # Apply methods and computed properties
        for k, t in inst._methods.items():
            setattr(inst, k, inst._create_method_wrapper(t))

        for n, t in inst._computed.items():
            setattr(inst, n, inst._execute_conditional_template(t, inst))
            
        for k, v in inst._polymorphic_methods.items():
            if id(inst) in v:
                setattr(inst, k, inst._execute_conditional_template(v[id(inst)], inst))
        return inst

    # --------------- Set Attributes ---------------- #
    def set(self, *values):
        for i, v in enumerate(values):
            name = self._names[i]
            temp = self._validators.get(name)
            if temp:
                expr = self._apply_template(temp, self)
                # --- SECURITY FIX: Using AST instead of eval() for validation ---
                try:
                    if not _safe_eval_ast(expr): 
                        raise ValueError(f"Validation failed for {name}={v}")
                except NttSecurityError as e:
                    raise ValueError(f"Security error in validator '{expr}': {e}") from e
                except Exception as e:
                    raise ValueError(f"Evaluation error in validator '{expr}': {e}") from e

            setattr(self, name, v)
            
        # Refresh computed and polymorphic properties
        for n, t in self._computed.items():
            setattr(self, n, self._execute_conditional_template(t, self))
            
        for k, v in self._polymorphic_methods.items():
            if id(self) in v:
                setattr(self, k, self._execute_conditional_template(v[id(self)], self))
        return self

    # --------------- Add Method Dynamically ---------------- #
    def add_method(self, name, template):
        self._methods[name] = template
        setattr(self, name, self._create_method_wrapper(template))
        return self

    # --------------- Apply Template (Simple replacement) ---------------- #
    def _apply_template(self, template, inst=None):
        if inst is None: inst = self
        result = template
        # The template replacement remains simple string substitution
        for i, n in enumerate(inst._names):
            try:
                # Using f-string for replacement here is okay as it's internal module code
                result = result.replace(f"({i})", str(getattr(inst, n)))
            except AttributeError:
                return f"[ATTR_MISSING: {n}]" 
        return result

    # --- OPERATOR HANDLING (Uses the secure AST method) ---
    def _parse_arithmetic(self, expr):
        try:
            return _safe_eval_ast(expr)
        except Exception as e:
            raise NttError(f"Arithmetic error in operator: {expr}") from e

    def _operate(self, other, symbol):
        temp = self._operators.get(symbol)
        if temp is None: return None
        
        # 1. Get values for substitution
        vals = [str(getattr(self, n)) for n in self._names]
        if isinstance(other, ntt):
            vals.extend([str(getattr(other, n)) for n in other._names])
        else:
            vals.append(str(other))

        # 2. Apply replacement
        result_template = temp
        for i, v in enumerate(vals):
            result_template = result_template.replace(f"({i})", v)

        # 3. Execution (Comparison or Arithmetic)
        if symbol in ('==', '!=', '<', '>', '<=', '>='):
            try:
                return _safe_eval_ast(result_template)
            except Exception as e:
                raise NttError(f"Comparison error in operator '{symbol}': {e}") from e
        
        # Arithmetic uses the secure AST method
        return self._parse_arithmetic(result_template)

    __add__ = lambda self, o: self._operate(o, '+')
    __sub__ = lambda self, o: self._operate(o, '-')
    __mul__ = lambda self, o: self._operate(o, '*')
    __truediv__ = lambda self, o: self._operate(o, '/')
    __eq__ = lambda self, o: self._operate(o, '==')
    __ne__ = lambda self, o: self._operate(o, '!=')
    __lt__ = lambda self, o: self._operate(o, '<')
    __le__ = lambda self, o: self._operate(o, '<=')
    __gt__ = lambda self, o: self._operate(o, '>')
    __ge__ = lambda self, o: self._operate(o, '>=')

    # --------------- String Representation ---------------- #
    __str__ = lambda self: f"{self.__class__.__name__}({', '.join(f'{n}={getattr(self,n)}' for n in self._names)}{', ' + ', '.join(f'{k}={getattr(self,k)}' for k in self._computed) if self._computed else ''})"
    __repr__ = __str__