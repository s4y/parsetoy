from collections import namedtuple

Token = namedtuple('Token', ( 'type', 'value' ))

tokens = [ Token('number', 10), Token('+', None), Token('number', 3), Token('+', None), Token('number', 5) ]
stack  = []

while True:
	if len(stack) and stack[-1].type == 'number':
		stack[-1] = Token('expression', stack[-1].value)
	elif len(stack) >= 3 and stack[-3].type == 'expression' and stack[-2].type == '+' and stack [-1].type == 'expression':
		r = stack.pop();
		stack.pop();
		l = stack.pop();
		stack.append(Token('expression', l.value + r.value))
	elif len(tokens):
		stack.append(tokens[0])
		del tokens[0]
	elif len(stack) == 1:
		break
	else:
		print "Parse error"
		break

print 'Stack: %s' % (stack,)
