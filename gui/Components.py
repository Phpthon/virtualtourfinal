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