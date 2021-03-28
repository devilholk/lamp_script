#Note - currently we use mul_color and add_color. Later we should just have a color class that supports __mul__ and so forth

colors = dict(
	red = 		(1, 0, 0),
	green = 	(0, 1, 0),
	blue = 		(0, 0, 1),
	black =		(0, 0, 0),
	yellow = 	(1, 1, 0),
	amber = 	(1, 0.6, 0),
	cyan = 		(0, 1, 1),
	magenta = 	(1, 0, 1),
	white = 	(1, 1, 1),
)


def parse_color(c):
	if c.startswith('#'):
		return [int('0x'+i, 16)/0xF for i in c[1:]]
	else:
		raise Exception(f'Is this a color? {c}')

def get_color(c):
	return colors.get(c.lower()) or parse_color(c)


def add_color(a, b):	#two equal size vectors
	return tuple(map(lambda a: a[0] + a[1], zip(a, b)))

def mul_color(a, b):	#one vector and one scalar	
	return tuple(map(lambda a: a * b, a))

def lerp_color(a, b, f):	
	return add_color(mul_color(a, 1-f), mul_color(b, f))