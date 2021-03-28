from lamp_types import Lamp, Lantern, Channel

def load(*args, **named):

	lamp = Lamp(*args, channels=[Channel() for v in range(15)], **named)
	lamp.lanterns = [Lantern(lamp, [None]*3) for i in range(5)]
	for channel_no, item in enumerate('G2 B2 R1 R3 G3 G1 B3 R2 B1 R5 G4 R4 B4 G5 B5'.split()):
		color, lantern_str = item
		lantern = int(lantern_str)
		lamp.lanterns[lantern-1].rgb_chan['RGB'.index(color)] = channel_no

	return lamp