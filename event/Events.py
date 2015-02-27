class Event(object):
	def __init__(self, name):
		self.name = name

	def istype(self, type):
		return isinstance(self, type)

class SliderEvent(Event):
	def __init__(self, name, slidervalue):
		Event.__init__(self, name)
		self.slidervalue = slidervalue

class MouseEvent(Event):
	def __init__(self):
		Event.__init__(self)

class ButtonClickEvent(Event):
	def __init__(self, name):
		Event.__init__(self, name)

class CheckBoxEvent(Event):
	def __init__(self, name, checked):
		Event.__init__(self, name)
		self.checked = checked

class LabelChange(Event):
	def __init__(self, name, string):
		Event.__init__(self, name)
		self.string = string

class LevelChangeEvent(Event):
	def __init__(self, name, level):
		Event.__init__(self, name)
		self.level = level

class LightChangeEvent(Event):
	def __init__(self, status):
		Event.__init__(self, None)
		self.status = status