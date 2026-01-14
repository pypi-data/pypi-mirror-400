from typing import List, Optional
from .equation_model import *
from .equation_tokenizer import EqTokenizer, Token

class EqParser:
    def __init__(self, script: str):
        self.tokenizer = EqTokenizer(script)
        self.tokens = list(self.tokenizer.tokenize())
        self.pos = 0

    def parse(self) -> EqNode:
        return self._parse_list(is_root=True)

    def _peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '')

    def _consume(self) -> Token:
        token = self._peek()
        self.pos += 1
        return token

    def _match(self, type_: str, value: str = None) -> bool:
        token = self._peek()
        if token.type == type_:
            if value is None or token.value == value:
                self._consume()
                return True
        return False

    def _parse_list(self, is_root: bool = False) -> EqList:
        nodes = []
        while True:
            token = self._peek()
            if token.type == 'EOF':
                break
            if token.type == 'RBRACE' and not is_root:
                break
            
            node = self._parse_expression()
            if node:
                nodes.append(node)
            else:
                break
                
        return EqList(nodes)

    def _parse_expression(self) -> Optional[EqNode]:
        # Handle prefix commands
        token = self._peek()
        
        if token.type == 'LBRACE':
            self._consume()
            node = self._parse_list()
            self._match('RBRACE')
            return self._handle_infix_postfix(node)

        if token.type == 'TEXT':
            self._consume()
            return self._handle_infix_postfix(EqAtom(token.value))

        if token.type == 'COMMAND':
            cmd = token.value
            self._consume()

            # Handle Structures
            if cmd == 'SQRT' or cmd == 'ROOT':
                # SQRT { content } or ROOT { index } OF { content }
                first = self._parse_expression()
                if cmd == 'ROOT' and self._peek().value == 'OF':
                    self._consume() # consume OF
                    second = self._parse_expression()
                    return self._handle_infix_postfix(EqRoot(content=second, root_idx=first))
                return self._handle_infix_postfix(EqRoot(content=first))

            # Handle Decorations
            if cmd in ['vec', 'hat', 'bar', 'tilde', 'dot', 'ddot']:
                content = self._parse_expression()
                return self._handle_infix_postfix(EqDecoration(content, cmd))

            return self._handle_infix_postfix(EqAtom(cmd, is_command=True))
            
        return None

    def _handle_infix_postfix(self, left: EqNode) -> EqNode:
        """
        Check if the current node is followed by an infix operator (OVER, ^, _)
        Recursively helper to build the tree upwards.
        """
        token = self._peek()

        # Fraction: left OVER right
        if token.value in ['OVER', 'ATOP']:
            cmd = token.value
            self._consume()
            right = self._parse_expression()
            # Note: Fraction binds loosely? "a + b OVER c" -> usually "(a+b) OVER c" in HWP?
            # Or "a OVER b" binds tightly? HWP script usually requires bracing for complex numerators.
            # Assuming immediate next term is denominator.
            return self._handle_infix_postfix(EqFraction(left, right, has_line=(cmd=='OVER')))

        # Scripts: left^sup_sub
        if token.value in ['SUP', 'SUB']:
            cmd = token.value
            self._consume()
            right = self._parse_expression()
            
            new_node = None
            if isinstance(left, EqScript):
                # if already has script, update it
                if cmd == 'SUP': left.sup = right
                else: left.sub = right
                new_node = left
            else:
                if cmd == 'SUP': new_node = EqScript(base=left, sup=right)
                else: new_node = EqScript(base=left, sub=right)
            
            return self._handle_infix_postfix(new_node)

        return left
