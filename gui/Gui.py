import pygame
from gui.Components import *

class Gui(pygame.Surface):

	def __init__(self, parent, size=(100, 100), offset=(0, 0), background=(242, 242, 242), **kwargs):
		pygame.Surface.__init__(self, size, **kwargs)
		self.components = []
		self.parent = parent
		self.rect = self.get_rect()
		self.rect.x, self.rect.y = offset[0], offset[1]
		self.background = background
		self.python_bg = pygame.image.load("assets/img/python_bg.png")
		self.fill(self.background)
		self.blit(self.python_bg, (self.rect.width - self.python_bg.get_rect().width, self.rect.height - self.python_bg.get_rect().height))
		
		font = pygame.font.Font(FONT_REGULAR, 12)
		rectangle = pygame.Rect(0, self.rect.height - 30, self.rect.width, 30)
		pygame.draw.rect(self, (242, 242, 242), rectangle)
		
		pygame.draw.line(self, (232, 232, 232), (rectangle.x, rectangle.y-1), (rectangle.right, rectangle.y-1))

		software_label = font.render("Software Version", True, (92, 92, 92))
		self.blit(software_label, (15, rectangle.center[1] - (software_label.get_rect().height / 2)))

		software_version = font.render(json_settings["version"], True, (92, 92, 92))
		self.blit(software_version, (rectangle.right - software_version.get_rect().width - 15, rectangle.center[1] - (software_version.get_rect().height / 2)))

		self.parent.blit(self, self.rect)
		self.initial_image = self.copy()

	def redraw_initial(self):
		self.parent.blit(self.initial_image, self.rect)

	def add_component(self, component):
		self.components.append(component)

	def remove_component(self, component):
		if not component:
			return
		# deregister handler if the component was a handler
		if isinstance(component, IEventHandler):
			EventDispatcher().deregister_event(component)
		# update the region of the removed component
		self.parent.blit(self.initial_image.subsurface(component.rect).copy(), component.event_rect)
		self.components.remove(component)

	def get_component(self, name):
		for component in self.components:
			if component.name == name:
				return component
		return False

	def update(self, timer, events):
		for component in self.components:
			update = component.update(timer, events)
			if update:
				self.parent.blit(self.initial_image.subsurface(component.rect).copy(), component.event_rect)
				self.parent.blit(component, component.event_rect)
