#!/usr/bin/env python3
# encoding=utf-8

from parsetoy import *

class CalculatorGrammar:
	from math import pow
	from re import compile
	grammar = (
		LexRule(compile(r'\s+'), lambda match: None),
		LexRule(compile(r'(?:\.[0-9]+|[0-9]+(?:\.[0-9]+)?)'), lambda match: Token('number', float(match))),
		LexRule(compile(r'\+'), lambda match: Token('add', None)),
		LexRule(compile(r'-'), lambda match: Token('subtract', None)),
		LexRule(compile(r'\*'), lambda match: Token('multiply', None)),
		LexRule(compile(r'/'), lambda match: Token('divide', None)),
		LexRule(compile(r'\^'), lambda match: Token('pow', None)),
		LexRule(compile(r'\('), lambda match: Token('(', None)),
		LexRule(compile(r'\)'), lambda match: Token(')', None))
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


if __name__ == '__main__':
	import sys, readline

	parser = Parser(CalculatorGrammar.expressions, CalculatorGrammar.precedence)
	lexer = Lexer(CalculatorGrammar.grammar)

	while True:
		try:
			inputText = input('> ')
			if not inputText:
				continue
			tokens = list(lexer.lex(inputText))

			print('Lexer results:')
			print(tokens)
			print('')

			parsed = parser.parse(tokens)

			print('Parser results:')
			print(parsed)

			if any(parsed):
				print('\nValue:')
				print(parsed[-1].value)
		except EOFError:
			print('')
			sys.exit()
		except Lexer.LexError:
			print('Couldn’t lex your input')
			continue
		except Parser.ParseError as e:
			print('Parse error. Stack:')
			print(e.stack)
		except:
			import traceback
			traceback.print_exc()
