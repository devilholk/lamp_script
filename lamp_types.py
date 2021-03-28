from utils import clamp
import struct

class Lamp:
	def __init__(self, port=None, channels=None, synchronous_mode=False):
		if channels:
			self.channels = list(channels)
		else:
			self.channels = list()

		self.port = port
		self.synchronous_mode = synchronous_mode

	def update(self):			
		packet = struct.pack('H'*15, *(c.value for c in self.channels))
		self.port.write(packet)
		self.port.flush()

		if self.synchronous_mode:
			self.port.read(1)


	def set_color(self, r, g, b):
		for l in self.lanterns:
			l.set_color(r, g, b)

class Channel:
	def __init__(self):
		self.value = 0


class Lantern:
	def __init__(self, lamp, rgb_chan=None):
		self.lamp = lamp
		self.rgb_chan = rgb_chan

	def __repr__(self):
		return '<%s of %r channels=%s>' % (self.__class__.__name__, self.lamp, ' '.join(repr(c) for c in self.rgb_chan))

	def set_color(self, r, g, b):
		rc, gc, bc = self.rgb_chan
		self.lamp.channels[rc].value = int(clamp(r)*4095)
		self.lamp.channels[gc].value = int(clamp(g)*4095)
		self.lamp.channels[bc].value = int(clamp(b)*4095)


