from typing import List, Generator, Tuple
from .equation_symbols import KEYWORDS

class Token:
    def __init__(self, type_: str, value: str):
        self.type = type_ # 'COMMAND', 'TEXT', 'LBRACE', 'RBRACE', 'SYMBOL', 'EOF'
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

class EqTokenizer:
    def __init__(self, script: str):
        self.script = script
        self.pos = 0
        self.length = len(script)

    def tokenize(self) -> Generator[Token, None, None]:
        while self.pos < self.length:
            char = self.script[self.pos]

            if char.isspace():
                self.pos += 1
                continue
            
            if char == '{':
                yield Token('LBRACE', '{')
                self.pos += 1
            elif char == '}':
                yield Token('RBRACE', '}')
                self.pos += 1
            elif char == '^':
                yield Token('COMMAND', 'SUP') # Normalize
                self.pos += 1
            elif char == '_':
                yield Token('COMMAND', 'SUB') # Normalize
                self.pos += 1
            elif char == '#':
                yield Token('COMMAND', '#')
                self.pos += 1
            elif char == '&':
                yield Token('COMMAND', '&')
                self.pos += 1
            elif char == '"':
                yield self._read_quoted_string()
            else:
                yield self._read_word_or_number()
        
        yield Token('EOF', '')

    def _read_quoted_string(self) -> Token:
        self.pos += 1 # skip opening quote
        start = self.pos
        while self.pos < self.length and self.script[self.pos] != '"':
            self.pos += 1
        
        value = self.script[start:self.pos]
        self.pos += 1 # skip closing quote
        return Token('TEXT', value)

    def _read_word_or_number(self) -> Token:
        start = self.pos
        while self.pos < self.length:
            char = self.script[self.pos]
            if char.isspace() or char in '{}#&^_"':
                break
            self.pos += 1
        
        word = self.script[start:self.pos]
        
        # Check if keyword
        if word in KEYWORDS:
            return Token('COMMAND', word)
        
        # Check if purely number -> treat as TEXT/NUMBER
        # For HWP equations, numbers are just atoms like text
        return Token('TEXT', word)
