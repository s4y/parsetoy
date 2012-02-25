#!/usr/bin/env python3
# encoding=utf-8

from collections import namedtuple
import re

Token = namedtuple('Token', ( 'type', 'value' ))
LexRule = namedtuple('LexRule', ( 'expression', 'handler' ))
ParseRule = namedtuple('ParseRule', ( 'operator', 'inputs', 'handler' ))
OpPrecedence = namedtuple('OpPrecedence', ( 'associativity', 'operators' ))

class CalculatorGrammar:
	from math import pow
	grammar = (
		LexRule(re.compile(r'\s+'), lambda match: None),
		LexRule(re.compile(r'(?:\.[0-9]+|[0-9]+(?:\.[0-9]+)?)'), lambda match: Token('number', float(match))),
		LexRule(re.compile(r'\+'), lambda match: Token('add', None)),
		LexRule(re.compile(r'-'), lambda match: Token('subtract', None)),
		LexRule(re.compile(r'\*'), lambda match: Token('multiply', None)),
		LexRule(re.compile(r'/'), lambda match: Token('divide', None)),
		LexRule(re.compile(r'\^'), lambda match: Token('pow', None)),
		LexRule(re.compile(r'\('), lambda match: Token('(', None)),
		LexRule(re.compile(r'\)'), lambda match: Token(')', None))
	)
	precedence = (
		OpPrecedence('left', { 'add', 'subtract' }),
		OpPrecedence('left', { 'multiply', 'divide' }),
		OpPrecedence('right', { 'pow' })
	)
	expressions = (
		ParseRule(None, ( 'number', ), lambda n: Token('expression', n.value)),
		ParseRule(None, ( '(', 'expression', ')' ), lambda l, ex, r: ex ),
		ParseRule('add', ( 'expression', 'add', 'expression' ), lambda l, op, r: Token('expression', l.value + r.value) ),
		ParseRule('subtract', ( 'expression', 'subtract', 'expression' ), lambda l, op, r: Token('expression', l.value - r.value) ),
		ParseRule('multiply', ( 'expression', 'multiply', 'expression' ), lambda l, op, r: Token('expression', l.value * r.value) ),
		ParseRule('divide', ( 'expression', 'divide', 'expression' ), lambda l, op, r: Token('expression', l.value / r.value) ),
		ParseRule('pow', ( 'expression', 'pow', 'expression' ), lambda l, op, r: Token('expression', pow(l.value, r.value)) )
	)


class Lexer:
	class LexError(Exception):
		"""Input couldn't be lexed based on this grammar."""
	def __init__(self, grammar):
		self.grammar = grammar
	def lex(self, input):
		"""Generate a series of tokens from an input string based on a grammar.
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

def test():
	import doctest
	return doctest.testmod()

def main():
	import sys

	parser = Parser(CalculatorGrammar.expressions, CalculatorGrammar.precedence)
	lexer = Lexer(CalculatorGrammar.grammar)

	try:
		tokens = list(lexer.lex(sys.argv[1]))
	except Lexer.LexError:
		print('Couldn’t lex your input')
		sys.exit(2)

	print('Lexer results:')
	print(tokens)

	print('')

	try:
		parsed = parser.parse(tokens)
	except Parser.ParseError as e:
		print('Parse error. Stack:')
		print(e.stack)

	else:
		print('Parser results:')
		print(parsed)

		if any(parsed):
			print('\nValue:')
			print(parsed[-1].value)


if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		test()
	elif len(sys.argv) != 2:
		print('usage: %s pattern' % (sys.argv[0],))
		sys.exit(1)
	else:
		main()
