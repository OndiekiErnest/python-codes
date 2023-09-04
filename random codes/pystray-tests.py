from PIL import Image, ImageDraw
from pystray import Icon as icon, Menu as menu, MenuItem as item


state = 0
def set_state(v):
	def inner(icon, item):
		global state
		state = v
	return inner

def get_state(v):
	def inner(item):
		return state == v
	return inner

def create_image():
	# Generate an image and draw a pattern
	image = Image.new('RGB', (20, 20), "blue")
	dc = ImageDraw.Draw(image)
	dc.rectangle((20 // 2, 0, 20, 20 // 2),
		fill="red")
	dc.rectangle((0, 20 // 2, 20 // 2, 20),
		fill="red")
	return image
# Let the menu items be a callable returning a sequence of menu
# items to allow the menu to grow
icon('test', create_image(), menu=menu(lambda: (
item(
	'State %d' % i,
	set_state(i),
	checked=get_state(i),
	radio=True)
	for i in range(max(5, state + 2))))).run()
