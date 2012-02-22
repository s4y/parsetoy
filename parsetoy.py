from collections import namedtuple

Token = namedtuple('Token', ( 'type', 'value' ))
Rule = namedtuple('Rule', ( 'operator', 'inputs', 'handler' ))

rules = (
	Rule(None, ( 'number', ), lambda n: Token('expression', n.value)),
	Rule('+', ( 'expression', '+', 'expression' ), lambda l, op, r: Token('expression', l.value + r.value) )
)

tokens = [
	Token('number', 10),
	Token('+', None),
	Token('number', 3),
	Token('+', None), Token('number', 5)
]
stack  = []

while True:
	for rule in rules:
		if len(stack) >= len(rule.inputs) and all( a == b for a, b in zip(rule.inputs, (t.type for t in stack[-len(rule.inputs):]))):
			stack[-len(rule.inputs):] = [rule.handler(*stack[-len(rule.inputs):])]
			break
	else:
		if len(tokens):
			stack.append(tokens[0])
			del tokens[0]
		elif len(stack) == 1:
			break
		else:
			print "Parse error"
			break

print 'Stack: %s' % (stack,)
