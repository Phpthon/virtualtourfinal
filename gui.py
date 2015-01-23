import pygame
from event.EventHandler import IEventHandler, EventDispatcher
from event.Events import ButtonClickEvent, SliderEvent, CheckBoxEvent, LabelChange
from misc.Constants import *
import math
import time
import random

class Component(pygame.Surface, IEventHandler):

	def __init__(self, size, parent, offset=(0, 0), name="untitled", **kwargs):

		pygame.Surface.__init__(self, size, **kwargs)
		self.rect = self.get_rect().copy()
		self.rect.x += offset[0]
		self.rect.y += offset[1]

		self.parent = parent
		self.event_rect = self.rect.copy()
		self.event_rect.x, self.event_rect.y = parent.rect.x + offset[0], parent.rect.y + offset[1]
		self.name = name

	def update(self, timer):
		pass
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

		self.counter = 0

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
						self.counter += 1
						EventDispatcher().send_event(ButtonClickEvent(self.name, str(self.counter)))
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
				
			self.parent.blit(self, self.rect)
			return True
		return False
