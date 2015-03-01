import pygame
from event.EventHandler import IEventHandler, EventDispatcher
from event.Events import *
from misc.Constants import *
import math
import time
import random
from abc import ABCMeta, abstractmethod

# abstract class containing the update method that all components should implement
class Component(pygame.Surface, IEventHandler):

	def __init__(self, size, parent, offset=(0, 0), name="untitled", **kwargs):

		pygame.Surface.__init__(self, size, **kwargs)
		self.rect = self.get_rect().copy()
		self.rect.x += offset[0]
		self.rect.y += offset[1]

		self.parent = parent
		self.event_rect = self.rect.copy()
		self.event_rect.x, self.event_rect.y = parent.rect.x + self.rect.x, parent.rect.y + self.rect.y
		self.name = name

	def get_position_locally(self, mouse_position):
		return (mouse_position[0] - self.parent.rect.x - self.rect.x, mouse_position[1] - self.parent.rect.y - self.rect.y)

	__metaclass__ = ABCMeta

	# abstractmethod - must be implemented in all subclasses
	@abstractmethod
	def update(self, time, events):
		raise NotImplementedError("Subclasses must implement the abstract method")

class Button(Component):

	icons = pygame.image.load("assets/img/button_icon_sprites.png")
	background = pygame.image.load("assets/img/button_sprites.png")

	def __init__(self, text, sprite, parent, **kwargs):

		Component.__init__(self, (100, 25), parent, **kwargs)
		#self.fill((220,20,60))
		self.clicked = False
		self.hovered = False
		self.init = False
		self.text = text
		self.size = (100, 25)

		self.states = [Button.background.subsurface((0, 0, 100, 25)),
						Button.background.subsurface((0, 25, 100, 25)),
						Button.background.subsurface((0, 50, 100, 25))]
		if sprite is not None:
			self.icon_states = [Button.icons.subsurface((sprite*16, 0, 16, 16)),
								Button.icons.subsurface((sprite*16, 16, 16, 16)),
								Button.icons.subsurface((sprite*16, 32, 16, 16))]
		else:
			self.icon_states = None
		self.offset = (6, 4)

		self.font = pygame.font.Font(FONT_REGULAR, 12)

	def update(self, timer, events):
		update = False
		for event in events:
			if event.type == pygame.MOUSEMOTION:
				if self.event_rect.collidepoint(event.pos):
					update = True
					self.hovered = True
				else:
					if self.clicked or self.hovered:
						update = True
					self.clicked = False
					self.hovered = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.event_rect.collidepoint(event.pos):
					if not self.clicked:
						EventDispatcher().send_event(ButtonClickEvent(self.name))
					self.clicked = True
					update = True
			if event.type == pygame.MOUSEBUTTONUP:
				if self.event_rect.collidepoint(event.pos):
					update = True
					self.clicked = False

		if update or not self.init:
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			self.init = True
			if self.hovered:
				if self.clicked:
					self.blit(self.states[2], (0, 0))
					if self.icon_states is not None:
						self.blit(self.icon_states[2], self.offset)
				else:
					self.blit(self.states[1], (0, 0))
					if self.icon_states is not None:
						self.blit(self.icon_states[1], self.offset)
				fontimg = self.font.render(self.text.upper(), True, (249, 249, 249))
				self.blit(fontimg, (30, 8))
			else:
				self.blit(self.states[0], (0, 0))
				if self.icon_states is not None:
					self.blit(self.icon_states[0], self.offset)
				fontimg = self.font.render(self.text.upper(), True, (125, 125, 125))
				self.blit(fontimg, (30, 8))
				
			#self.parent.blit(self, self.rect)
			return True
		return False

class CheckBox(Component):

	sprites = pygame.image.load("assets/img/checkbox_sprites.png")

	def __init__(self, name, parent, **kwargs):
		Component.__init__(self, (210, 16), parent, **kwargs)

		self.clicked = False
		self.hovered = False
		self.init = False
		self.checked = False

		self.counter = 0
		self.font = pygame.font.Font(FONT_REGULAR, 12).render(name, True, (92, 92, 92))
		self.bg = CheckBox.sprites.subsurface((0, 0, 16, 16))
		self.bg_hover = CheckBox.sprites.subsurface((0, 16, 16, 16))
		self.tick = CheckBox.sprites.subsurface((0, 32, 16, 14))

	def update(self, timer, events):
		update = False
		for event in events:
			if event.type == pygame.MOUSEMOTION:
				if self.event_rect.collidepoint(event.pos):
					update = True
					self.hovered = True
				else:
					if self.hovered:
						update = True
					self.hovered = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.event_rect.collidepoint(event.pos):
					if self.checked:
						self.checked = False
						EventDispatcher().send_event(CheckBoxEvent(self.name, self.checked))
					else:
						self.checked = True
						EventDispatcher().send_event(CheckBoxEvent(self.name, self.checked))
					update = True

		if update or not self.init:
			self.init = True
			#self.fill(self.parent.background)
			
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			if self.hovered:
				self.blit(self.bg_hover, (0, 0))
			else:
				self.blit(self.bg, (0, 0))
			if self.checked:
				self.blit(self.tick, (2,0))
			self.blit(self.font, (26, 3))

			#self.parent.blit(self, self.rect)
			return True
		return False

class Title(Component):

	sprites = pygame.image.load("assets/img/title_sprites.png")

	def __init__(self, title, parent, sprite, **kwargs):
		Component.__init__(self, (210, 38), parent, **kwargs)
		self.sprite = Title.sprites.subsurface((0, sprite * 16, 16, 16))
		self.font = pygame.font.Font(FONT_REGULAR, 12).render(title, True, (0, 0, 0))
		self.init = False

	def update(self, timer, events):
		if not self.init:
			self.init = True
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			self.blit(self.sprite, (10, 10))
			self.blit(self.font, (40, 13))
			pygame.draw.line(self, (212, 212, 212), (0, self.rect.height-1), (self.rect.width, self.rect.height-1))
			#self.parent.blit(self, self.rect)

			return True
		return False

class OrangeLabel(Component, IEventHandler):

	def __init__(self, title, value, parent, size=(210, 16), **kwargs):
		Component.__init__(self, size, parent, **kwargs)
		IEventHandler.__init__(self)
		self.font = pygame.font.Font(FONT_REGULAR, 12)
		self.title = self.font.render(title, True, (92, 92, 92))
		self.value = self.font.render(value, True, (228, 174, 46))
		self.init = False
		self.test = 0

	def update(self, timer, events):

		if not self.init:
			self.init = True
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			#self.blit(self.sprite, (10, 10))
			self.blit(self.title, (0, 0))
			self.blit(self.value, (self.get_rect().width - self.value.get_rect().width, 0))
			
			#self.parent.blit(self, self.rect)

			return True
		return False

	def event_handler(self, event):
		if event.istype(LabelChange) and event.name == self.name:
			self.value = self.font.render(event.string, True, (228, 174, 46))
			self.init = False

class Slider(Component):

	slider_sprites = None

	def __init__(self, title, parent, offset=(0, 0), increment=10.0, minvalue=10.0, maxvalue=100.0, **kwargs):
		Component.__init__(self, (210, 38), parent, offset, **kwargs)

		if Slider.slider_sprites == None:
			sprites = pygame.image.load("assets/img/slider_sprites.png")
			Slider.slider_sprites = [
				sprites.subsurface((0,0,210,13)),
				sprites.subsurface((0,13,210,13)),
				sprites.subsurface((0,26,30,7)),
				sprites.subsurface((0,33,30,7))
			]

		# user options
		self.paddingright = 3
		self.paddingleft = 3
		self.increment = increment
		self.minvalue = minvalue
		self.maxvalue = maxvalue
		self.x, self.y = 0, 0

		# init the track
		self.track_rect = Slider.slider_sprites[0].get_rect().copy()
		self.track_rect.x = 0
		self.track_rect.y = 25

		# calc max start/end position of bar
		self.maxright = self.track_rect.right - self.paddingright
		self.maxleft = self.track_rect.x + self.paddingleft

		# init the bar
		self.bar_rect = Slider.slider_sprites[2].get_rect().copy()
		self.bar_rect.x = self.maxleft
		self.bar_rect.y = self.track_rect.y + 3

		self.click = False
		self.offset = None
		self.currentvalue = 0

		# calculate empty space between bar and padded edges along with the ratio
		self.emptyspace = self.maxright - self.maxleft - self.bar_rect.width
		self.ratio = ((self.maxvalue - self.minvalue) / self.increment) / self.emptyspace

		self.track_image = Slider.slider_sprites[0]
		self.bar_image = Slider.slider_sprites[2]

		self.track_rect_event = self.track_rect.copy()
		self.track_rect_event.x = self.track_rect.x + self.event_rect.x
		self.track_rect_event.y = self.track_rect.y + self.event_rect.y

		self.bar_rect_event = self.bar_rect.copy()
		self.bar_rect_event.x = self.bar_rect.x + self.event_rect.x
		self.bar_rect_event.y = self.bar_rect.y + self.event_rect.y

		self.font = pygame.font.Font(FONT_REGULAR, 12)
		self.label = self.font.render(title, True, (92, 92, 92))
		self.init = False

		self.hovered = False
		self.previousvalue = 0

	def update(self, timer, events):

		required = False

		for event in events:
			if event.type == pygame.MOUSEMOTION:
			
				if self.track_rect_event.collidepoint(event.pos):
					self._hovered(True)
					required = True
				elif not self.click and self.hovered:
					self._hovered(False)
					required = True
			if event.type == pygame.MOUSEBUTTONDOWN:

				if self.bar_rect_event.collidepoint(event.pos):
					required = True
					self._hovered_bar(True)
					self.click = True
					if self.offset is None:
						self.offset = event.pos[0] - self.bar_rect.x

			elif event.type == pygame.MOUSEBUTTONUP and self.hovered:
				required = True
				self.click = False
				self.offset = None
				self._hovered_bar(False)

		if required or self.click or not self.init:
			self.init = True
			self.fill(self.parent.background)

			if self.click:
				newpos = pygame.mouse.get_pos()[0] - self.offset
				if newpos + self.bar_rect.width < self.maxright and newpos > self.maxleft:
					self.bar_rect.right = newpos + self.bar_rect.width
					self.bar_rect_event.x = self.track_rect_event.left + self.paddingleft + newpos
				elif newpos + self.bar_rect.width > self.maxright:
					self.bar_rect.right = self.maxright
					self.bar_rect_event.right = self.track_rect_event.right - self.paddingright
				elif newpos < self.maxleft:
					self.bar_rect.left = self.maxleft
					self.bar_rect_event.left = self.track_rect_event.x + self.paddingleft

			self.currentvalue = self.myround( ( (self.bar_rect.left - self.maxleft ) * self.ratio) * self.increment + self.minvalue, self.increment)
			
			text = self.font.render(str(self.currentvalue), True, (41, 140, 218))

			self.blit(text, (self.track_rect.right - self.paddingright - text.get_rect().width, self.track_rect.y - 20))
			self.blit(self.label, (self.track_rect.left + self.paddingleft, self.track_rect.y - 20))

			self.blit(self.track_image, self.track_rect)
			self.blit(self.bar_image, self.bar_rect)

			#print self.track_rect
			#self.parent.blit(self, self.rect)

			if self.currentvalue is not self.previousvalue:
				EventDispatcher().send_event(SliderEvent(self.name, self.currentvalue))
				self.previousvalue = self.currentvalue

			return True
		return False

	def _hovered(self, is_hovered):
		self.hovered = is_hovered
		if is_hovered:
			self.track_image = Slider.slider_sprites[1]
		else:
			self.track_image = Slider.slider_sprites[0]

	def _hovered_bar(self, is_hovered):
		if is_hovered:
			self.bar_image = Slider.slider_sprites[3]
		else:
			self.bar_image = Slider.slider_sprites[2]

	def myround(self, x, base=5):
		return int(base * math.ceil(float(x)/base))


class FlashingLabel(Component, IEventHandler):

	def __init__(self, title, parent, **kwargs):
		Component.__init__(self, (210, 16), parent, **kwargs)
		IEventHandler.__init__(self)
		self.font = pygame.font.Font(FONT_REGULAR, 12)
		self.title = self.font.render(title, True, (92, 92, 92))
		self.init = False

		self.amount = 510
		self.direction = -1
		self.current = random.randint(0, 255)

	def update(self, timer, events):

		self.current += timer * self.direction * self.amount

		if self.current > 255:
			self.direction = -1
			self.current = 255
		elif self.current < 0:
			self.direction = 1
			self.current = 0

		if not self.init:
			self.init = True
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			#self.blit(self.sprite, (10, 10))
			self.blit(self.title, (0, 0))
			#self.parent.blit(self, self.rect)

			return True

		self.set_alpha(math.ceil(self.current))
		return True

	def event_handler(self, event):
		if event.istype(LabelChange) and event.name == self.name:
			self.value = self.font.render(event.string, True, (228, 174, 46))
			self.init = False

class MainTitle(Component):

	def __init__(self, parent, **kwargs):
		Component.__init__(self, (225, 100), parent, **kwargs)
		self.font = pygame.font.Font(FONT_REGULAR, 12)
		self.init = False

	def update(self, timer, events):

		if not self.init:
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			title = self.font.render("Python Virtual Robot", True, (0, 0, 0))
			value = self.font.render("Group B13A", True, (125, 125, 125))

			img = pygame.image.load("assets/img/python_sml.png")
			self.blit(img, (15, 15))
			self.blit(title, (self.rect.width - title.get_rect().width, 40))
			self.blit(value, (self.rect.width - value.get_rect().width, 60))
			self.init = True
			return True
		return False

class PlayTitle(Component, IEventHandler):

	def __init__(self, title, parent, **kwargs):
		Component.__init__(self, (210, 30), parent, **kwargs)
		IEventHandler.__init__(self)
		self.font = pygame.font.Font(FONT_REGULAR, 20)
		self.title = self.font.render(title, True, (0, 0, 0))
		self.init = False

		self.amount = 510
		self.direction = -1
		self.current = random.randint(0, 255)

	def update(self, timer, events):

		self.current += timer * self.direction * self.amount

		if self.current > 255:
			self.direction = -1
			self.current = 255
		elif self.current < 0:
			self.direction = 1
			self.current = 0

		if not self.init:
			self.init = True
			self.blit(self.parent.initial_image.subsurface(self.rect), (0,0))
			#self.blit(self.sprite, (10, 10))
			self.blit(self.title, (0, 0))
			#self.parent.blit(self, self.rect)

		self.set_alpha(math.ceil(self.current))
		return True

	def event_handler(self, event):
		if event.istype(LabelChange) and event.name is self.name:
			self.value = self.font.render(event.string, True, (228, 174, 46))
			self.init = False

class TrafficLight(Component):

	def __init__(self, parent, **kwargs):
		Component.__init__(self, (41, 88), parent, **kwargs)
		self.init = False

		lights = pygame.image.load("assets/img/trafficlights.png")
		self.red = lights.subsurface(0, 0, 15, 15)
		self.yellow = lights.subsurface(0, 15, 15, 15)
		self.green = lights.subsurface(0, 30, 15, 15)

		self.bg = pygame.image.load("assets/img/trafficlight.png")

		self.amount = 510
		self.direction = -1
		self.current = random.randint(0, 255)

		self.font = pygame.font.Font(FONT_REGULAR, 20)
		self.title = self.font.render("T", True, (255, 255, 255))
		self.title.set_alpha(0)

		self.timer = 0

		self.fill(self.parent.background)
		self.status = [False, False, False]

	def update(self, timer, events):

		self.timer += timer
		self.current += timer * self.direction * self.amount
		
		if self.current > 255:
			self.direction = -1
			self.current = 255
		elif self.current < 0:
			self.direction = 1
			self.current = 0

		if not self.init:
			self.init = True
			self.blit(self.parent.initial_image.subsurface(self.rect).copy(), (0,0))
		self.blit(self.bg.copy(), self.bg.get_rect())

		#pygame.draw.circle(self, (255, 255, 255), (0,0), 50)

		self.red.set_alpha(self.current)
		self.yellow.set_alpha(self.current)
		self.green.set_alpha(self.current)

		'''
		if self.timer < 10:
			if 1 < self.timer > 2:
				self.blit(self.red, (13, 15))
				EventDispatcher().send_event(LightChangeEvent(0))
				self.timer = random.randint(10, 18)
			elif self.timer > 1:
				self.blit(self.yellow, (13, 38))
				EventDispatcher().send_event(LightChangeEvent(1))
			elif self.timer < 1:
				self.blit(self.green, (13, 60))
				EventDispatcher().send_event(LightChangeEvent(2))
		else:
			if 20 < self.timer < 21:
				self.blit(self.red, (13, 15))
				self.blit(self.yellow, (13, 38))
				EventDispatcher().send_event(LightChangeEvent(1))
			elif self.timer < 20:
				self.blit(self.red, (13, 15))
				EventDispatcher().send_event(LightChangeEvent(0))
			elif self.timer > 21:
				self.blit(self.green, (13, 60))
				EventDispatcher().send_event(LightChangeEvent(2))
				self.timer = random.randint(-10, 0)
		return True
		'''

class TreasureSelectorTreasure(pygame.sprite.Sprite):

	def __init__(self, treasure):
		pygame.sprite.Sprite.__init__(self)

		surface = pygame.image.load("assets/img/treasure_bg.png")

		testfont = pygame.font.SysFont(FONT_REGULAR, 14)
		font_rendered = testfont.render(str(treasure.score), 1, (0, 0, 0))
		surface.blit(treasure.image, ((surface.get_rect().width/2)-(treasure.image.get_rect().width/2), 3))
		surface.blit(font_rendered, ((surface.get_rect().width/2)-(font_rendered.get_rect().width/2), (surface.get_rect().height)-(font_rendered.get_rect().height) - 3))
		self.image = surface

		self.rect = None
		self.x, self.y = 0.0, 0.0
		self.score = treasure.score
		self.target = None
		self.velocity = [1, 1]

	def has_target(self):
		if self.target is not None:
			return True
		return False

	def set_rect(self, rect):
		self.rect = rect
		self.x, self.y = rect.x, rect.y

	def set_target(self, target):
		self.target = target.rect.copy()
		if self.rect.x > target.rect.x:
			self.velocity[0] = -1
		elif self.rect.x < target.rect.x:
			self.velocity[0] = 1
		else:
			self.velocity[0] = 0

		if self.rect.y > target.rect.y:
			self.velocity[1] = -1
		elif self.rect.y < target.rect.y:
			self.velocity[1] = 1
		else:
			self.velocity[1] = 0

	def at_target_x(self):
		if self.rect.x == self.target.x or (self.rect.x > self.target.x and self.velocity[0] == 1) or (self.rect.x < self.target.x and self.velocity[0] == -1):
			self.rect.x = self.target.x
			self.x = self.rect.x
			return True
		return False

	def at_target_y(self):
		if self.rect.y == self.target.y or (self.rect.y > self.target.y and self.velocity[1] == 1) or (self.rect.y < self.target.y and self.velocity[1] == -1):
			self.rect.y = self.target.y
			self.y = self.rect.y
			return True
		return False

	def move(self, velocity):
		if self.target is not None:
			t_x, t_y = self.at_target_x(), self.at_target_y()
			if t_x and t_y:
				self.target = None
				return False
			if not t_x:
				self.x += velocity * self.velocity[0]
				self.rect.x = self.x
			if not t_y:
				self.y += velocity * self.velocity[1]
				self.rect.y = self.y
		return True

class TreasureSelector(Component, IEventHandler):

	def __init__(self, parent, **kwargs):
		Component.__init__(self, (202, 135), parent, **kwargs)
		IEventHandler.__init__(self)
		self.init = False
		#self.treasures = [TempTreasure(50), TempTreasure(1023), TempTreasure(122), TempTreasure(938), TempTreasure(234), TempTreasure(34)]
		self.treasures = []
		'''
		for i in range(0, 6):
			if i == 2 or i == 5 or i == 4:
				self.treasures.append(TempTreasure(100))
				continue

			self.treasures.append(TempTreasure(random.randint(50, 1500)))

		testfont = pygame.font.SysFont(FONT_REGULAR, 16)

		for i in range(0, len(self.treasures)):
			#surface = pygame.Surface((50, 50))
			surface = pygame.image.load("assets/img/treasure_bg.png")

			#surface.fill((212, 212, 212))
			font_rendered = testfont.render(str(self.treasures[i].score), 1, (0, 0, 0))
			surface.blit(font_rendered, ((surface.get_rect().width/2)-(font_rendered.get_rect().width/2), (surface.get_rect().height/2)-(font_rendered.get_rect().height/2)))
			self.treasures[i].image = surface
			if i < 3:
				self.treasures[i].set_rect(pygame.Rect(13 + (i*13) + (i*50), 15, 50, 50))
			else:
				self.treasures[i].set_rect(pygame.Rect(13 + ((i-3)*13) + ((i-3)*50), 70, 50, 50))
		'''
		self.swapping = False

		self.current_index = 0
		self.sort_encountered = False

		self.unsorted = True

		self.final_blit = False

		self.velocity = 0
		self.ascending = True

	def recalculate_positions(self):
		for i in range(0, len(self.treasures)):
			if not self.treasures[i].has_target():
				if i < 3:
					self.treasures[i].set_rect(pygame.Rect(13 + (i*13) + (i*50), 15, 50, 50))
				else:
					self.treasures[i].set_rect(pygame.Rect(13 + ((i-3)*13) + ((i-3)*50), 70, 50, 50))

		self.unsorted = True

	def update(self, timer, events):

		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				for treasure in self.treasures:
					if treasure.rect.collidepoint(self.get_position_locally(event.pos)):
						if not self.swapping:
							self.treasures.remove(treasure)
							self.recalculate_positions()

		if not self.unsorted and self.final_blit:
			return False

		if self.current_index == len(self.treasures) - 2:
			self.current_index = 0
			self.sort_encountered = False

		self.fill((232, 232, 232))

		swap_status = False
		blit_order = []
		for i in range(0, len(self.treasures)):
			if self.treasures[i].target is None:
				'''
				if self.swapping:
					self.treasures[i].image.set_alpha(100)
				else:
					self.treasures[i].image.set_alpha(255)
				'''

				blit_order.insert(0, self.treasures[i])
			else:
				# do something with the target
				self.treasures[i].image.set_alpha(255)
				self.treasures[i].move(self.velocity)
				swap_status = True
				blit_order.append(self.treasures[i])

		self.swapping = swap_status
		#print self.swapping

		for item in blit_order:
			self.blit(item.image, item.rect)

		# do some bubble magic
		# if not sorted and not swapping
		if self.unsorted and not self.swapping:
			index = self.current_index
			for i in range(index, len(self.treasures) - 1):
				if self.sort_encountered:
					self.unsorted = True
				else:
					self.unsorted = False
				self.current_index = i
				if (self.treasures[i].score > self.treasures[i + 1].score) == self.ascending and not self.treasures[i].score == self.treasures[i + 1].score:
					self.treasures[i].set_target(self.treasures[i + 1])
					self.treasures[i + 1].set_target(self.treasures[i])

					hold = self.treasures[i + 1]
					self.treasures[i + 1] = self.treasures[i]
					self.treasures[i] = hold

					self.unsorted = True
					self.swapping = True
					self.sort_encountered = True
					break

		if not self.unsorted and self.final_blit:
			self.final_blit = False
		else:
			self.final_blit = True

		return True

	def event_handler(self, event):
		if event.istype(SliderEvent) and event.name == "treasurevelocitychange":
			self.velocity = event.slidervalue
		if event.istype(CheckBoxEvent) and event.name == "sortdescending":
			self.unsorted = True
			self.ascending = not event.checked
		if event.istype(TreasureCollectEvent):
			if len(self.treasures) < 6:
				self.treasures.append(TreasureSelectorTreasure(event.treasure))
				self.recalculate_positions()
		if event.istype(RemoveEvent) and event.name == "removelasttreasure":
			self.treasures.pop(len(self.treasures)-1)
			self.recalculate_positions()

	def remove_last_treasure(self):
		if len(self.treasures) > 0:
			treasure = self.treasures.pop(len(self.treasures)-1)
			self.recalculate_positions()
			return treasure
		return False