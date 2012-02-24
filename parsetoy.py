#!/usr/bin/env python3
# encoding=utf-8

from collections import namedtuple
import re

Token = namedtuple('Token', ( 'type', 'value' ))
LexRule = namedtuple('LexRule', ( 'expression', 'handler' ))
ParseRule = namedtuple('ParseRule', ( 'operator', 'inputs', 'handler' ))
OpPrecedence = namedtuple('OpPrecedence', ( 'associativity', 'operators' ))

class CalculatorGrammar:
	grammar = (
		LexRule(re.compile(r'\s+'), lambda match: None),
		LexRule(re.compile(r'(?:\.[0-9]+|[0-9]+(?:\.[0-9]+)?)'), lambda match: Token('number', float(match))),
		LexRule(re.compile(r'\+'), lambda match: Token('+', None)),
		LexRule(re.compile(r'-'), lambda match: Token('-', None)),
		LexRule(re.compile(r'\('), lambda match: Token('(', None)),
		LexRule(re.compile(r'\)'), lambda match: Token(')', None))
	)
	expressions = (
		ParseRule(None, ( 'number', ), lambda n: Token('expression', n.value)),
		ParseRule(None, ( '(', 'expression', ')' ), lambda l, ex, r: ex ),
		ParseRule('+', ( 'expression', '+', 'expression' ), lambda l, op, r: Token('expression', l.value + r.value) ),
		ParseRule('-', ( 'expression', '-', 'expression' ), lambda l, op, r: Token('expression', l.value - r.value) )
	)

class LexError(Exception):
	"""Input couldn't be lexed based on this grammer."""
	pass

def lex(grammar, input):
	"""Generate a series of tokens from an input string based on a grammar.
		>>> list(lex(CalculatorGrammar.grammar, '1 + 5 +7 - 0.5'))
		[Token(type='number', value=1.0), Token(type='+', value=None), Token(type='number', value=5.0), Token(type='+', value=None), Token(type='number', value=7.0), Token(type='-', value=None), Token(type='number', value=0.5)]
	"""
	while input:
		for rule in grammar:
			match = rule.expression.match(input)
			if match:
				matchText = match.group()
				token = rule.handler(matchText)
				if token:
					yield token
				input = input[len(matchText):]
				break
		else:
			raise LexError


class ParseError(Exception):
	"""Input couldn't be parsed under these rules"""
	def __init__(self, stack):
		self.stack = stack

def parse(rules, tokens):
	stack = []
	while True:
		for rule in rules:
			if len(stack) >= len(rule.inputs) and all( a == b for a, b in zip(rule.inputs, (t.type for t in stack[-len(rule.inputs):]))):
				stack[-len(rule.inputs):] = [rule.handler(*stack[-len(rule.inputs):])]
				break
		else:
			if len(tokens):
				stack.append(tokens[0])
				del tokens[0]
			elif len(stack) <= 1:
				break
			else:
				raise ParseError(stack)
	return stack

def test():
	import doctest
	return doctest.testmod()

def main():
	import sys
	try:
		tokens = list(lex(CalculatorGrammar.grammar, sys.argv[1]))
	except LexError:
		print('Couldn’t lex your input')
		sys.exit(2)

	print('Lexer results:')
	print(tokens)

	print('')

	try:
		parsed = parse(CalculatorGrammar.expressions, tokens)
	except ParseError as e:
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
		sys.exit()
	if len(sys.argv) != 2:
		print('usage: %s pattern' % (sys.argv[0],))
		sys.exit(1)
	main()
