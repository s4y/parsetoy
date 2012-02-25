#!/usr/bin/env python3
# encoding=utf-8

from collections import namedtuple

Token = namedtuple('Token', ( 'type', 'value' ))
LexRule = namedtuple('LexRule', ( 'expression', 'handler' ))
ParseRule = namedtuple('ParseRule', ( 'operator', 'inputs', 'handler' ))
OpPrecedence = namedtuple('OpPrecedence', ( 'associativity', 'operators' ))

class Lexer:
	class LexError(Exception):
		"""Input couldn't be lexed based on this grammar."""
	def __init__(self, grammar):
		self.grammar = grammar
	def lex(self, input):
		"""Generate a series of tokens from an input string based on a grammar.
			>>> from calculator import CalculatorGrammar
			>>> list(Lexer(CalculatorGrammar.grammar).lex('1 + 5 +7 - 0.5'))
			[Token(type='number', value=1.0), Token(type='add', value=None), Token(type='number', value=5.0), Token(type='add', value=None), Token(type='number', value=7.0), Token(type='subtract', value=None), Token(type='number', value=0.5)]
		"""
		while input:
			for rule in self.grammar:
				match = rule.expression.match(input)
				if match:
					matchText = match.group()
					token = rule.handler(matchText)
					if token:
						yield token
					input = input[len(matchText):]
					break
			else:
				raise Lexer.LexError

class Parser:
	class ParseError(Exception):
		"""Input couldn't be parsed under these rules"""
		def __init__(self, stack):
			self.stack = stack
	def __init__(self, rules, precedence):
		self.rules = rules
		self.precedence = precedence
	def opPrecedence(self, op):
		try:
			return next( prec for prec in enumerate(self.precedence) if op in prec[1].operators )
		except StopIteration:
			return None
	def parse(self, tokens):
		stack = []
		while True:
			for rule in self.rules:
				if len(stack) >= len(rule.inputs) and all( a == b for a, b in zip(rule.inputs, (t.type for t in stack[-len(rule.inputs):]))):
					if rule.operator and len(tokens):
						stackPrecedence = self.opPrecedence(rule.operator)
						inputPrecedence = self.opPrecedence(tokens[0].type)
						if inputPrecedence and stackPrecedence and (
							(inputPrecedence[0] > stackPrecedence[0]) or
							(inputPrecedence[0] == stackPrecedence[0] and stackPrecedence[1].associativity == 'right')
						):
							continue
					stack[-len(rule.inputs):] = [rule.handler(*stack[-len(rule.inputs):])]
					break
			else:
				if len(tokens):
					stack.append(tokens[0])
					del tokens[0]
				elif len(stack) <= 1:
					break
				else:
					raise Parser.ParseError(stack)
		return stack

if __name__ == "__main__":
	import doctest
	doctest.testmod(verbose=True)
