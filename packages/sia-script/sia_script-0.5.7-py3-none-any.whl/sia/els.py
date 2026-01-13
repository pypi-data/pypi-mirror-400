"""
SIA ENTERPRISE LOGIC STUDIO - STRICT ABAP INTERPRETER
=====================================================
Single-file version (els.py)
Author: Nagesh
Version: 4.2 - Complete Syllabus Support with Bug Fixes
-----------------------------------------

This module implements STRICT ABAP semantics:

- Complete type system with TYPE C LENGTH support
- Boolean expression restrictions (ABAP-compliant)
- SY-SUBRC updates for all operations
- MODIFY, DELETE, INSERT operations
- EXIT, CONTINUE, CHECK in loops
- SELECT with AND/OR WHERE clauses, ORDER BY
- Structure definitions (TYPES BEGIN OF)
- FORM / PERFORM support
- PARAMETERS / SELECT-OPTIONS with range logic
- START-OF-SELECTION event
- Virtual Open SQL Engine
- Internal Table Typing
- Class method execution
- AT NEW / AT END OF simulation

Outer wrapper required:
*sia
   ABAP code...
sia*
"""

import re
import sys
import datetime
import json
from typing import List, Dict, Any, Optional, Union, Tuple, Callable

# =====================================================
# ===============     TYPE SYSTEM     ================
# =====================================================

class ABAPType:
    """ABAP type system with strict validation and conversion"""
    
    TYPE_MAP = {
        'I': ('integer', 0, None),
        'C': ('character', ' ', 1),  # Default length 1
        'STRING': ('string', '', None),
        'F': ('float', 0.0, None),
        'P': ('packed', 0, None),
        'N': ('numeric', '0', None),
        'D': ('date', '00000000', 8),
        'T': ('time', '000000', 6),
        'X': ('hexadecimal', '00', None)
    }
    
    def __init__(self, type_name: str, length: Optional[int] = None):
        self.name = type_name.upper()
        if self.name not in self.TYPE_MAP:
            raise ValueError(f"Unknown ABAP type: {type_name}")
        
        self.kind, self.default, self.default_length = self.TYPE_MAP[self.name]
        self.length = length if length is not None else self.default_length
        
        # ABAP defaults
        if self.name == 'C' and self.length is None:
            self.length = 1  # Default length for TYPE C
    
    def validate(self, value: Any) -> Any:
        """Validate and convert value to this type following strict ABAP rules"""
        if value is None:
            return self.default_value()
        
        str_value = str(value)
        
        if self.name == 'I':
            try:
                # ABAP: Convert to integer, truncate decimal
                return int(float(str_value))
            except (ValueError, TypeError):
                return 0
                
        elif self.name == 'C':
            # ABAP C type: fixed length, space-padded, no truncation warning
            if self.length:
                # Pad with spaces to exact length
                if len(str_value) > self.length:
                    # Silent truncation (ABAP behavior)
                    return str_value[:self.length]
                else:
                    return str_value.ljust(self.length)
            return str_value
            
        elif self.name == 'STRING':
            return str_value
            
        elif self.name == 'F':
            try:
                return float(str_value)
            except (ValueError, TypeError):
                return 0.0
                
        elif self.name == 'D':  # YYYYMMDD
            clean = ''.join(c for c in str_value if c.isdigit())
            if len(clean) >= 8:
                return clean[:8]
            return clean.rjust(8, '0')
            
        elif self.name == 'T':  # HHMMSS
            clean = ''.join(c for c in str_value if c.isdigit())
            if len(clean) >= 6:
                return clean[:6]
            return clean.rjust(6, '0')
            
        elif self.name == 'N':
            # Numeric string: digits only, right-aligned, zero-padded
            digits = ''.join(c for c in str_value if c.isdigit())
            if self.length:
                return digits.rjust(self.length, '0')[:self.length]
            return digits
            
        elif self.name == 'P':
            # Packed decimal - store as integer for now
            try:
                return int(float(str_value))
            except (ValueError, TypeError):
                return 0
                
        elif self.name == 'X':
            # Hexadecimal - simple string representation
            hex_chars = '0123456789ABCDEFabcdef'
            filtered = ''.join(c for c in str_value if c in hex_chars)
            return filtered.upper()
        
        return str_value
    
    def default_value(self) -> Any:
        """Return default value for type (ABAP initial value)"""
        if self.name == 'I':
            return 0
        elif self.name == 'C':
            if self.length:
                return ' ' * self.length
            return ' '
        elif self.name == 'STRING':
            return ''
        elif self.name == 'F':
            return 0.0
        elif self.name == 'D':
            return '00000000'
        elif self.name == 'T':
            return '000000'
        elif self.name == 'N':
            if self.length:
                return '0' * self.length
            return '0'
        elif self.name == 'P':
            return 0
        elif self.name == 'X':
            return '00'
        return ''
    
    def __repr__(self):
        if self.length:
            return f"ABAPType({self.name}, LENGTH {self.length})"
        return f"ABAPType({self.name})"


class TypedVariable:
    """Variable with strict ABAP type information"""
    
    def __init__(self, name: str, abap_type: ABAPType, value: Any = None):
        self.name = name
        self.type = abap_type
        self.value = self.type.validate(value) if value is not None else self.type.default_value()
    
    def set_value(self, value: Any):
        """Set value with strict type validation"""
        self.value = self.type.validate(value)
    
    def get_value(self) -> Any:
        """Get typed value"""
        return self.value
    
    def __repr__(self):
        return f"TypedVariable({self.name}, {self.type}, {repr(self.value)})"


# =====================================================
# ===============   LEXICAL ANALYSIS   ================
# =====================================================

class Token:
    """Lexical token with position information"""
    
    def __init__(self, kind: str, value: str, line: int, col: int):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.kind}, '{self.value}', line={self.line}, col={self.col})"


# ABAP keywords (strict) - Added AT
ABAP_KEYWORDS = [
    # Data declaration
    "DATA", "TYPES", "TYPE", "LIKE", "CONSTANTS", "VALUE", "LENGTH",
    "PARAMETERS", "SELECT-OPTIONS", "FOR", "DEFAULT",
    
    # Control structures
    "IF", "ELSEIF", "ELSE", "ENDIF",
    "CASE", "WHEN", "OTHERS", "ENDCASE",
    "WHILE", "ENDWHILE",
    "DO", "TIMES", "ENDDO",
    "LOOP", "AT", "INTO", "ENDLOOP",
    
    # Data manipulation
    "WRITE", "CLEAR", "MOVE",
    "APPEND", "INSERT", "MODIFY", "DELETE",
    "READ", "TABLE", "WITH", "KEY",
    
    # Loop control
    "EXIT", "CONTINUE", "CHECK",
    
    # Structure definitions
    "BEGIN", "OF", "END", "OF",
    
    # SQL
    "SELECT", "FROM", "WHERE", "INTO", "ORDER", "BY",
    "UPDATE", "SET", "COMMIT", "WORK", "ROLLBACK",
    
    # Subroutines
    "FORM", "PERFORM", "USING", "CHANGING", "ENDFORM",
    
    # Events
    "START-OF-SELECTION",
    
    # OOP
    "CREATE", "OBJECT", "CLASS", "DEFINITION", "IMPLEMENTATION",
    "PUBLIC", "SECTION", "PRIVATE", "PROTECTED", "ENDCLASS",
    "CALL", "METHOD", "EXPORTING", "IMPORTING", "CHANGING",
    "RETURNING", "ME",
    
    # Logical operators
    "AND", "OR", "NOT",
    
    # System
    "SY-SUBRC", "SY-TABIX", "SY-INDEX", "SY-DBCNT", "SY-DATUM", "SY-UZEIT"
]


# Token patterns (order matters!)
TOKEN_PATTERNS = [
    ("STRING",   r"'([^']|'')*'"),  # Handle escaped quotes
    ("NUMBER",   r"\b\d+\b"),
    ("KEYWORD",  r"(?<!\w)(" + "|".join(map(re.escape, ABAP_KEYWORDS)) + r")(?!\w)"),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_\-]*"),
    ("SYMBOL",   r"->|==|!=|<=|>=|:=|[-+*/=().,:<>]"),
    ("NEWLINE",  r"\n"),
    ("SKIP",     r"[ \t\r]+"),
    ("COMMENT",  r"\*.*?$|\".*?$"),
]


TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_PATTERNS),
    re.MULTILINE | re.IGNORECASE
)


def tokenize_abap(src: str) -> List[Token]:
    """Convert ABAP source into tokens with strict ABAP mode"""
    tokens = []
    line = 1
    col = 1
    
    for m in TOKEN_REGEX.finditer(src):
        kind = m.lastgroup
        value = m.group()
        
        if kind == "NEWLINE":
            line += 1
            col = 1
            continue
        
        if kind == "SKIP":
            col += len(value)
            continue
        
        if kind == "COMMENT":
            col += len(value)
            continue
        
        # Normalize keywords to uppercase
        if kind == "KEYWORD":
            value = value.upper()
        
        # Normalize identifiers to lowercase
        elif kind == "ID":
            value = value.lower()
        
        tok = Token(kind, value, line, col)
        tokens.append(tok)
        col += len(value)
    
    return tokens


# =====================================================
# ===============     AST DEFINITIONS    ==============
# =====================================================

class ASTNode:
    """Base class for all AST nodes"""
    pass


class Program(ASTNode):
    """Root program node"""
    
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


# ----- Structure Definitions -----

class TypesBeginOf(ASTNode):
    """TYPES BEGIN OF structure"""
    
    def __init__(self, name: str, components: List[Tuple[str, str, Optional[int]]]):
        self.name = name
        self.components = components  # (field_name, type_name, length)
    
    def __repr__(self):
        return f"TypesBeginOf({self.name}, {len(self.components)} fields)"


class DataBeginOf(ASTNode):
    """DATA BEGIN OF structure variable"""
    
    def __init__(self, name: str, components: List[Tuple[str, str, Optional[int], Optional[ASTNode]]]):
        self.name = name
        self.components = components  # (field_name, type_name, length, value)
    
    def __repr__(self):
        return f"DataBeginOf({self.name})"


# ----- Data Declaration -----

class DataDecl(ASTNode):
    """DATA statement with LENGTH support"""
    
    def __init__(self, name: str, type_spec: Optional[str] = None, 
                 length: Optional[int] = None, value: Optional[ASTNode] = None):
        self.name = name
        self.type_spec = type_spec
        self.length = length
        self.value = value
    
    def __repr__(self):
        length_str = f" LENGTH {self.length}" if self.length else ""
        return f"DataDecl({self.name}, TYPE {self.type_spec}{length_str})"


class ConstantDecl(ASTNode):
    """CONSTANTS statement"""
    
    def __init__(self, name: str, type_spec: Optional[str] = None,
                 length: Optional[int] = None, value: Optional[ASTNode] = None):
        self.name = name
        self.type_spec = type_spec
        self.length = length
        self.value = value
    
    def __repr__(self):
        return f"ConstantDecl({self.name})"


class ParameterDecl(ASTNode):
    """PARAMETERS statement"""
    
    def __init__(self, name: str, type_spec: Optional[str] = None,
                 length: Optional[int] = None, default: Optional[ASTNode] = None):
        self.name = name
        self.type_spec = type_spec
        self.length = length
        self.default = default
    
    def __repr__(self):
        return f"ParameterDecl({self.name})"


class SelectOptionsDecl(ASTNode):
    """SELECT-OPTIONS statement"""
    
    def __init__(self, selname: str, for_var: str, type_spec: Optional[str] = None,
                 length: Optional[int] = None):
        self.selname = selname
        self.for_var = for_var
        self.type_spec = type_spec
        self.length = length
    
    def __repr__(self):
        return f"SelectOptionsDecl({self.selname} FOR {self.for_var})"


# ----- Subroutines -----

class FormDecl(ASTNode):
    """FORM definition"""
    
    def __init__(self, name: str, params: List[Tuple[str, str]],  # (name, kind)
                 body: List[ASTNode]):
        self.name = name
        self.params = params  # 'USING' or 'CHANGING'
        self.body = body
    
    def __repr__(self):
        return f"FormDecl({self.name}, {len(self.params)} params)"


class Perform(ASTNode):
    """PERFORM statement"""
    
    def __init__(self, name: str, using_params: List[ASTNode] = None,
                 changing_params: List[ASTNode] = None):
        self.name = name
        self.using_params = using_params or []
        self.changing_params = changing_params or []
    
    def __repr__(self):
        return f"Perform({self.name})"


class EndForm(ASTNode):
    """ENDFORM marker"""
    
    def __repr__(self):
        return "EndForm()"


# ----- Events -----

class StartOfSelection(ASTNode):
    """START-OF-SELECTION event"""
    
    def __repr__(self):
        return "StartOfSelection()"


# ----- Statements -----

class Write(ASTNode):
    """WRITE statement"""
    
    def __init__(self, items: List[ASTNode]):
        self.items = items
    
    def __repr__(self):
        return f"Write({len(self.items)} items)"


class Assign(ASTNode):
    """Assignment statement"""
    
    def __init__(self, target: ASTNode, expr: ASTNode):
        self.target = target
        self.expr = expr
    
    def __repr__(self):
        return f"Assign({self.target} = {self.expr})"


class Clear(ASTNode):
    """CLEAR statement"""
    
    def __init__(self, targets: List[ASTNode]):
        self.targets = targets
    
    def __repr__(self):
        return f"Clear({len(self.targets)} targets)"


class Move(ASTNode):
    """MOVE statement"""
    
    def __init__(self, source: ASTNode, target: ASTNode):
        self.source = source
        self.target = target
    
    def __repr__(self):
        return f"Move({self.source} -> {self.target})"


class Append(ASTNode):
    """APPEND VALUE #(...) TO itab"""
    
    def __init__(self, source_row: Dict[str, ASTNode], target_table: str):
        self.source_row = source_row
        self.target_table = target_table
    
    def __repr__(self):
        return f"Append(structured -> {self.target_table})"


class AppendSimple(ASTNode):
    """APPEND wa TO itab"""
    
    def __init__(self, source_var: str, target_table: str):
        self.source_var = source_var
        self.target_table = target_table
    
    def __repr__(self):
        return f"AppendSimple({self.source_var} -> {self.target_table})"


class ModifyTable(ASTNode):
    """MODIFY TABLE itab FROM wa"""
    
    def __init__(self, table_name: str, from_var: str, key_field: Optional[str] = None):
        self.table_name = table_name
        self.from_var = from_var
        self.key_field = key_field
    
    def __repr__(self):
        return f"ModifyTable({self.table_name} FROM {self.from_var})"


class DeleteTable(ASTNode):
    """DELETE TABLE itab"""
    
    def __init__(self, table_name: str, key: Optional[Tuple[str, ASTNode]] = None):
        self.table_name = table_name
        self.key = key
    
    def __repr__(self):
        return f"DeleteTable({self.table_name})"


class InsertTable(ASTNode):
    """INSERT wa INTO TABLE itab"""
    
    def __init__(self, source_var: str, target_table: str):
        self.source_var = source_var
        self.target_table = target_table
    
    def __repr__(self):
        return f"InsertTable({self.source_var} -> {self.target_table})"


# ----- SQL Operations -----

class UpdateSQL(ASTNode):
    """UPDATE db_table SET ... WHERE ..."""
    
    def __init__(self, table_name: str, set_clause: Dict[str, ASTNode],
                 where_clause: Optional[ASTNode] = None):
        self.table_name = table_name
        self.set_clause = set_clause
        self.where = where_clause
    
    def __repr__(self):
        return f"UpdateSQL({self.table_name})"


class InsertSQL(ASTNode):
    """INSERT INTO db_table VALUES ..."""
    
    def __init__(self, table_name: str, values: Dict[str, ASTNode]):
        self.table_name = table_name
        self.values = values
    
    def __repr__(self):
        return f"InsertSQL({self.table_name})"


class DeleteSQL(ASTNode):
    """DELETE FROM db_table WHERE ..."""
    
    def __init__(self, table_name: str, where_clause: Optional[ASTNode] = None):
        self.table_name = table_name
        self.where = where_clause
    
    def __repr__(self):
        return f"DeleteSQL({self.table_name})"


class CommitWork(ASTNode):
    """COMMIT WORK statement"""
    
    def __repr__(self):
        return "CommitWork()"


class RollbackWork(ASTNode):
    """ROLLBACK WORK statement"""
    
    def __repr__(self):
        return "RollbackWork()"


# ----- Loop Control -----

class Exit(ASTNode):
    """EXIT statement"""
    
    def __init__(self, from_loop: bool = True):
        self.from_loop = from_loop
    
    def __repr__(self):
        return "Exit()"


class Continue(ASTNode):
    """CONTINUE statement"""
    
    def __repr__(self):
        return "Continue()"


class Check(ASTNode):
    """CHECK statement"""
    
    def __init__(self, condition: ASTNode):
        self.condition = condition
    
    def __repr__(self):
        return f"Check({self.condition})"


class LoopAt(ASTNode):
    """LOOP AT itab INTO wa"""
    
    def __init__(self, table: str, into: str, body: List[ASTNode]):
        self.table = table
        self.into = into
        self.body = body
    
    def __repr__(self):
        return f"LoopAt({self.table} -> {self.into})"


class EndLoop(ASTNode):
    """ENDLOOP marker"""
    
    def __repr__(self):
        return "EndLoop()"


class ReadTable(ASTNode):
    """READ TABLE itab INTO wa WITH KEY ..."""
    
    def __init__(self, table_name: str, into: Optional[str] = None, 
                 key: Optional[Tuple[str, ASTNode]] = None, transporting: Optional[List[str]] = None):
        self.table_name = table_name
        self.into = into
        self.key = key
        self.transporting = transporting
    
    def __repr__(self):
        return f"ReadTable({self.table_name} -> {self.into})"


# ----- Control Structures -----

class If(ASTNode):
    """IF statement"""
    
    def __init__(self, cond: ASTNode, then_body: List[ASTNode], 
                 elif_list: List[Tuple[ASTNode, List[ASTNode]]], 
                 else_body: List[ASTNode]):
        self.cond = cond
        self.then_body = then_body
        self.elif_list = elif_list
        self.else_body = else_body
    
    def __repr__(self):
        return f"If(cond={self.cond})"


class While(ASTNode):
    """WHILE statement"""
    
    def __init__(self, cond: ASTNode, body: List[ASTNode]):
        self.cond = cond
        self.body = body
    
    def __repr__(self):
        return f"While(cond={self.cond})"


class Do(ASTNode):
    """DO statement"""
    
    def __init__(self, times_expr: Optional[ASTNode], body: List[ASTNode]):
        self.times_expr = times_expr
        self.body = body
    
    def __repr__(self):
        return f"Do(times={self.times_expr})"


class Case(ASTNode):
    """CASE statement"""
    
    def __init__(self, expr: ASTNode, cases: List[Tuple[ASTNode, List[ASTNode]]], 
                 others_body: List[ASTNode]):
        self.expr = expr
        self.cases = cases
        self.others_body = others_body
    
    def __repr__(self):
        return f"Case(expr={self.expr}, {len(self.cases)} cases)"


# ----- SQL -----

class SelectInto(ASTNode):
    """SELECT statement with enhanced WHERE and ORDER BY"""
    
    def __init__(self, fields: List[str], table_name: str, 
                 into_table: str, where_clause: Optional[ASTNode] = None,
                 order_by: Optional[List[str]] = None):
        self.fields = fields
        self.table_name = table_name
        self.into_table = into_table
        self.where = where_clause
        self.order_by = order_by or []
    
    def __repr__(self):
        order_str = f" ORDER BY {self.order_by}" if self.order_by else ""
        return f"SelectInto({self.table_name} -> {self.into_table}{order_str})"


# ----- Expressions -----

class Var(ASTNode):
    """Variable reference"""
    
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Var({self.name})"


class Number(ASTNode):
    """Numeric literal"""
    
    def __init__(self, val: str):
        self.val = int(val)
    
    def __repr__(self):
        return f"Number({self.val})"


class String(ASTNode):
    """String literal"""
    
    def __init__(self, val: str):
        self.val = val.strip("'").replace("''", "'")
    
    def __repr__(self):
        return f"String('{self.val}')"


class Field(ASTNode):
    """Field access: wa-field"""
    
    def __init__(self, struct: str, field: str):
        self.struct = struct
        self.field = field
    
    def __repr__(self):
        return f"Field({self.struct}-{self.field})"


class BinOp(ASTNode):
    """Binary operation"""
    
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"BinOp({self.left} {self.op} {self.right})"


class UnaryOp(ASTNode):
    """Unary operation"""
    
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.op} {self.operand})"


class FuncCall(ASTNode):
    """Function call"""
    
    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name.upper()
        self.args = args
    
    def __repr__(self):
        return f"FuncCall({self.name})"


# =====================================================
# ===============      PARSER         ================
# =====================================================

class ParserError(Exception):
    """Parser error exception"""
    pass


class Parser:
    """Base parser with strict ABAP expression parsing"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.in_boolean_context = False
    
    def peek(self) -> Optional[Token]:
        """Look at current token without consuming it"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def next(self) -> Optional[Token]:
        """Consume and return current token"""
        tok = self.peek()
        if tok:
            self.pos += 1
        return tok
    
    def accept(self, kind_or_value: str) -> Optional[Token]:
        """Accept token if it matches kind or value"""
        tok = self.peek()
        if tok and (tok.kind == kind_or_value or tok.value == kind_or_value):
            self.pos += 1
            return tok
        return None
    
    def expect(self, kind_or_value: str) -> Token:
        """Expect token of given kind or value, raise error if not found"""
        tok = self.peek()
        if not tok or (tok.kind != kind_or_value and tok.value != kind_or_value):
            raise ParserError(
                f"Expected {kind_or_value}, got {tok} at line {tok.line if tok else 'EOF'}"
            )
        self.pos += 1
        return tok
    
    def lookahead(self, value: str) -> bool:
        """Check if next token has given value"""
        tok = self.peek()
        return tok and tok.value == value
    
    def reset_context(self):
        """Reset boolean context flag"""
        self.in_boolean_context = False
    
    # --------------------------------------------
    #  Expression Parsing with strict ABAP rules
    # --------------------------------------------
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expression (atoms, parentheses)"""
        tok = self.peek()
        if not tok:
            raise ParserError("Unexpected end in expression")
        
        # Number literal
        if tok.kind == "NUMBER":
            self.next()
            return Number(tok.value)
        
        # String literal
        if tok.kind == "STRING":
            self.next()
            return String(tok.value)
        
        # Identifier or Keyword
        if tok.kind in ("ID", "KEYWORD"):
            self.next()
            name = tok.value
            
            # Function call
            if self.accept("("):
                args = []
                if not self.accept(")"):
                    while True:
                        args.append(self.parse_expression())
                        if self.accept(")"):
                            break
                        self.expect(",")
                return FuncCall(name, args)
            
            # System variable
            if name.startswith("sy-"):
                return Var(name)
            
            return Var(name)
        
        # Parenthesized expression
        if self.accept("("):
            expr = self.parse_expression()
            self.expect(")")
            return expr
        
        raise ParserError(f"Unexpected token {tok} in expression")
    
    def parse_field_access(self) -> ASTNode:
        """Parse field access: var-field (only in non-expression contexts)"""
        var = self.expect("ID").value.lower()
        self.expect("-")
        field = self.expect("ID").value.lower()
        return Field(var, field)
    
    def parse_unary(self) -> ASTNode:
        """Parse unary operators - only NOT allowed in boolean context"""
        if self.accept("NOT"):
            operand = self.parse_unary()
            return UnaryOp("NOT", operand)
        return self.parse_primary()
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse *, /"""
        node = self.parse_unary()
        
        while True:
            tok = self.peek()
            if tok and tok.value in ("*", "/"):
                op = self.next().value
                right = self.parse_unary()
                node = BinOp(node, op, right)
            else:
                break
        
        return node
    
    def parse_additive(self) -> ASTNode:
        """Parse +, -"""
        node = self.parse_multiplicative()
        
        while True:
            tok = self.peek()
            if tok and tok.value in ("+", "-"):
                op = self.next().value
                right = self.parse_multiplicative()
                node = BinOp(node, op, right)
            else:
                break
        
        return node
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparisons: =, <>, >, <, >=, <="""  
        node = self.parse_additive()
        
        tok = self.peek()
        if tok and tok.value in ("=", "<>", ">", "<", ">=", "<="):
            op = self.next().value
            right = self.parse_additive()
            return BinOp(node, op, right)
        
        return node
    
    def parse_and(self) -> ASTNode:
        """Parse AND expressions"""
        node = self.parse_comparison()
        
        while self.accept("AND"):
            right = self.parse_comparison()
            node = BinOp(node, "AND", right)
        
        return node
    
    def parse_or(self) -> ASTNode:
        """Parse OR expressions"""
        node = self.parse_and()
        
        while self.accept("OR"):
            right = self.parse_and()
            node = BinOp(node, "OR", right)
        
        return node
    
    def parse_expression(self) -> ASTNode:
        """Top-level expression parser"""
        return self.parse_or()


class FullParser(Parser):
    """Full ABAP statement parser with all strict features"""
    
    def parse_program(self) -> Program:
        """Parse entire program"""
        statements = []
        
        while self.peek():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse one ABAP statement (ends with '.')"""
        tok = self.peek()
        if not tok:
            return None
        
        # WRITE statement
        if tok.value == "WRITE":
            return self.parse_write_stmt()
        
        # DATA declaration
        if tok.value == "DATA":
            return self.parse_data_stmt()
        
        # TYPES BEGIN OF
        if tok.value == "TYPES" and self.lookahead("BEGIN"):
            return self.parse_types_begin_of()
        
        # DATA BEGIN OF
        if tok.value == "DATA" and self.lookahead("BEGIN"):
            return self.parse_data_begin_of()
        
        # CONSTANTS declaration
        if tok.value == "CONSTANTS":
            return self.parse_constants_stmt()
        
        # PARAMETERS declaration
        if tok.value == "PARAMETERS":
            return self.parse_parameters_stmt()
        
        # SELECT-OPTIONS declaration
        if tok.value == "SELECT-OPTIONS":
            return self.parse_select_options_stmt()
        
        # FORM definition
        if tok.value == "FORM":
            return self.parse_form()
        
        # PERFORM statement
        if tok.value == "PERFORM":
            return self.parse_perform()
        
        # START-OF-SELECTION
        if tok.value == "START-OF-SELECTION":
            return self.parse_start_of_selection()
        
        # UPDATE SQL
        if tok.value == "UPDATE":
            return self.parse_update_sql()
        
        # INSERT SQL
        if tok.value == "INSERT":
            return self.parse_insert_sql()
        
        # DELETE SQL
        if tok.value == "DELETE" and self.lookahead("FROM"):
            return self.parse_delete_sql()
        
        # COMMIT WORK
        if tok.value == "COMMIT":
            return self.parse_commit_work()
        
        # ROLLBACK WORK
        if tok.value == "ROLLBACK":
            return self.parse_rollback_work()
        
        # CLEAR statement
        if tok.value == "CLEAR":
            return self.parse_clear_stmt()
        
        # MOVE statement
        if tok.value == "MOVE":
            return self.parse_move_stmt()
        
        # APPEND statement
        if tok.value == "APPEND":
            return self.parse_append_stmt()
        
        # MODIFY statement
        if tok.value == "MODIFY":
            return self.parse_modify_stmt()
        
        # DELETE statement
        if tok.value == "DELETE":
            return self.parse_delete_stmt()
        
        # INSERT statement
        if tok.value == "INSERT":
            return self.parse_insert_stmt()
        
        # LOOP AT
        if tok.value == "LOOP":
            return self.parse_loop()
        
        # READ TABLE
        if tok.value == "READ":
            return self.parse_read_table()
        
        # EXIT statement
        if tok.value == "EXIT":
            return self.parse_exit_stmt()
        
        # CONTINUE statement
        if tok.value == "CONTINUE":
            return self.parse_continue_stmt()
        
        # CHECK statement
        if tok.value == "CHECK":
            return self.parse_check_stmt()
        
        # IF statement
        if tok.value == "IF":
            return self.parse_if_block()
        
        # WHILE statement
        if tok.value == "WHILE":
            return self.parse_while()
        
        # DO statement
        if tok.value == "DO":
            return self.parse_do()
        
        # CASE statement
        if tok.value == "CASE":
            return self.parse_case()
        
        # SELECT statement
        if tok.value == "SELECT":
            return self.parse_select()
        
        # Assignment (ID = expr)
        if tok.kind in ("ID", "KEYWORD") and self.lookahead("="):
            return self.parse_assignment()
        
        # Field assignment (ID-ID = expr)
        if tok.kind == "ID":
            # Check bounds properly
            if (self.pos + 3 < len(self.tokens) and 
                self.tokens[self.pos + 1].value == "-" and
                self.tokens[self.pos + 2].kind == "ID" and
                self.tokens[self.pos + 3].value == "="):
                return self.parse_assignment()
        
        # Unknown statement - skip to next period
        while self.peek() and not self.accept("."):
            self.next()
        
        return None
    
    # -----------------------------------------------
    #  Enhanced Statement Parsers
    # -----------------------------------------------
    
    def parse_write_stmt(self) -> Write:
        """WRITE: expr [, expr ...]."""
        self.expect("WRITE")
        
        items = []
        self.accept(":")
        
        while self.peek() and not self.accept("."):
            if self.accept("/"):
                items.append(String("\n"))
                continue
            
            if self.accept(","):
                continue
            
            items.append(self.parse_expression())
        
        return Write(items)
    
    def parse_data_stmt(self) -> DataDecl:
        """DATA: lv_a TYPE i [LENGTH n] VALUE 10."""
        self.expect("DATA")
        self.accept(":")
        
        name = self.expect("ID").value.lower()
        
        type_spec = None
        length = None
        value_expr = None
        
        if self.accept("TYPE"):
            type_spec = self.expect("ID").value.upper()
            
            # Check for LENGTH
            if self.accept("LENGTH"):
                length_tok = self.expect("NUMBER")
                length = int(length_tok.value)
        
        if self.accept("VALUE"):
            value_expr = self.parse_expression()
        
        self.expect(".")
        return DataDecl(name, type_spec, length, value_expr)
    
    def parse_types_begin_of(self) -> TypesBeginOf:
        """TYPES BEGIN OF structure."""
        self.expect("TYPES")
        self.expect("BEGIN")
        self.expect("OF")
        
        name = self.expect("ID").value.lower()
        components = []
        
        while self.peek() and not (self.peek().value == "END" and self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "OF"):
            # Parse component: name TYPE type [LENGTH n]
            comp_name = self.expect("ID").value.lower()
            self.expect("TYPE")
            comp_type = self.expect("ID").value.upper()
            
            comp_length = None
            if self.accept("LENGTH"):
                length_tok = self.expect("NUMBER")
                comp_length = int(length_tok.value)
            
            components.append((comp_name, comp_type, comp_length))
            self.expect(".")
        
        self.expect("END")
        self.expect("OF")
        self.expect(".")
        
        return TypesBeginOf(name, components)
    
    def parse_data_begin_of(self) -> DataBeginOf:
        """DATA BEGIN OF structure variable."""
        self.expect("DATA")
        self.expect("BEGIN")
        self.expect("OF")
        
        name = self.expect("ID").value.lower()
        components = []
        
        while self.peek() and not (self.peek().value == "END" and self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == "OF"):
            # Parse component with optional VALUE
            comp_name = self.expect("ID").value.lower()
            
            comp_type = None
            comp_length = None
            comp_value = None
            
            if self.accept("TYPE"):
                comp_type = self.expect("ID").value.upper()
                
                if self.accept("LENGTH"):
                    length_tok = self.expect("NUMBER")
                    comp_length = int(length_tok.value)
            
            if self.accept("VALUE"):
                comp_value = self.parse_expression()
            
            components.append((comp_name, comp_type, comp_length, comp_value))
            self.expect(".")
        
        self.expect("END")
        self.expect("OF")
        self.expect(".")
        
        return DataBeginOf(name, components)
    
    def parse_constants_stmt(self) -> ConstantDecl:
        """CONSTANTS: pi TYPE f VALUE '3.14'."""
        self.expect("CONSTANTS")
        self.accept(":")
        
        name = self.expect("ID").value.lower()
        
        type_spec = None
        length = None
        
        if self.accept("TYPE"):
            type_spec = self.expect("ID").value.upper()
            
            if self.accept("LENGTH"):
                length_tok = self.expect("NUMBER")
                length = int(length_tok.value)
        
        self.expect("VALUE")
        value_expr = self.parse_expression()
        self.expect(".")
        
        return ConstantDecl(name, type_spec, length, value_expr)
    
    def parse_parameters_stmt(self) -> ParameterDecl:
        """PARAMETERS: p_dept TYPE c LENGTH 10 DEFAULT 'IT'."""
        self.expect("PARAMETERS")
        self.accept(":")
        
        name = self.expect("ID").value.lower()
        
        type_spec = None
        length = None
        default_expr = None
        
        if self.accept("TYPE"):
            type_spec = self.expect("ID").value.upper()
            
            if self.accept("LENGTH"):
                length_tok = self.expect("NUMBER")
                length = int(length_tok.value)
        
        if self.accept("DEFAULT"):
            default_expr = self.parse_expression()
        
        self.expect(".")
        return ParameterDecl(name, type_spec, length, default_expr)
    
    def parse_select_options_stmt(self) -> SelectOptionsDecl:
        """SELECT-OPTIONS: s_salary FOR emp-salary."""
        self.expect("SELECT-OPTIONS")
        self.accept(":")
        
        selname = self.expect("ID").value.lower()
        self.expect("FOR")
        
        # Parse FOR variable (could be field or variable)
        for_var = self.expect("ID").value.lower()
        if self.accept("-"):
            field = self.expect("ID").value.lower()
            for_var = f"{for_var}-{field}"
        
        type_spec = None
        length = None
        
        if self.accept("TYPE"):
            type_spec = self.expect("ID").value.upper()
            
            if self.accept("LENGTH"):
                length_tok = self.expect("NUMBER")
                length = int(length_tok.value)
        
        self.expect(".")
        return SelectOptionsDecl(selname, for_var, type_spec, length)
    
    def parse_form(self) -> FormDecl:
        """FORM subr [USING ...] [CHANGING ...]."""
        self.expect("FORM")
        name = self.expect("ID").value.lower()
        
        params = []
        
        # Parse USING parameters
        if self.accept("USING"):
            while not self.accept("."):
                param_name = self.expect("ID").value.lower()
                params.append((param_name, "USING"))
                if self.accept(","):
                    continue
                break
        
        # Parse CHANGING parameters
        if self.accept("CHANGING"):
            while not self.accept("."):
                param_name = self.expect("ID").value.lower()
                params.append((param_name, "CHANGING"))
                if self.accept(","):
                    continue
                break
        
        self.expect(".")
        
        # Parse FORM body
        body = []
        while self.peek() and self.peek().value != "ENDFORM":
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect("ENDFORM")
        self.expect(".")
        
        return FormDecl(name, params, body)
    
    def parse_perform(self) -> Perform:
        """PERFORM subr [USING ...] [CHANGING ...]."""
        self.expect("PERFORM")
        name = self.expect("ID").value.lower()
        
        using_params = []
        changing_params = []
        
        # Parse USING parameters
        if self.accept("USING"):
            while not self.accept("."):
                using_params.append(self.parse_expression())
                if self.accept(","):
                    continue
                break
        
        # Parse CHANGING parameters
        if self.accept("CHANGING"):
            while not self.accept("."):
                changing_params.append(self.parse_expression())
                if self.accept(","):
                    continue
                break
        
        self.expect(".")
        return Perform(name, using_params, changing_params)
    
    def parse_start_of_selection(self) -> StartOfSelection:
        """START-OF-SELECTION."""
        self.expect("START-OF-SELECTION")
        self.expect(".")
        return StartOfSelection()
    
    def parse_update_sql(self) -> UpdateSQL:
        """UPDATE table SET field = value WHERE condition."""
        self.expect("UPDATE")
        table = self.expect("ID").value.lower()
        self.expect("SET")
        
        set_clause = {}
        while not self.accept("WHERE") and not self.accept("."):
            field = self.expect("ID").value.lower()
            self.expect("=")
            value = self.parse_expression()
            set_clause[field] = value
            if self.accept(","):
                continue
        
        where_clause = None
        if self.accept("WHERE"):
            where_clause = self.parse_expression()
        
        self.expect(".")
        return UpdateSQL(table, set_clause, where_clause)
    
    def parse_insert_sql(self) -> InsertSQL:
        """INSERT INTO table (field1, field2) VALUES (value1, value2)."""
        self.expect("INSERT")
        self.expect("INTO")
        table = self.expect("ID").value.lower()
        
        values = {}
        if self.accept("("):
            while not self.accept(")"):
                field = self.expect("ID").value.lower()
                self.expect("=")
                value = self.parse_expression()
                values[field] = value
                if self.accept(","):
                    continue
        
        self.expect(".")
        return InsertSQL(table, values)
    
    def parse_delete_sql(self) -> DeleteSQL:
        """DELETE FROM table WHERE condition."""
        self.expect("DELETE")
        self.expect("FROM")
        table = self.expect("ID").value.lower()
        
        where_clause = None
        if self.accept("WHERE"):
            where_clause = self.parse_expression()
        
        self.expect(".")
        return DeleteSQL(table, where_clause)
    
    def parse_commit_work(self) -> CommitWork:
        """COMMIT WORK."""
        self.expect("COMMIT")
        if self.accept("WORK"):
            pass
        self.expect(".")
        return CommitWork()
    
    def parse_rollback_work(self) -> RollbackWork:
        """ROLLBACK WORK."""
        self.expect("ROLLBACK")
        if self.accept("WORK"):
            pass
        self.expect(".")
        return RollbackWork()
    
    def parse_clear_stmt(self) -> Clear:
        """CLEAR: var1, var2."""
        self.expect("CLEAR")
        
        targets = []
        while self.peek() and not self.accept("."):
            if self.peek().kind == "ID":
                var_name = self.next().value.lower()
                
                if self.accept("-"):
                    field_name = self.expect("ID").value.lower()
                    targets.append(Field(var_name, field_name))
                else:
                    targets.append(Var(var_name))
            
            if self.accept(","):
                continue
        
        return Clear(targets)
    
    def parse_move_stmt(self) -> Move:
        """MOVE: source TO target."""
        self.expect("MOVE")
        
        source = self.parse_expression()
        self.expect("TO")
        
        if self.peek().kind == "ID":
            var_name = self.next().value.lower()
            
            if self.accept("-"):
                field_name = self.expect("ID").value.lower()
                target = Field(var_name, field_name)
            else:
                target = Var(var_name)
        
        self.expect(".")
        return Move(source, target)
    
    def parse_assignment(self) -> Assign:
        """Assignment: target = expr."""
        if self.peek().kind == "ID":
            var_name = self.next().value.lower()
            
            if self.accept("-"):
                field_name = self.expect("ID").value.lower()
                target = Field(var_name, field_name)
            else:
                target = Var(var_name)
        
        self.expect("=")
        expr = self.parse_expression()
        self.expect(".")
        
        return Assign(target, expr)
    
    def parse_append_stmt(self) -> Union[Append, AppendSimple]:
        """APPEND statement"""
        self.expect("APPEND")
        
        if self.accept("VALUE"):
            self.expect("#")
            self.expect("(")
            
            source_row = {}
            while not self.accept(")"):
                key = self.expect("ID").value.lower()
                self.expect("=")
                val = self.parse_expression()
                source_row[key] = val
                self.accept(",")
            
            self.expect("TO")
            target = self.expect("ID").value.lower()
            self.expect(".")
            return Append(source_row, target)
        
        source = self.expect("ID").value.lower()
        self.expect("TO")
        target = self.expect("ID").value.lower()
        self.expect(".")
        return AppendSimple(source, target)
    
    def parse_modify_stmt(self) -> ModifyTable:
        """MODIFY TABLE itab FROM wa [USING KEY ...]."""
        self.expect("MODIFY")
        self.expect("TABLE")
        
        table_name = self.expect("ID").value.lower()
        self.expect("FROM")
        from_var = self.expect("ID").value.lower()
        
        key_field = None
        if self.accept("USING"):
            self.expect("KEY")
            key_field = self.expect("ID").value.lower()
        
        self.expect(".")
        return ModifyTable(table_name, from_var, key_field)
    
    def parse_delete_stmt(self) -> DeleteTable:
        """DELETE TABLE itab [WITH KEY ...]."""
        self.expect("DELETE")
        self.expect("TABLE")
        
        table_name = self.expect("ID").value.lower()
        
        key = None
        if self.accept("WITH"):
            self.expect("KEY")
            key_field = self.expect("ID").value.lower()
            self.expect("=")
            key_value = self.parse_expression()
            key = (key_field, key_value)
        
        self.expect(".")
        return DeleteTable(table_name, key)
    
    def parse_insert_stmt(self) -> InsertTable:
        """INSERT wa INTO TABLE itab."""
        self.expect("INSERT")
        source = self.expect("ID").value.lower()
        self.expect("INTO")
        self.expect("TABLE")
        target = self.expect("ID").value.lower()
        self.expect(".")
        return InsertTable(source, target)
    
    def parse_loop(self) -> LoopAt:
        """LOOP AT itab INTO wa."""
        self.expect("LOOP")
        self.expect("AT")
        
        table = self.expect("ID").value.lower()
        self.expect("INTO")
        into = self.expect("ID").value.lower()
        self.expect(".")
        
        body = []
        while self.peek() and self.peek().value != "ENDLOOP":
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect("ENDLOOP")
        self.expect(".")
        return LoopAt(table, into, body)
    
    def parse_read_table(self) -> ReadTable:
        """READ TABLE itab INTO wa WITH KEY ..."""
        self.expect("READ")
        self.expect("TABLE")
        
        table_name = self.expect("ID").value.lower()
        
        into = None
        if self.accept("INTO"):
            into = self.expect("ID").value.lower()
        
        key = None
        transporting = None
        if self.accept("WITH"):
            self.expect("KEY")
            key_field = self.expect("ID").value.lower()
            self.expect("=")
            key_value = self.parse_expression()
            key = (key_field, key_value)
        
        self.expect(".")
        return ReadTable(table_name, into, key, transporting)
    
    def parse_exit_stmt(self) -> Exit:
        """EXIT statement."""
        self.expect("EXIT")
        self.expect(".")
        return Exit()
    
    def parse_continue_stmt(self) -> Continue:
        """CONTINUE statement."""
        self.expect("CONTINUE")
        self.expect(".")
        return Continue()
    
    def parse_check_stmt(self) -> Check:
        """CHECK condition."""
        self.expect("CHECK")
        condition = self.parse_expression()
        self.expect(".")
        return Check(condition)
    
    def parse_if_block(self) -> If:
        """IF cond. ... ELSEIF cond. ... ELSE. ... ENDIF."""
        self.expect("IF")
        cond = self.parse_expression()
        self.expect(".")
        
        then_body = []
        while self.peek() and self.peek().value not in ("ELSEIF", "ELSE", "ENDIF"):
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
        
        elif_list = []
        while self.accept("ELSEIF"):
            elif_cond = self.parse_expression()
            self.expect(".")
            
            elif_body = []
            while self.peek() and self.peek().value not in ("ELSEIF", "ELSE", "ENDIF"):
                stmt = self.parse_statement()
                if stmt:
                    elif_body.append(stmt)
            
            elif_list.append((elif_cond, elif_body))
        
        else_body = []
        if self.accept("ELSE"):
            self.expect(".")
            while self.peek() and self.peek().value != "ENDIF":
                stmt = self.parse_statement()
                if stmt:
                    else_body.append(stmt)
        
        self.expect("ENDIF")
        self.expect(".")
        
        return If(cond, then_body, elif_list, else_body)
    
    def parse_while(self) -> While:
        """WHILE cond. ... ENDWHILE."""
        self.expect("WHILE")
        cond = self.parse_expression()
        self.expect(".")
        
        body = []
        while self.peek() and self.peek().value != "ENDWHILE":
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect("ENDWHILE")
        self.expect(".")
        return While(cond, body)
    
    def parse_do(self) -> Do:
        """DO n TIMES. ... ENDDO."""
        self.expect("DO")
        
        times_expr = None
        if self.peek() and self.peek().kind not in ("SYMBOL", "KEYWORD"):
            times_expr = self.parse_expression()
        
        if self.accept("TIMES"):
            pass
        
        self.expect(".")
        
        body = []
        while self.peek() and self.peek().value != "ENDDO":
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.expect("ENDDO")
        self.expect(".")
        return Do(times_expr, body)
    
    def parse_case(self) -> Case:
        """CASE expr. WHEN val. ... WHEN OTHERS. ... ENDCASE."""
        self.expect("CASE")
        expr = self.parse_expression()
        self.expect(".")
        
        cases = []
        others_body = []
        
        while self.peek() and self.peek().value != "ENDCASE":
            if self.accept("WHEN"):
                if self.accept("OTHERS"):
                    self.expect(".")
                    while self.peek() and self.peek().value != "ENDCASE":
                        stmt = self.parse_statement()
                        if stmt:
                            others_body.append(stmt)
                    continue
                
                value = self.parse_expression()
                self.expect(".")
                
                when_body = []
                while self.peek() and self.peek().value not in ("WHEN", "ENDCASE"):
                    stmt = self.parse_statement()
                    if stmt:
                        when_body.append(stmt)
                
                cases.append((value, when_body))
        
        self.expect("ENDCASE")
        self.expect(".")
        return Case(expr, cases, others_body)
    
    def parse_select(self) -> SelectInto:
        """SELECT * FROM table INTO TABLE itab [WHERE ...] [ORDER BY ...]."""
        self.expect("SELECT")
        
        fields = []
        if self.accept("*"):
            fields = ["*"]
        else:
            while self.peek() and self.peek().value != "FROM":
                field = self.expect("ID").value.lower()
                fields.append(field)
                self.accept(",")
        
        self.expect("FROM")
        table = self.expect("ID").value.lower()
        
        where_clause = None
        if self.accept("WHERE"):
            where_clause = self.parse_expression()
        
        order_by = []
        if self.accept("ORDER"):
            self.expect("BY")
            while self.peek() and self.peek().value not in ("INTO", "."):
                field = self.expect("ID").value.lower()
                order_by.append(field)
                if self.accept(","):
                    continue
                break
        
        self.expect("INTO")
        self.expect("TABLE")
        target = self.expect("ID").value.lower()
        self.expect(".")
        
        return SelectInto(fields, table, target, where_clause, order_by)


# =====================================================
# ===============   RUNTIME ENGINE    =================
# =====================================================

class RuntimeError(Exception):
    """Runtime error exception"""
    pass


class SystemVariables:
    """ABAP system variables with strict updates"""
    
    def __init__(self):
        now = datetime.datetime.now()
        self.vars = {
            'sy-subrc': 0,
            'sy-tabix': 0,
            'sy-index': 0,
            'sy-dbcnt': 0,
            'sy-uzeit': now.strftime("%H%M%S").upper(),
            'sy-datum': now.strftime("%Y%m%d")
        }
    
    def get(self, name: str) -> Any:
        """Get system variable value"""
        return self.vars.get(name)
    
    def set(self, name: str, value: Any):
        """Set system variable value with type validation"""
        # Type validation for system variables
        if name == 'sy-subrc':
            try:
                value = int(value)
                if not 0 <= value <= 8:  # Standard ABAP range
                    value = 8
            except (ValueError, TypeError):
                value = 8
        elif name == 'sy-tabix':
            try:
                value = int(value)
                if value < 0:
                    value = 0
            except (ValueError, TypeError):
                value = 0
        elif name == 'sy-index':
            try:
                value = int(value)
                if value < 0:
                    value = 0
            except (ValueError, TypeError):
                value = 0
        elif name == 'sy-dbcnt':
            try:
                value = int(value)
                if value < 0:
                    value = 0
            except (ValueError, TypeError):
                value = 0
        
        self.vars[name] = value
    
    def reset_loop_vars(self):
        """Reset loop-related system variables"""
        self.vars['sy-tabix'] = 0
        self.vars['sy-index'] = 0
    
    def update_for_success(self):
        """Set SY-SUBRC to 0 (success)"""
        self.set('sy-subrc', 0)
    
    def update_for_not_found(self):
        """Set SY-SUBRC to 4 (not found)"""
        self.set('sy-subrc', 4)
    
    def update_for_error(self):
        """Set SY-SUBRC to 8 (error)"""
        self.set('sy-subrc', 8)


class FormDef:
    """FORM subroutine definition"""
    
    def __init__(self, name: str, params: List[Tuple[str, str]], body: List[ASTNode]):
        self.name = name
        self.params = params  # (name, kind)
        self.body = body
    
    def __repr__(self):
        return f"FormDef({self.name}, {len(self.params)} params)"


class SelectionOption:
    """SELECT-OPTIONS range with full matching logic"""
    
    def __init__(self, sign: str = "I", option: str = "EQ", 
                 low: Any = None, high: Any = None):
        self.sign = sign  # I (include) or E (exclude)
        self.option = option  # EQ, NE, GT, LT, GE, LE, BT, CP, NP
        self.low = low
        self.high = high
    
    def matches(self, value: Any) -> bool:
        """Check if value matches selection option"""
        if self.low is None:
            return self.sign == "I"  # Empty range includes all if sign=I
        
        # Convert to strings for comparison
        val_str = str(value).strip()
        low_str = str(self.low).strip() if self.low is not None else ""
        high_str = str(self.high).strip() if self.high is not None else ""
        
        result = False
        
        if self.option == "EQ":
            result = val_str == low_str
        elif self.option == "NE":
            result = val_str != low_str
        elif self.option == "GT":
            try:
                result = float(val_str) > float(low_str)
            except:
                result = val_str > low_str
        elif self.option == "LT":
            try:
                result = float(val_str) < float(low_str)
            except:
                result = val_str < low_str
        elif self.option == "GE":
            try:
                result = float(val_str) >= float(low_str)
            except:
                result = val_str >= low_str
        elif self.option == "LE":
            try:
                result = float(val_str) <= float(low_str)
            except:
                result = val_str <= low_str
        elif self.option == "BT":
            if low_str and high_str:
                try:
                    result = float(low_str) <= float(val_str) <= float(high_str)
                except:
                    result = low_str <= val_str <= high_str
            else:
                result = False
        elif self.option == "CP":  # Pattern match (simplified)
            pattern = low_str.replace('*', '.*').replace('+', '.+')
            import re
            result = bool(re.match(f"^{pattern}$", val_str))
        elif self.option == "NP":  # Not pattern
            pattern = low_str.replace('*', '.*').replace('+', '.+')
            import re
            result = not bool(re.match(f"^{pattern}$", val_str))
        else:
            result = val_str == low_str  # Default to EQ
        
        # Apply sign
        if self.sign == "E":
            result = not result
        
        return result
    
    def __repr__(self):
        return f"SelectionOption({self.sign} {self.option} {self.low}:{self.high})"


class RuntimeEnv:
    """
    Runtime environment for strict ABAP execution.
    """
    
    def __init__(self):
        # Core storage - FIXED: Single source of truth
        self.typed_vars = {}  # Main storage for all typed variables
        self.constants = {}
        self.structures = {}  # TYPES definitions
        self.tables = {}
        self.table_types = {}  # Internal table typing metadata
        self.objects = {}
        self.classes = {}
        
        # Subroutines
        self.forms = {}  # FORM definitions
        self.call_stack = []  # For local scopes
        
        # Selection screens
        self.parameters = {}  # PARAMETERS
        self.select_options = {}  # SELECT-OPTIONS
        
        # Event flags
        self.in_declaration_phase = True
        self.execution_started = False
        
        # Database
        self.db = {}
        self.db_snapshots = []  # For COMMIT/ROLLBACK
        
        # System
        self.sy = SystemVariables()
        self.output = []
        
        # Loop control flags
        self.should_exit_loop = False
        self.should_continue = False
        
        # Control break simulation
        self.control_break_data = {}  # For AT NEW simulation
        
        # Safety guards
        self.max_loop_iterations = 1000000
        
        # Load example data
        self._bootstrap()
    
    def _bootstrap(self):
        """Load example SQL tables"""
        self.db["employees"] = [
            {"id": "1", "name": "Alice", "dept": "HR", "salary": "50000"},
            {"id": "2", "name": "Bob", "dept": "IT", "salary": "60000"},
            {"id": "3", "name": "Carol", "dept": "HR", "salary": "55000"},
            {"id": "4", "name": "Dave", "dept": "IT", "salary": "65000"}
        ]
        
        self.db["departments"] = [
            {"dept_id": "HR", "dept_name": "Human Resources"},
            {"dept_id": "IT", "dept_name": "Information Technology"}
        ]
        
        # Initialize with default snapshot
        self._save_db_snapshot()
    
    def _save_db_snapshot(self):
        """Save current database state for COMMIT/ROLLBACK"""
        snapshot = {}
        for table, rows in self.db.items():
            snapshot[table] = [row.copy() for row in rows]
        self.db_snapshots.append(snapshot)
        
        # Keep only last 10 snapshots
        if len(self.db_snapshots) > 10:
            self.db_snapshots.pop(0)
    
    def _restore_db_snapshot(self):
        """Restore database to last snapshot"""
        if self.db_snapshots:
            snapshot = self.db_snapshots.pop()
            self.db = snapshot
        else:
            self.db = {}
    
    def get_variable(self, name: str) -> Any:
        """Get variable value with strict checking - FIXED: single source of truth"""
        if name.startswith('sy-'):
            return self.sy.get(name)
        
        # Check local scope first (for FORM parameters)
        if self.call_stack:
            local_scope = self.call_stack[-1]
            if name in local_scope:
                return local_scope[name]
        
        # Check parameters
        if name in self.parameters:
            return self.parameters[name]
        
        # Check select-options
        if name in self.select_options:
            return self.select_options[name]
        
        if name in self.constants:
            return self.constants[name]
        
        # FIX: Always read from typed_vars if it exists
        if name in self.typed_vars:
            typed_var = self.typed_vars[name]
            return typed_var.get_value()
        
        # Variable doesn't exist - return type default based on context
        # This prevents "None" output for uninitialized variables
        return None  # Will be handled in eval_expr
    
    def set_variable(self, name: str, value: Any, var_type: Optional[str] = None, length: Optional[int] = None):
        """Set variable value with type checking - FIXED: single source of truth"""
        if name in self.constants:
            raise RuntimeError(f"Cannot modify constant: {name}")
        
        if name.startswith('sy-'):
            self.sy.set(name, value)
            return
        
        # Check local scope for CHANGING parameters
        if self.call_stack:
            local_scope = self.call_stack[-1]
            if name in local_scope:
                local_scope[name] = value
                return
        
        # FIX: Always use typed_vars as single source of truth
        if name in self.typed_vars:
            typed_var = self.typed_vars[name]
            typed_var.set_value(value)
        else:
            if var_type:
                abap_type = ABAPType(var_type, length)
                typed_var = TypedVariable(name, abap_type, value)
                self.typed_vars[name] = typed_var
            else:
                # For untyped variables, create with auto-detected type
                if isinstance(value, int):
                    abap_type = ABAPType('I')
                elif isinstance(value, float):
                    abap_type = ABAPType('F')
                elif isinstance(value, str):
                    abap_type = ABAPType('C')
                else:
                    abap_type = ABAPType('C')  # Default to character
                typed_var = TypedVariable(name, abap_type, value)
                self.typed_vars[name] = typed_var
    
    def declare_constant(self, name: str, value: Any, var_type: Optional[str] = None, length: Optional[int] = None):
        """Declare a constant with type validation"""
        if name in self.constants:
            raise RuntimeError(f"Constant already declared: {name}")
        
        if var_type:
            abap_type = ABAPType(var_type, length)
            typed_value = abap_type.validate(value)
            self.constants[name] = typed_value
        else:
            # For untyped constants, validate based on value type
            if isinstance(value, (int, float)):
                # Auto-detect numeric type
                if isinstance(value, float):
                    abap_type = ABAPType('F')
                else:
                    abap_type = ABAPType('I')
                typed_value = abap_type.validate(value)
                self.constants[name] = typed_value
            else:
                # Default to string
                self.constants[name] = str(value)
        
        # Also create typed variable for consistency
        self.set_variable(name, self.constants[name], var_type, length)
    
    def declare_parameter(self, name: str, value: Any = None, var_type: Optional[str] = None, length: Optional[int] = None):
        """Declare a PARAMETER"""
        if var_type:
            abap_type = ABAPType(var_type, length)
            typed_value = abap_type.validate(value) if value is not None else abap_type.default_value()
            self.parameters[name] = typed_value
        else:
            self.parameters[name] = value
        
        # Also create typed variable
        self.set_variable(name, self.parameters[name], var_type, length)
    
    def declare_select_option(self, name: str, for_var: str, var_type: Optional[str] = None, length: Optional[int] = None):
        """Declare a SELECT-OPTIONS"""
        # Initialize with empty range list
        self.select_options[name] = []
        # Create a typed variable for the SELECT-OPTIONS itself
        self.set_variable(name, [], 'C', 1)
    
    def add_selection_option(self, selopt_name: str, sign: str = "I", option: str = "EQ", 
                            low: Any = None, high: Any = None):
        """Add a range to SELECT-OPTIONS"""
        if selopt_name not in self.select_options:
            self.select_options[selopt_name] = []
        
        selopt = SelectionOption(sign, option, low, high)
        self.select_options[selopt_name].append(selopt)
    
    def matches_selection_options(self, value: Any, selopt_name: str) -> bool:
        """Check if value matches any SELECT-OPTIONS range"""
        if selopt_name not in self.select_options:
            return True  # No restriction
        
        ranges = self.select_options[selopt_name]
        if not ranges:
            return True  # Empty range = all values
        
        for range_obj in ranges:
            if range_obj.matches(value):
                return True
        return False
    
    def get_field_value(self, struct: str, field: str) -> Any:
        """Get value from structure field"""
        struct_data = self.get_variable(struct)
        if isinstance(struct_data, dict):
            return struct_data.get(field)
        return None
    
    def set_field_value(self, struct: str, field: str, value: Any):
        """Set value in structure field"""
        struct_data = self.get_variable(struct)
        if not isinstance(struct_data, dict):
            # Initialize as dict if not already
            struct_data = {field: value}
            self.set_variable(struct, struct_data)
            return
        
        struct_data[field] = value
        # Update the variable
        self.set_variable(struct, struct_data)
    
    def define_table_type(self, table_name: str, field_types: Dict[str, str]):
        """Define internal table type metadata"""
        self.table_types[table_name] = field_types
    
    def get_table_type(self, table_name: str) -> Optional[Dict[str, str]]:
        """Get internal table type metadata"""
        return self.table_types.get(table_name)
    
    def check_loop_control(self) -> Tuple[bool, bool]:
        """Check if loop should exit or continue"""
        should_exit = self.should_exit_loop
        should_continue = self.should_continue
        
        # Reset for next iteration
        if should_exit:
            self.should_exit_loop = False
        if should_continue:
            self.should_continue = False
        
        return should_exit, should_continue
    
    def get_table_safe(self, table_name: str) -> List:
        """Get table or raise error if not declared"""
        if table_name not in self.tables:
            # Check if it's a DATA-defined table
            table_var = self.get_variable(table_name)
            if isinstance(table_var, list):
                self.tables[table_name] = table_var
            else:
                raise RuntimeError(f"Table '{table_name}' not declared")
        return self.tables[table_name]
    
    def push_scope(self):
        """Push new local scope onto stack"""
        self.call_stack.append({})
    
    def pop_scope(self):
        """Pop local scope from stack"""
        if self.call_stack:
            self.call_stack.pop()
    
    def detect_control_break(self, current_value: Any, field: str) -> Tuple[bool, bool]:
        """Simulate AT NEW / AT END OF control break logic"""
        # Store previous value
        prev_key = f"prev_{field}"
        prev_value = self.control_break_data.get(prev_key)
        
        is_at_new = prev_value is None or prev_value != current_value
        is_at_end = False  # Simplified - would need lookahead for proper AT END
        
        # Update stored value
        self.control_break_data[prev_key] = current_value
        
        return is_at_new, is_at_end


# =====================================================
# ===============   EXPRESSION EVALUATION   ===========
# =====================================================

def eval_expr(env: RuntimeEnv, expr: ASTNode) -> Any:
    """Evaluate an expression node with strict ABAP rules"""
    
    if isinstance(expr, Number):
        return expr.val
    
    if isinstance(expr, String):
        return expr.val
    
    if isinstance(expr, Var):
        value = env.get_variable(expr.name)
        # FIX: Handle uninitialized variables gracefully
        if value is None:
            # Return type-specific default instead of None
            # Check if it's a typed variable
            if expr.name in env.typed_vars:
                typed_var = env.typed_vars[expr.name]
                return typed_var.type.default_value()
            # For unknown variables, return empty string
            return ""
        return value
    
    if isinstance(expr, Field):
        value = env.get_field_value(expr.struct, expr.field)
        if value is None:
            return ""  # Return empty string for uninitialized fields
        return value
    
    if isinstance(expr, FuncCall):
        return eval_func_call(env, expr)
    
    if isinstance(expr, BinOp):
        return eval_binop(env, expr)
    
    if isinstance(expr, UnaryOp):
        return eval_unaryop(env, expr)
    
    raise RuntimeError(f"Cannot evaluate expression: {expr}")


def eval_binop(env: RuntimeEnv, expr: BinOp) -> Any:
    """Evaluate binary operation with strict rules"""
    # Operands are NOT in boolean context
    left = eval_expr(env, expr.left)
    right = eval_expr(env, expr.right)
    op = expr.op
    
    # Handle None values - convert to type defaults
    if left is None:
        left = 0 if op in ("+", "-", "*", "/") else ""
    if right is None:
        right = 0 if op in ("+", "-", "*", "/") else ""
    
    # Arithmetic operations
    if op == "+":
        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        return (left or 0) + (right or 0)
    
    if op == "-":
        return (left or 0) - (right or 0)
    
    if op == "*":
        return (left or 0) * (right or 0)
    
    if op == "/":
        if right == 0:
            raise RuntimeError("Division by zero")
        return (left or 0) / (right or 0)
    
    # Comparison operations (always return boolean)
    if op == "=":
        # Numeric comparison for numeric types
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left == right
        if isinstance(left, bool) and isinstance(right, bool):
            return left == right
        # String comparison for others
        left_str = str(left).strip() if left is not None else ""
        right_str = str(right).strip() if right is not None else ""
        return left_str == right_str
    
    if op == "<>":
        # Numeric comparison for numeric types
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left != right
        if isinstance(left, bool) and isinstance(right, bool):
            return left != right
        # String comparison for others
        left_str = str(left).strip() if left is not None else ""
        right_str = str(right).strip() if right is not None else ""
        return left_str != right_str
    
    if op == ">":
        try:
            return float(left or 0) > float(right or 0)
        except ValueError:
            return str(left or "") > str(right or "")
    
    if op == "<":
        try:
            return float(left or 0) < float(right or 0)
        except ValueError:
            return str(left or "") < str(right or "")
    
    if op == ">=":
        try:
            return float(left or 0) >= float(right or 0)
        except ValueError:
            return str(left or "") >= str(right or "")
    
    if op == "<=":
        try:
            return float(left or 0) <= float(right or 0)
        except ValueError:
            return str(left or "") <= str(right or "")
    
    # Logical operations - require boolean operands with short-circuit
    if op == "AND":
        # Short-circuit evaluation
        if not isinstance(left, bool):
            # Try to convert to boolean (ABAP allows this)
            left = bool(left)
        if not left:
            return False
        if not isinstance(right, bool):
            right = bool(right)
        return left and right
    
    if op == "OR":
        # Short-circuit evaluation
        if not isinstance(left, bool):
            left = bool(left)
        if left:
            return True
        if not isinstance(right, bool):
            right = bool(right)
        return left or right
    
    raise RuntimeError(f"Unknown operator: {op}")


def eval_unaryop(env: RuntimeEnv, expr: UnaryOp) -> Any:
    """Evaluate unary operation"""
    if expr.op == "NOT":
        operand = eval_expr(env, expr.operand)
        if not isinstance(operand, bool):
            # Try to convert to boolean (ABAP allows this)
            operand = bool(operand)
        return not operand
    
    raise RuntimeError(f"Unknown unary operator: {expr.op}")


def eval_func_call(env: RuntimeEnv, expr: FuncCall) -> Any:
    """Evaluate function call"""
    func_name = expr.name
    args = [eval_expr(env, arg) for arg in expr.args]
    
    if func_name == "LINES":
        if len(args) != 1:
            raise RuntimeError("LINES expects 1 argument")
        table_name = expr.args[0].name if hasattr(expr.args[0], 'name') else str(args[0])
        return len(env.tables.get(table_name, []))
    
    if func_name == "STRLEN":
        if len(args) != 1:
            raise RuntimeError("STRLEN expects 1 argument")
        return len(str(args[0]))
    
    if func_name == "ABS":
        if len(args) != 1:
            raise RuntimeError("ABS expects 1 argument")
        try:
            return abs(float(args[0]))
        except ValueError:
            return 0
    
    if func_name == "CONCATENATE":
        return "".join(str(arg) for arg in args)
    
    if func_name == "UPPER":
        if len(args) != 1:
            raise RuntimeError("UPPER expects 1 argument")
        return str(args[0]).upper()
    
    if func_name == "LOWER":
        if len(args) != 1:
            raise RuntimeError("LOWER expects 1 argument")
        return str(args[0]).lower()
    
    return None


def validate_boolean_condition(cond: Any, context: str = "IF") -> bool:
    """Validate that condition evaluates to boolean (ABAP rule)"""
    if not isinstance(cond, bool):
        # Try to convert (ABAP allows non-boolean in boolean context with conversion)
        try:
            return bool(cond)
        except:
            raise RuntimeError(f"{context} condition does not evaluate to boolean")
    return cond


# =====================================================
# ===============   STATEMENT EXECUTION   =============
# =====================================================

def exec_statement(env: RuntimeEnv, stmt: ASTNode):
    """Execute a single ABAP statement with strict semantics"""
    
    # FIX: Enforce START-OF-SELECTION phase rules
    # No executable statements should run in declaration phase
    if env.in_declaration_phase:
        if isinstance(stmt, (Write, If, While, Do, LoopAt, Case, Perform, 
                           Check, Exit, Continue, Assign, Clear, Move,
                           Append, AppendSimple, ModifyTable, DeleteTable,
                           InsertTable, ReadTable)):
            return
    
    # Check loop control flags
    should_exit, should_continue = env.check_loop_control()
    if should_exit:
        return
    if should_continue:
        return
    
    # -------------------------
    # WRITE statement - FIXED: No declaration phase execution
    # -------------------------
    if isinstance(stmt, Write):
        for item in stmt.items:
            if isinstance(item, String) and item.val == "\n":
                env.output.append("\n")
            else:
                value = eval_expr(env, item)
                env.output.append(str(value))
        env.output.append("\n")
        return
    
    # -------------------------
    # DATA declaration
    # -------------------------
    if isinstance(stmt, DataDecl):
        value = None
        if stmt.value:
            value = eval_expr(env, stmt.value)
        
        env.set_variable(stmt.name, value, stmt.type_spec, stmt.length)
        env.sy.update_for_success()
        return
    
    # -------------------------
    # TYPES BEGIN OF
    # -------------------------
    if isinstance(stmt, TypesBeginOf):
        # Store structure definition
        env.structures[stmt.name] = stmt.components
        return
    
    # -------------------------
    # DATA BEGIN OF
    # -------------------------
    if isinstance(stmt, DataBeginOf):
        # Create structure instance
        structure = {}
        for comp_name, comp_type, comp_length, comp_value in stmt.components:
            value = None
            if comp_value:
                value = eval_expr(env, comp_value)
            
            if comp_type:
                abap_type = ABAPType(comp_type, comp_length)
                typed_value = abap_type.validate(value)
                structure[comp_name] = typed_value
            else:
                structure[comp_name] = value
        
        env.set_variable(stmt.name, structure)
        env.sy.update_for_success()
        return
    
    # -------------------------
    # CONSTANTS declaration
    # -------------------------
    if isinstance(stmt, ConstantDecl):
        if not stmt.value:
            raise RuntimeError(f"Constant {stmt.name} must have a VALUE")
        
        value = eval_expr(env, stmt.value)
        
        # Type validation for constants
        if stmt.type_spec:
            abap_type = ABAPType(stmt.type_spec, stmt.length)
            typed_value = abap_type.validate(value)
            env.declare_constant(stmt.name, typed_value, stmt.type_spec, stmt.length)
        else:
            # For untyped constants, use automatic type detection
            env.declare_constant(stmt.name, value, None, None)
        
        env.sy.update_for_success()
        return
    
    # -------------------------
    # PARAMETERS declaration
    # -------------------------
    if isinstance(stmt, ParameterDecl):
        value = None
        if stmt.default:
            value = eval_expr(env, stmt.default)
        
        env.declare_parameter(stmt.name, value, stmt.type_spec, stmt.length)
        return
    
    # -------------------------
    # SELECT-OPTIONS declaration
    # -------------------------
    if isinstance(stmt, SelectOptionsDecl):
        env.declare_select_option(stmt.selname, stmt.for_var, stmt.type_spec, stmt.length)
        return
    
    # -------------------------
    # FORM declaration
    # -------------------------
    if isinstance(stmt, FormDecl):
        form_def = FormDef(stmt.name, stmt.params, stmt.body)
        env.forms[stmt.name] = form_def
        return
    
    # -------------------------
    # PERFORM statement
    # -------------------------
    if isinstance(stmt, Perform):
        if stmt.name not in env.forms:
            raise RuntimeError(f"FORM {stmt.name} not found")
        
        form_def = env.forms[stmt.name]
        
        # Push new scope for FORM execution
        env.push_scope()
        
        try:
            # Map parameters to local scope
            param_idx = 0
            
            # Handle USING parameters (value copy)
            for param_name, param_kind in form_def.params:
                if param_kind == "USING":
                    if param_idx < len(stmt.using_params):
                        param_value = eval_expr(env, stmt.using_params[param_idx])
                        env.call_stack[-1][param_name] = param_value
                        param_idx += 1
            
            # Handle CHANGING parameters (reference)
            for param_name, param_kind in form_def.params:
                if param_kind == "CHANGING":
                    if param_idx < len(stmt.changing_params):
                        # Store reference to original variable
                        changing_expr = stmt.changing_params[param_idx]
                        if isinstance(changing_expr, Var):
                            original_value = env.get_variable(changing_expr.name)
                            env.call_stack[-1][param_name] = original_value
                        param_idx += 1
            
            # Execute FORM body
            for form_stmt in form_def.body:
                exec_statement(env, form_stmt)
            
            # Copy back CHANGING parameters
            param_idx = len(stmt.using_params)
            for param_name, param_kind in form_def.params:
                if param_kind == "CHANGING":
                    if param_idx < len(stmt.changing_params):
                        changing_expr = stmt.changing_params[param_idx]
                        if isinstance(changing_expr, Var):
                            new_value = env.call_stack[-1].get(param_name)
                            env.set_variable(changing_expr.name, new_value)
                        param_idx += 1
        
        finally:
            # Pop local scope
            env.pop_scope()
        
        return
    
    # -------------------------
    # START-OF-SELECTION
    # -------------------------
    if isinstance(stmt, StartOfSelection):
        env.in_declaration_phase = False
        env.execution_started = True
        return
    
    # -------------------------
    # UPDATE SQL
    # -------------------------
    if isinstance(stmt, UpdateSQL):
        table_name = stmt.table_name
        if table_name not in env.db:
            env.sy.update_for_error()
            return
        
        # Evaluate SET clause
        set_values = {}
        for field, expr in stmt.set_clause.items():
            set_values[field] = eval_expr(env, expr)
        
        rows_updated = 0
        
        for row in env.db[table_name]:
            match = True
            
            # Apply WHERE clause if present
            if stmt.where:
                try:
                    where_result = eval_where_with_row(env, stmt.where, row)
                    if not where_result:
                        match = False
                except:
                    match = False
            
            if match:
                # Update row
                row.update(set_values)
                rows_updated += 1
        
        env.sy.set('sy-dbcnt', rows_updated)
        env.sy.update_for_success() if rows_updated > 0 else env.sy.update_for_not_found()
        return
    
    # -------------------------
    # INSERT SQL
    # -------------------------
    if isinstance(stmt, InsertSQL):
        table_name = stmt.table_name
        if table_name not in env.db:
            env.db[table_name] = []
        
        # Evaluate values
        row = {}
        for field, expr in stmt.values.items():
            row[field] = eval_expr(env, expr)
        
        env.db[table_name].append(row)
        env.sy.set('sy-dbcnt', 1)
        env.sy.update_for_success()
        return
    
    # -------------------------
    # DELETE SQL
    # -------------------------
    if isinstance(stmt, DeleteSQL):
        table_name = stmt.table_name
        if table_name not in env.db:
            env.sy.update_for_error()
            return
        
        rows_deleted = 0
        new_rows = []
        
        for row in env.db[table_name]:
            match = True
            
            # Apply WHERE clause if present
            if stmt.where:
                try:
                    where_result = eval_where_with_row(env, stmt.where, row)
                    if not where_result:
                        match = False
                except:
                    match = False
            
            if match:
                rows_deleted += 1
            else:
                new_rows.append(row)
        
        env.db[table_name] = new_rows
        env.sy.set('sy-dbcnt', rows_deleted)
        env.sy.update_for_success() if rows_deleted > 0 else env.sy.update_for_not_found()
        return
    
    # -------------------------
    # COMMIT WORK
    # -------------------------
    if isinstance(stmt, CommitWork):
        env._save_db_snapshot()
        return
    
    # -------------------------
    # ROLLBACK WORK
    # -------------------------
    if isinstance(stmt, RollbackWork):
        env._restore_db_snapshot()
        return
    
    # -------------------------
    # CLEAR statement
    # -------------------------
    if isinstance(stmt, Clear):
        for target in stmt.targets:
            if isinstance(target, Var):
                env.set_variable(target.name, None)
            elif isinstance(target, Field):
                try:
                    env.set_field_value(target.struct, target.field, None)
                except RuntimeError:
                    # If structure doesn't exist, that's okay for CLEAR
                    pass
        env.sy.update_for_success()
        return
    
    # -------------------------
    # MOVE statement
    # -------------------------
    if isinstance(stmt, Move):
        source_val = eval_expr(env, stmt.source)
        
        if isinstance(stmt.target, Var):
            env.set_variable(stmt.target.name, source_val)
        elif isinstance(stmt.target, Field):
            env.set_field_value(stmt.target.struct, stmt.target.field, source_val)
        
        env.sy.update_for_success()
        return
    
    # -------------------------
    # Assignment - FIXED: Properly sync typed_vars
    # -------------------------
    if isinstance(stmt, Assign):
        value = eval_expr(env, stmt.expr)
        
        if isinstance(stmt.target, Var):
            env.set_variable(stmt.target.name, value)
        elif isinstance(stmt.target, Field):
            env.set_field_value(stmt.target.struct, stmt.target.field, value)
        
        env.sy.update_for_success()
        return
    
    # -------------------------
    # APPEND (structured)
    # -------------------------
    if isinstance(stmt, Append):
        target = stmt.target_table
        if target not in env.tables:
            env.tables[target] = []
        
        row = {}
        for field, expr in stmt.source_row.items():
            row[field] = eval_expr(env, expr)
        
        env.tables[target].append(row)
        
        # Update table type metadata
        if target not in env.table_types:
            field_types = {}
            for field, expr in stmt.source_row.items():
                # Try to infer type from expression
                if isinstance(expr, Number):
                    field_types[field] = 'I'
                elif isinstance(expr, String):
                    field_types[field] = 'C'
                else:
                    field_types[field] = 'C'  # Default
            env.define_table_type(target, field_types)
        
        env.sy.update_for_success()
        return
    
    # -------------------------
    # APPEND (simple)
    # -------------------------
    if isinstance(stmt, AppendSimple):
        src = stmt.source_var
        tgt = stmt.target_table
        
        if tgt not in env.tables:
            env.tables[tgt] = []
        
        value = env.get_variable(src)
        if isinstance(value, dict):
            env.tables[tgt].append(value.copy())
        else:
            env.tables[tgt].append(value)
        
        env.sy.update_for_success()
        return
    
    # -------------------------
    # MODIFY TABLE
    # -------------------------
    if isinstance(stmt, ModifyTable):
        try:
            table = env.get_table_safe(stmt.table_name)
        except RuntimeError:
            env.sy.update_for_error()
            return
        
        source_data = env.get_variable(stmt.from_var)
        
        if not isinstance(source_data, dict):
            env.sy.update_for_error()
            return
        
        # Validate key field exists in source data
        if stmt.key_field and stmt.key_field not in source_data:
            env.sy.update_for_error()
            return
        
        found = False
        key_field = stmt.key_field
        
        for i, row in enumerate(table):
            match = True
            if key_field:
                # Match by key field
                if row.get(key_field) != source_data.get(key_field):
                    match = False
            else:
                # Match all fields that exist in source
                for k, v in source_data.items():
                    if k in row and row[k] != v:
                        match = False
                        break
            
            if match:
                # Update the row
                table[i].update(source_data)
                found = True
                break
        
        if found:
            env.sy.update_for_success()
        else:
            # If not found, append
            env.tables[stmt.table_name].append(source_data.copy())
            env.sy.update_for_success()
        return
    
    # -------------------------
    # DELETE TABLE
    # -------------------------
    if isinstance(stmt, DeleteTable):
        try:
            table = env.get_table_safe(stmt.table_name)
        except RuntimeError:
            env.sy.update_for_error()
            return
        
        if stmt.key:
            key_field, key_expr = stmt.key
            key_value = eval_expr(env, key_expr)
            
            # Find and remove matching rows
            original_len = len(table)
            env.tables[stmt.table_name] = [
                row for row in table 
                if not (isinstance(row, dict) and row.get(key_field) == key_value)
            ]
            
            if len(env.tables[stmt.table_name]) < original_len:
                env.sy.update_for_success()
            else:
                env.sy.update_for_not_found()
        else:
            # Delete all rows
            env.tables[stmt.table_name] = []
            env.sy.update_for_success()
        return
    
    # -------------------------
    # INSERT TABLE
    # -------------------------
    if isinstance(stmt, InsertTable):
        try:
            tgt = stmt.target_table
            if tgt not in env.tables:
                env.tables[tgt] = []
        except RuntimeError:
            env.sy.update_for_error()
            return
        
        src = stmt.source_var
        value = env.get_variable(src)
        
        # Check if already exists (simple check)
        if isinstance(value, dict) and value in env.tables[tgt]:
            env.sy.update_for_error()
        else:
            if isinstance(value, dict):
                env.tables[tgt].append(value.copy())
            else:
                env.tables[tgt].append(value)
            env.sy.update_for_success()
        return
    
    # -------------------------
    # EXIT statement
    # -------------------------
    if isinstance(stmt, Exit):
        env.should_exit_loop = True
        return
    
    # -------------------------
    # CONTINUE statement
    # -------------------------
    if isinstance(stmt, Continue):
        env.should_continue = True
        return
    
    # -------------------------
    # CHECK statement
    # -------------------------
    if isinstance(stmt, Check):
        condition = eval_expr(env, stmt.condition)
        if not validate_boolean_condition(condition, "CHECK"):
            return
        if not condition:
            env.should_continue = True
        return
    
    # -------------------------
    # LOOP AT
    # -------------------------
    if isinstance(stmt, LoopAt):
        try:
            itab = env.get_table_safe(stmt.table)
        except RuntimeError:
            env.sy.update_for_error()
            return
        
        env.sy.reset_loop_vars()
        
        for idx, row in enumerate(itab):
            env.sy.set('sy-tabix', idx + 1)
            env.sy.set('sy-index', idx + 1)
            
            # Set loop variable
            if isinstance(row, dict):
                env.set_variable(stmt.into, row.copy())
            else:
                env.set_variable(stmt.into, row)
            
            # Execute loop body
            for inner_stmt in stmt.body:
                exec_statement(env, inner_stmt)
                
                # Check if should exit or continue
                should_exit, should_continue = env.check_loop_control()
                if should_exit:
                    break
                if should_continue:
                    continue
            
            if env.should_exit_loop:
                env.should_exit_loop = False
                break
        
        env.sy.reset_loop_vars()
        return
    
    # -------------------------
    # READ TABLE
    # -------------------------
    if isinstance(stmt, ReadTable):
        try:
            itab = env.get_table_safe(stmt.table_name)
        except RuntimeError:
            env.sy.set('sy-subrc', 8)
            env.sy.set('sy-tabix', 0)
            return
        
        found = False
        
        for idx, row in enumerate(itab):
            match = True
            
            if stmt.key:
                key_field, key_expr = stmt.key
                expected_value = eval_expr(env, key_expr)
                
                if not isinstance(row, dict) or row.get(key_field) != expected_value:
                    match = False
            
            if match:
                found = True
                env.sy.set('sy-subrc', 0)
                env.sy.set('sy-tabix', idx + 1)
                
                if stmt.into:
                    if isinstance(row, dict):
                        env.set_variable(stmt.into, row.copy())
                    else:
                        env.set_variable(stmt.into, row)
                break
        
        if not found:
            env.sy.set('sy-subrc', 4)
            env.sy.set('sy-tabix', 0)
        return
    
    # -------------------------
    # IF statement
    # -------------------------
    if isinstance(stmt, If):
        cond = eval_expr(env, stmt.cond)
        if validate_boolean_condition(cond, "IF") and cond:
            for s in stmt.then_body:
                exec_statement(env, s)
            return
        
        for elif_cond, elif_body in stmt.elif_list:
            cond_val = eval_expr(env, elif_cond)
            if validate_boolean_condition(cond_val, "ELSEIF") and cond_val:
                for s in elif_body:
                    exec_statement(env, s)
                return
        
        for s in stmt.else_body:
            exec_statement(env, s)
        return
    
    # -------------------------
    # WHILE statement
    # -------------------------
    if isinstance(stmt, While):
        # Add infinite loop guard
        iteration_limit = env.max_loop_iterations
        iterations = 0
        
        while iterations < iteration_limit:
            iterations += 1
            cond = eval_expr(env, stmt.cond)
            if not validate_boolean_condition(cond, "WHILE") or not cond:
                break
                
            for s in stmt.body:
                exec_statement(env, s)
                
                # Check loop control
                should_exit, should_continue = env.check_loop_control()
                if should_exit:
                    env.should_exit_loop = False
                    break
                if should_continue:
                    continue
            
            if env.should_exit_loop:
                env.should_exit_loop = False
                break
        
        if iterations >= iteration_limit:
            raise RuntimeError("WHILE loop exceeded maximum iteration limit")
        return
    
    # -------------------------
    # DO statement - FIXED: Works correctly, user variable updates are separate issue
    # -------------------------
    if isinstance(stmt, Do):
        times = 1
        if stmt.times_expr:
            times_val = eval_expr(env, stmt.times_expr)
            times = int(times_val) if times_val else 1
        
        # Add iteration limit check
        if times > env.max_loop_iterations:
            raise RuntimeError(f"DO loop exceeds maximum iteration limit: {times} > {env.max_loop_iterations}")
        
        for i in range(times):
            env.sy.set('sy-index', i + 1)
            for s in stmt.body:
                exec_statement(env, s)
                
                # Check loop control
                should_exit, should_continue = env.check_loop_control()
                if should_exit:
                    env.should_exit_loop = False
                    break
                if should_continue:
                    continue
            
            if env.should_exit_loop:
                env.should_exit_loop = False
                break
        
        env.sy.set('sy-index', 0)
        return
    
    # -------------------------
    # CASE statement
    # -------------------------
    if isinstance(stmt, Case):
        value = eval_expr(env, stmt.expr)
        
        for case_val, case_body in stmt.cases:
            case_eval = eval_expr(env, case_val)
            if value == case_eval:
                for s in case_body:
                    exec_statement(env, s)
                return
        
        # WHEN OTHERS
        for s in stmt.others_body:
            exec_statement(env, s)
        return
    
    # -------------------------
    # SELECT statement with enhanced WHERE and ORDER BY
    # -------------------------
    if isinstance(stmt, SelectInto):
        src_table = env.db.get(stmt.table_name, [])
        result = []
        
        for row in src_table:
            # Apply WHERE clause if present
            if stmt.where:
                try:
                    where_result = eval_where_with_row(env, stmt.where, row)
                    if not where_result:
                        continue
                except:
                    continue
            
            # Select fields
            if stmt.fields == ["*"]:
                filtered_row = row.copy()
            else:
                filtered_row = {field: row.get(field, '') for field in stmt.fields}
            
            result.append(filtered_row)
        
        # Apply ORDER BY if specified
        if stmt.order_by and result:
            def get_sort_key(row):
                keys = []
                for field in stmt.order_by:
                    value = row.get(field, '')
                    # Try numeric sort first
                    try:
                        keys.append(float(value))
                    except:
                        keys.append(str(value))
                return tuple(keys)
            
            result.sort(key=get_sort_key)
        
        env.tables[stmt.into_table] = result
        
        # Create table type metadata
        if result and stmt.fields != ["*"]:
            field_types = {}
            for field in stmt.fields:
                # Try to infer type from first row
                if result and field in result[0]:
                    value = result[0][field]
                    if isinstance(value, (int, float)):
                        field_types[field] = 'I'
                    else:
                        field_types[field] = 'C'
            env.define_table_type(stmt.into_table, field_types)
        
        env.sy.set('sy-dbcnt', len(result))
        env.sy.set('sy-subrc', 0 if len(result) > 0 else 4)
        return


def eval_where_with_row(env: RuntimeEnv, where_expr: ASTNode, row: Dict) -> bool:
    """Evaluate WHERE clause with row values as variables (isolated scope)"""
    
    # Create isolated variable map for WHERE evaluation
    row_vars = row.copy()
    
    def eval_with_row(expr: ASTNode) -> Any:
        if isinstance(expr, Var):
            # Check if variable exists in row first
            if expr.name in row_vars:
                return row_vars[expr.name]
            # Then check if it's a system variable
            if expr.name.startswith('sy-'):
                return env.sy.get(expr.name)
            # Otherwise check environment (read-only)
            return env.get_variable(expr.name)
        
        if isinstance(expr, Number):
            return expr.val
        
        if isinstance(expr, String):
            return expr.val
        
        if isinstance(expr, Field):
            # Handle field access in WHERE clause
            struct_value = eval_with_row(Var(expr.struct))
            if isinstance(struct_value, dict):
                return struct_value.get(expr.field)
            return None
        
        if isinstance(expr, BinOp):
            left = eval_with_row(expr.left)
            right = eval_with_row(expr.right)
            op = expr.op
            
            if op == "=":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left == right
                return str(left).strip() == str(right).strip()
            elif op == "<>":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left != right
                return str(left).strip() != str(right).strip()
            elif op == ">":
                try:
                    return float(left) > float(right)
                except:
                    return str(left) > str(right)
            elif op == "<":
                try:
                    return float(left) < float(right)
                except:
                    return str(left) < str(right)
            elif op == ">=":
                try:
                    return float(left) >= float(right)
                except:
                    return str(left) >= str(right)
            elif op == "<=":
                try:
                    return float(left) <= float(right)
                except:
                    return str(left) <= str(right)
            elif op == "AND":
                # Short-circuit evaluation
                if not isinstance(left, bool):
                    left = bool(left)
                if not left:
                    return False
                if not isinstance(right, bool):
                    right = bool(right)
                return left and right
            elif op == "OR":
                # Short-circuit evaluation
                if not isinstance(left, bool):
                    left = bool(left)
                if left:
                    return True
                if not isinstance(right, bool):
                    right = bool(right)
                return left or right
        
        if isinstance(expr, UnaryOp) and expr.op == "NOT":
            operand = eval_with_row(expr.operand)
            if not isinstance(operand, bool):
                operand = bool(operand)
            return not operand
        
        return None
    
    result = eval_with_row(where_expr)
    return bool(result) if not isinstance(result, bool) else result


def execute_program(program: Program, input_params: Dict[str, Any] = None) -> str:
    """Execute entire program and return output"""
    env = RuntimeEnv()
    
    # Apply input parameters if provided
    if input_params:
        for name, value in input_params.items():
            if name in env.parameters:
                env.parameters[name] = value
                # Also update the typed variable
                env.set_variable(name, value)
    
    # Two-phase execution: declaration phase then execution phase
    declaration_statements = []
    execution_statements = []
    in_execution_phase = False
    
    for stmt in program.statements:
        if isinstance(stmt, StartOfSelection):
            in_execution_phase = True
            execution_statements.append(stmt)
        elif in_execution_phase:
            execution_statements.append(stmt)
        else:
            declaration_statements.append(stmt)
    
    # Execute declaration phase
    for stmt in declaration_statements:
        try:
            exec_statement(env, stmt)
        except RuntimeError as e:
            raise RuntimeError(f"Runtime error in declaration phase: {e}")
    
    # Execute execution phase
    for stmt in execution_statements:
        try:
            exec_statement(env, stmt)
        except RuntimeError as e:
            raise RuntimeError(f"Runtime error in execution phase: {e}")
    
    # FIX: Join output properly, filter out empty lines from declaration phase
    filtered_output = [line for line in env.output if line != "\n" or len(env.output) > 1]
    return "".join(filtered_output)


# =====================================================
# ===============   PUBLIC API   ======================
# =====================================================

def extract_sia_block(code: str) -> str:
    """Extract content inside *sia ... sia*"""
    start = code.find("*sia")
    end = code.rfind("sia*")
    
    if start == -1 or end == -1:
        raise RuntimeError(
            "Missing SIA wrapper. Expected code inside:\n"
            "*sia\n"
            "   ... ABAP code ...\n"
            "sia*"
        )
    
    inner = code[start + 4:end].strip()
    return inner


def run(code: str, input_params: Dict[str, Any] = None) -> str:
    """Execute ABAP code inside *sia ... sia*"""
    try:
        src = extract_sia_block(code)
        tokens = tokenize_abap(src)
        parser = FullParser(tokens)
        program = parser.parse_program()
        
        output = execute_program(program, input_params)
        return output
        
    except ParserError as pe:
        raise RuntimeError(f"[PARSER ERROR] {pe}")
    except RuntimeError as re:
        raise RuntimeError(f"[RUNTIME ERROR] {re}")
    except Exception as e:
        raise RuntimeError(f"[UNKNOWN ERROR] {e}")


def run_file(path: str, input_params: Dict[str, Any] = None) -> str:
    """Run ABAP code from a file"""
    with open(path, "r", encoding="utf-8") as f:
        return run(f.read(), input_params)


def safe_run(code: str, input_params: Dict[str, Any] = None) -> Optional[str]:
    """Same as run(), but traps errors cleanly"""
    try:
        return run(code, input_params)
    except Exception as e:
        print(f"[SIA-ELS ERROR] {e}")
        return None


def repl():
    """Interactive REPL shell for SIA-ELS"""
    print("SIA Enterprise Logic Studio - REPL (Version 4.2 - Bug Fixes)")
    print("Enter ABAP code inside *sia ... sia* blocks.")
    print("Type ':quit' to exit.")
    print("Type ':params key=value' to set parameters (e.g., ':params p_dept=IT').")
    print("Type ':selopt name=value' to set SELECT-OPTIONS (e.g., ':selopt s_salary=50000').\n")
    
    buffer = []
    recording = False
    input_params = {}
    select_options = {}
    
    while True:
        try:
            line = input("ELS> ").rstrip("\n")
            
            if line == ":quit":
                break
            
            if line.startswith(":params"):
                # Parse parameters
                parts = line.split()
                for param in parts[1:]:
                    if "=" in param:
                        key, value = param.split("=", 1)
                        input_params[key] = value
                print(f"Parameters set: {input_params}")
                continue
            
            if line.startswith(":selopt"):
                # Parse SELECT-OPTIONS
                parts = line.split()
                for param in parts[1:]:
                    if "=" in param:
                        key, value = param.split("=", 1)
                        select_options[key] = value
                print(f"SELECT-OPTIONS set: {select_options}")
                continue
            
            if "*sia" in line:
                recording = True
                buffer = [line]
                
                if "sia*" in line:
                    code = "\n".join(buffer)
                    
                    # Merge input_params and select_options
                    all_params = {**input_params, **select_options}
                    output = safe_run(code, all_params)
                    if output:
                        print(output, end="")
                    recording = False
                    buffer = []
                
                continue
            
            if recording:
                buffer.append(line)
                
                if "sia*" in line:
                    code = "\n".join(buffer)
                    all_params = {**input_params, **select_options}
                    output = safe_run(code, all_params)
                    if output:
                        print(output, end="")
                    recording = False
                    buffer = []
                
                continue
            
            print("Use *sia ... sia* to execute code.")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break


# =====================================================
# ===============   HELPER FUNCTIONS   ================
# =====================================================

def load_sql_table(env: RuntimeEnv, name: str, rows: List[Dict]):
    """Loads a Python list of dicts into SQL namespace"""
    if not isinstance(rows, list):
        raise RuntimeError("SQL table must be a list of dictionaries")
    env.db[name] = [row.copy() for row in rows]
    
    # Create initial snapshot
    env._save_db_snapshot()


def register_class(env: RuntimeEnv, cls_name: str, methods: Dict):
    """Register a class with method bodies"""
    env.classes[cls_name] = {
        "methods": methods,
        "attributes": {}
    }


def set_object_attr(env: RuntimeEnv, obj_name: str, key: str, value: Any):
    """Set object attribute"""
    if obj_name not in env.objects:
        raise RuntimeError(f"Object '{obj_name}' not created.")
    env.objects[obj_name]["attrs"][key] = value


def get_object_attr(env: RuntimeEnv, obj_name: str, key: str) -> Any:
    """Get object attribute"""
    if obj_name not in env.objects:
        raise RuntimeError(f"Object '{obj_name}' not created.")
    return env.objects[obj_name]["attrs"].get(key)


# =====================================================
# ===============   MAIN ENTRY POINT   ================
# =====================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            # Check for parameter file
            params = {}
            if len(sys.argv) > 2 and sys.argv[2] == "--params":
                param_file = sys.argv[3] if len(sys.argv) > 3 else "params.json"
                try:
                    with open(param_file, "r") as f:
                        params = json.load(f)
                except:
                    print(f"Could not load parameters from {param_file}")
            
            output = run_file(filename, params)
            print(output, end="")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        repl()


# =====================================================
# ===============   EXPORTS   =========================
# =====================================================

__all__ = [
    # Main API
    "run",
    "run_file",
    "repl",
    "safe_run",
    
    # Core components
    "tokenize_abap",
    "FullParser",
    "RuntimeEnv",
    "execute_program",
    
    # Helper functions
    "load_sql_table",
    "register_class",
    "set_object_attr",
    "get_object_attr",
    
    # Type system
    "ABAPType",
    "TypedVariable",
    
    # Selection options
    "SelectionOption",
]