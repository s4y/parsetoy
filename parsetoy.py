# encoding=utf-8

from collections import namedtuple
import re, sys

Token = namedtuple('Token', ( 'type', 'value' ))
LexRule = namedtuple('LexRule', ( 'expression', 'handler' ))
ParseRule = namedtuple('ParseRule', ( 'operator', 'inputs', 'handler' ))

def lex(grammar, input):
	while len(input):
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
			raise Exception('Couldn’t parse your input')


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
				# Should be an exception, but want to see the stack for now
				print "Parse error"
				break
	return stack


if len(sys.argv) != 2:
	print 'usage: %s pattern' % (sys.argv[0],)
	sys.exit(1);

tokens = list(lex((
	LexRule(re.compile(r'\s+'), lambda match: None),
	LexRule(re.compile(r'(?:\.[0-9]+|[0-9]+(?:.[0-9]+)?)'), lambda match: Token('number', float(match))),
	LexRule(re.compile(r'\+'), lambda match: Token('+', None)),
	LexRule(re.compile(r'-'), lambda match: Token('-', None))
), sys.argv[1]))

print tokens

print parse((
	ParseRule(None, ( 'number', ), lambda n: Token('expression', n.value)),
	ParseRule('+', ( 'expression', '+', 'expression' ), lambda l, op, r: Token('expression', l.value + r.value) ),
	ParseRule('-', ( 'expression', '-', 'expression' ), lambda l, op, r: Token('expression', l.value - r.value) )
), tokens)
