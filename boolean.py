"""
Parser for the following grammar:

<expression>::=<term>{'or' <term>}
<term>::=<factor>{'and' <factor>}
<factor>::=<identifier>|'not'<factor>|(<expression>)
Identifier: a single word of alphanumeric characters
"""

class Or:
	def __init__ (self):
		self.left = None
		self.right = None

	def to_string (self):
		return "(" + self.left.to_string() + " or " + self.right.to_string() + ")"

	def evaluate (self, a_line):
		return self.left.evaluate(a_line) or self.right.evaluate(a_line)

class And:
	def __init__ (self):
		self.left = None
		self.right = None

	def to_string (self):
		return "(" + self.left.to_string() + " and " + self.right.to_string() + ")"

	def evaluate (self, a_line):
		return self.left.evaluate(a_line) and self.right.evaluate(a_line)

class Not:
	def __init__ (self):
		self.child = None

	def to_string (self):
		return "not " + self.child.to_string()

	def evaluate (self, a_line):
		return not self.child.evaluate(a_line)

class Literal:
	def __init__ (self, a_identifier):
		self.identifier = a_identifier

	def to_string (self):
		return self.identifier

	def evaluate (self, a_line):
			# TODO: This expression matches any character sequence.
			# We could instead use a regular expression to match whole words.
		return self.identifier in a_line

def tokenize (stream):
	result = []
	token = ""

	def extend (a_token):
		if a_token != "":
			result.append (a_token)

	for c in stream:
		if c == '(' or c == ')':
			extend (token)
			extend (c)
			token = ""
		elif c.isspace():
			extend (token)
			token = ""
		elif c.isalnum():
			token = token + c
		else:
			raise Exception ("Lexer error: Invalid character in input string.")
	extend (token)
	return result

class Parser:
	def __init__ (self, a_input):
		self.tokens = tokenize (a_input)

	def parse (self):
		self.symbol = None
		self.root = None
		self.index = 0

		self.expression()
		if self.symbol != None:
			raise Exception ("Parser error: Input not fully consumed.")
		return self.root

	def expression (self):
		self.term()
		while self.symbol == 'or':
			l_or = Or()
			l_or.left = self.root
			self.term()
			l_or.right = self.root
			self.root = l_or

	def term (self):
		self.factor()
		while self.symbol == 'and':
			l_and = And()
			l_and.left = self.root
			self.factor()
			l_and.right = self.root
			self.root = l_and

	def factor (self):
		self._next()
		if self.symbol == 'not':
			l_not = Not()
			self.factor()
			l_not.child = self.root
			self.root = l_not
		elif self.symbol == '(':
			self.expression()
			if self.symbol != ')':
				raise Exception ("Parser error: No matching right parenthesis found.")
			else:
				self._next() # Ignore ')'
		elif self.symbol == ')':
			raise Exception ("Parser error: Unexpected right parenthesis")
		else:
			if self.symbol == None or self.symbol == 'and' or self.symbol == 'or':
				raise Exception ("Parser error: Unexpected symbol or end of stream.")
			l_literal = Literal (self.symbol)
			self.root = l_literal
			self._next()

	def _next (self):
		if len (self.tokens) > self.index:
			self.symbol = self.tokens [self.index]
		else:
			self.symbol = None
		self.index = self.index + 1

def test():
	print (tokenize ("A and B and 234 or C and not (e and F and scoop2345)"))
	print (tokenize (" A and    B and (234) or C and not 	(e and F and scoop2345)"))
	t = Parser ("a and b and not c")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("a and (b and not c)")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("a and (b) and (not c)")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("a and b and not c and d and e or f")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("a and (b and not c)")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("(a and b) and not c")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("a or b and not c")
	print (t.tokens)
	print (t.parse().to_string())
	t = Parser ("a or( b )and (not c)")
	print (t.tokens)
	print (t.parse().to_string())

	t = Parser ("(scoop or benchmark) and not fail")
	f = t.parse()
	print (f.evaluate ("scoop multithreaded asdf"))
	print (f.evaluate ("benchmark fail"))
	print (f.evaluate ("benchmark pass"))
	print (f.evaluate ("used_to_fail"))
