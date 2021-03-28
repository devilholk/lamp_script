#!/usr/bin/env python3
import argparse, serial, time, random, re, sys
from math import e
from lamp_5strip import load as load_5strip
from color_definitions import get_color, lerp_color

max_frame_skip = 8

class defaults:
	function = 'static'
	pattern = '12121'
	lerp_filter = 'linear'
	order = 'cycle_up'
	no_reset = False
	device = '/dev/ttyUSB0'
	baud = 921600
	speed = 60.0
	frame_rate = 1000
	cycle_stop = 0

class order_variants:
	@staticmethod
	def random_init(indices):
		source = random.choice(tuple(indices))
		dest = random.choice(tuple(indices - {source}))
		return source, dest

	@staticmethod
	def random_next(indices, source, dest):
		return dest, random.choice(tuple(indices - {dest}))



	@staticmethod
	def cycle_up_init(indices):
		return 0, 1

	@staticmethod
	def cycle_up_next(indices, source, dest):
		return dest, (dest + 1) % len(indices)

class lerp_filters:
	@staticmethod
	def linear(x):
		return x

	@staticmethod
	def sigmoid(x):
		w = 6
		w2 = w * 2
		return 1 / (1+e**-(w - w2 * (1-x)))


class lamp_functions:
	@staticmethod
	def static(lamp,  args):
		pattern = args.pattern
		colors = [get_color(c) for c in args.colors]

		for lantern, entry in zip(lamp.lanterns, pattern):
			lantern.set_color(*colors[int(entry)-1])

		lamp.update()

	@staticmethod
	def lerp_cycle(lamp,  args):
		pattern_list = [p.strip() for p in args.pattern.split(',')]

		color_list = ' '.join(args.colors)
		frame_rate = args.frame_rate
		color_cycle = [[get_color(c) for c in colors.split()] for colors in color_list.split(',')]
		color_cycle_length = len(color_cycle)
		lerp_filter = getattr(lerp_filters, args.lerp_filter)

		if len(pattern_list) == len(color_cycle):
			pass
		elif len(pattern_list) == 1:
			pattern_list = [pattern_list[0] for c in color_cycle]
		else:
			raise Exception('Currently pattern has to be either same length as color cycle or just one entry')


		cycle_stop = args.cycle_stop
		position = 0
		increment = args.speed / 60 / frame_rate
		indices = set(range(color_cycle_length))

		order = args.order
		source_index, dest_index = getattr(order_variants, f'{order}_init')(indices)
		next_function = getattr(order_variants, f'{order}_next')

		frame_duration = 1 / frame_rate
		time_reference = time.monotonic()
		
		while True:
			lerp_factor = lerp_filter(position)
			
			source_pattern = pattern_list[source_index]
			dest_pattern = pattern_list[dest_index]

			for lantern, (p1, p2) in zip(lamp.lanterns, zip(source_pattern, dest_pattern)):
				p1i, p2i = int(p1)-1, int(p2)-1			
				lantern.set_color(*lerp_color(color_cycle[source_index][p1i], color_cycle[dest_index][p2i], lerp_factor))
								
			lamp.update()

			last_time_reference = time_reference
			time_reference = time.monotonic()
			delta_time = time_reference - last_time_reference
			if delta_time > frame_duration * max_frame_skip:
				print("CPU is too slow for this frame rate")
				position = position + increment * max_frame_skip
			elif delta_time > frame_duration:
				#We are too slow so we will increase increment
				position = position + increment * delta_time / frame_duration
			else:
				#We need to wait (which means we are not too slow)
				time.sleep(frame_duration - delta_time)
				print(frame_duration - delta_time)

			position = position + increment

			if position > 1:
				position %= 1
				source_index, dest_index = next_function(indices, source_index, dest_index)
				if cycle_stop > 0:
					time.sleep(cycle_stop)
					time_reference = time.monotonic()	#When pausing we need to get a new time_reference




order_re = re.compile(r'^(\w+)_init$')
function_re = lerp_re = re.compile(r'^([^\W_]+\w*)$')

parser = argparse.ArgumentParser(
	formatter_class=argparse.ArgumentDefaultsHelpFormatter,
	epilog=f'Example usage: {sys.argv[0]} -p 12321 -l sigmoid -s 10 -f lerp_cycle -o \\ cycle_up magenta green white, red amber yellow, blue cyan white -c 3'
)
parser.add_argument("colors", nargs='+',
	help='List of colors, groups can be separated by commas')
parser.add_argument("-p", "--pattern", default=defaults.pattern,
	help='List of patterns, groups can be separated by commas')
parser.add_argument("-f", "--function", default=defaults.function, choices=[i.group(1) for i in map(function_re.match, dir(lamp_functions)) if i],
	help='Function to perform')
parser.add_argument("-R", "--no-reset", default=defaults.no_reset, action='store_true',
	help='Do not use serial port DTR and RTS to reset lamp')
parser.add_argument("-d", "--device", default=defaults.device,
	help='Device node to connect with')
parser.add_argument("-b", "--baud", default=defaults.baud, type=int,
	help='Baud rate of communication interface')
parser.add_argument("-s", "--speed", default=defaults.speed, type=float,
	help='Color stops per minute')
parser.add_argument("-l", "--lerp-filter", default=defaults.lerp_filter, choices=[i.group(1) for i in map(lerp_re.match, dir(lerp_filters)) if i],
	help='Filter for linear interpolation')
parser.add_argument("-r", "--frame-rate", default=defaults.frame_rate, type=float,
	help='Frame rate')
parser.add_argument("-c", "--cycle-stop", default=defaults.cycle_stop, type=float,
	help='Duration of pause between cycles when cycling through colors')
parser.add_argument("-o", "--order", default=defaults.order, choices=[i.group(1) for i in map(order_re.match, dir(order_variants)) if i],
	help='What order to use for cycling')

args = parser.parse_args()


port = serial.Serial(args.device, args.baud)
if not args.no_reset:
	port.setDTR(True)
	port.setRTS(True)
	port.setRTS(False)


function = getattr(lamp_functions, args.function)
lamp = load_5strip(port)
function(lamp, args)
