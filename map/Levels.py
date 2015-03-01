import pygame
from gui.Gui import Gui
from gui.Components import *
from event.EventHandler import IEventHandler, EventDispatcher
from event.Events import SliderEvent, CheckBoxEvent, ButtonClickEvent, LabelChange, LevelChangeEvent
from threading import Thread
from time import sleep
from misc.Constants import *
from misc.Entity import *
from misc.path.astar import *
import random
from abc import ABCMeta, abstractmethod

# abstract class containing the update method that all sub classes should implement
class Level(pygame.Surface):
	
	__metaclass__ = ABCMeta

	# abstractmethod - must be implemented in all subclasses
	@abstractmethod
	def update(self, time, events):
		raise NotImplementedError("Subclasses must implement the abstract method")

	def __init__(self, size=(500,500)):
		pygame.Surface.__init__(self, size)

# main menu class that draws the main menu screen
class MainMenu(Level, IEventHandler):

	def __init__(self):
		Level.__init__(self, size=(500, 500))
		IEventHandler.__init__(self)

		self.gui = Gui(self, (500, 500), offset=(0, 0))

		component = PlayTitle("Python Virtual Robot", self.gui, offset=(self.gui.rect.center[0]-105, 50))
		component.name = "test"
		self.gui.add_component(component)

		component = Button("Start", 2, self.gui, offset=(self.gui.rect.center[0]-50, 130))
		component.name = "start"
		self.gui.add_component(component)

		component = Button("Exit", 0, self.gui, offset=(self.gui.rect.center[0]-50, 190))
		component.name = "exit"
		self.gui.add_component(component)

	def update(self, time, events):
		self.gui.update(time, events)

	def event_handler(self, event):
		if event.istype(ButtonClickEvent) and event.name == "start":
			EventDispatcher().send_event(LevelChangeEvent("test", LEVEL_GAME))

class GameLevel(Level, IEventHandler):

	def __init__(self):
		Level.__init__(self, size=(860, 800))
		IEventHandler.__init__(self)
		self.state = False
		self.time = 0

		self.game = GameSurface(self)

		#self.gui_ = Gui(self, (300, 300), offset=(100, 100))
		#component = MainTitle(self.gui_, offset=(0, 0))
		#self.gui_.add_component(component)

		self.gui = Gui(self, (260, 800), offset=(600, 0))

		component = MainTitle(self.gui, offset=(0, 0))
		self.gui.add_component(component)

		component = OrangeLabel("", "0.0", self.gui, offset=(155, 20), size=(70, 16))
		component.name = "current_time"
		self.gui.add_component(component)

		component = Title("Robot 1 : Automated", self.gui, 0, offset=(25, 100))
		self.gui.add_component(component)

		component = Slider("Velocity", self.gui, offset=(25, 145), increment=10.0, minvalue=150.0, maxvalue=300.0)
		component.name = "velocityai"
		self.gui.add_component(component)

		component = OrangeLabel("Position (x, y)", "0.0", self.gui, offset=(25, 200))
		component.name = "positionai"
		self.gui.add_component(component)

		component = OrangeLabel("Bearing (degrees)", "0.0", self.gui, offset=(25, 220))
		component.name = "bearingai"
		self.gui.add_component(component)

		component = OrangeLabel("Score", "0.0", self.gui, offset=(25, 240))
		component.name = "scoreai"
		self.gui.add_component(component)

		component = OrangeLabel("", "N/A", self.gui, offset=(25, 260))
		component.name = "locationai"
		self.gui.add_component(component)


		component = TreasureSelector(self.gui, offset=(30, 280))
		component.name = "treasureselector"
		self.gui.add_component(component)


		component = Slider("Sort Speed", self.gui, offset=(25, 420), increment=1.0, minvalue=0.0, maxvalue=25.0)
		component.name = "treasurevelocitychange"
		self.gui.add_component(component)
		
		#treasurevelocitychange

		component = Title("General Settings", self.gui, 2, offset=(25, 645))
		self.gui.add_component(component)

		#component = TrafficLight(self.gui, offset=(180, 530))
		#component.name = "light"
		#self.gui.add_component(component)

		component = Button("Pause", 3, self.gui, offset=(30, 690))
		component.name = "pause"
		self.gui.add_component(component)

		component = Button("Menu", 1, self.gui, offset=(135, 690))
		component.name = "menu"
		self.gui.add_component(component)

		component = Button("Reset Trap", 4, self.gui, offset=(60, 620))
		component.name = "trapreset"
		self.gui.add_component(component)

		component = CheckBox("Sort Descending", self.gui, offset=(25, 475))
		component.name = "sortdescending"
		self.gui.add_component(component)

		component = CheckBox("Display Traps", self.gui, offset=(25, 495))
		component.name = "displaytraps"
		self.gui.add_component(component)

		component = CheckBox("Display Treasures", self.gui, offset=(25, 515))
		component.name = "displaytreasure"
		self.gui.add_component(component)

		component = OrangeLabel("Time Running", "0.0", self.gui, offset=(25, 730))
		component.name = "time"
		self.gui.add_component(component)

		component = OrangeLabel("FPS", "0.0", self.gui, offset=(25, 750))
		component.name = "fps"
		self.gui.add_component(component)

		# add pause button to component array at end due to updating issues
		component = Button("Pause Ro...", 3, self.gui, offset=(60, 590))
		component.name = "pauserobot"
		self.gui.add_component(component)

	def update(self, time, events):
		self.gui.update(time, events)
		self.game.update(time, events)
		#self.gui_.update(time, events)
		#self.blit(self.gui_, self.gui_.rect)
		#self.gui1.update(time, events)

	def event_handler(self, event):
		if event.istype(ButtonClickEvent) and event.name == "pauserobot":
			self.gui.remove_component(self.gui.get_component("pauserobot"))

			component = Button("Resume Ro...", 2, self.gui, offset=(60, 590))
			component.name = "resumerobot"
			self.gui.add_component(component)

			for entity in self.game.known_entities:
				if isinstance(entity, Robot):
					entity.velocity = 0

		if event.istype(ButtonClickEvent) and event.name == "resumerobot":
			self.gui.remove_component(self.gui.get_component("resumerobot"))

			component = Button("Pause Ro...", 3, self.gui, offset=(60, 590))
			component.name = "pauserobot"
			self.gui.add_component(component)

			for entity in self.game.known_entities:
				if isinstance(entity, Robot):
					entity.velocity = entity.previous_velocity


class GameSurface(Level, IEventHandler):

	def __init__(self, parent):
		Level.__init__(self, size=(600, 800))
		IEventHandler.__init__(self)
		self.parent = parent
		self.mapimg = pygame.image.load(json_settings["map_img"])
		self.rect = self.mapimg.get_rect()

		self.nodegraph = NodeGraph(self)
		self.astar = AStar(self.nodegraph.graph)

		self.blit(self.mapimg, self.rect)
		self.landmarks = []
		self.display_treasures = False
		self.display_traps = False
		for landmark in json_settings["landmarks"]:
			self.landmarks.append(Landmark(landmark))

		self.update_timer = 0

		self.known_entities = []
		self.robots = []
		robot = RobotAI(self)

		self.obstacles = []
		
		self.known_entities.append(robot)
		self.robots.append(robot)

		entity = Cloud(self)
		self.known_entities.append(entity)
		self.obstacles.append(entity)

		entity = Cloud(self)
		self.known_entities.append(entity)
		self.obstacles.append(entity)

		self.treasures = []
	
	def update(self, time, events):

		if len(self.treasures) == 0:
			for i in range(0, 5):
				treasure = Treasure(self)
				collision = False
				for entity in self.known_entities:
					if (isinstance(entity, Cloud) or isinstance(entity, Treasure)) and entity.rect.colliderect(treasure.rect):
						collision = True
				if not collision:
					self.treasures.append(treasure)
					self.known_entities.append(treasure)

		for entity in self.known_entities:
			self.blit(self.mapimg.subsurface(entity.previous_rect.x, entity.previous_rect.y, entity.previous_rect.width, entity.previous_rect.height), entity.previous_rect)

		# remove all of the unrequired entities from the list of know entities
		for entity in self.known_entities:
			if entity.remove:
				self.known_entities.remove(entity)

		self.update_timer += time

		for i in range(0, len(self.known_entities)):

			self.known_entities[i].update(time, events)

			if isinstance(self.known_entities[i], Robot):

				for entity in self.known_entities:
					if isinstance(entity, Treasure) and not entity.remove:
						if self.known_entities[i].rect.colliderect(entity.rect):
							self.known_entities[i].score += entity.score
							indicator = ScoreIndicator(self, self.known_entities[i].x, self.known_entities[i].y, entity.score)
							self.known_entities.append(indicator)
							self.treasures.remove(entity)
							entity.remove = True
					if isinstance(entity, Cloud) and not entity.remove:
						collide_obstacle = self.known_entities[i].rect.colliderect(entity.rect)
						if collide_obstacle and not entity.in_collision:
							# remove some points from the robot
							indicator = ScoreRemoveIndicator(self, self.known_entities[i].rect.x, self.known_entities[i].rect.y, 50)
							self.known_entities.append(indicator)
							self.known_entities[i].score -= 50
							entity.in_collision = True
						elif not collide_obstacle and entity.in_collision:
							entity.in_collision = False

		# do some updates to the gui
		if self.update_timer > 0.25:
			self.update_timer = 0
			for robot in self.robots:
				EventDispatcher().send_event(LabelChange("bearing"+robot.type, str(robot.bearing)))
				EventDispatcher().send_event(LabelChange("position"+robot.type, "(" + str(robot.rect.center[0]) + ", " + str(robot.rect.center[1]) + ")"))
				EventDispatcher().send_event(LabelChange(str("score"+robot.type), str(robot.score)))

				points = pygame.sprite.spritecollide(robot, self.landmarks, False)
				if len(points) > 0:
					loc = ""
					for landmark in points:
						loc += landmark.name + "/"
					EventDispatcher().send_event(LabelChange("location"+robot.type, loc))

				else:
					EventDispatcher().send_event(LabelChange("location"+robot.type, "N/A"))

		#self.parent.blit(self, self.rect)

	# override the blit method in case we need to do anything with it later on
	def blit(self, surface, rect):
		#if rect.right > self.rect.width: rect.right = self.rect.width
		#if rect.left < 0: rect.left = 0
		#if rect.top < 0: rect.top = 0
		#if rect.bottom > self.rect.height: rect.bottom = self.rect.height

		self.parent.blit(surface, rect)

		#super(Level, self).blit(surface, rect)

	def event_handler(self, event):
		if event.istype(CheckBoxEvent) and event.name == "displaypath":
			if event.checked:
				self.color = (255, 255, 255)
			else:
				self.color = (0, 0, 0)
		if event.istype(ButtonClickEvent) and event.name == "menu":
			EventDispatcher().send_event(LevelChangeEvent(None, LEVEL_MAIN_MENU))
		if event.istype(SliderEvent) and event.name == "bearing":
			for robot in self.robots:
				if not robot.type == "ai":
					robot.bearing = event.slidervalue
					robot.timer = 0
		if event.istype(SliderEvent) and event.name == "velocity":
			for robot in self.robots:
				if not robot.type == "ai":
					robot.velocity = event.slidervalue
					robot.previous_velocity = event.slidervalue
		if event.istype(SliderEvent) and event.name == "velocityai":
			for robot in self.robots:
				if robot.type == "ai":
					robot.velocity = event.slidervalue
					robot.previous_velocity = event.slidervalue
			
		if event.istype(CheckBoxEvent) and event.name == "displaytreasure":
			self.display_treasures = event.checked
		if event.istype(CheckBoxEvent) and event.name == "displaytraps":
			self.display_traps = event.checked
		if event.istype(ButtonClickEvent) and event.name == "trapreset":
			# do something with flashing indicator
			for entity in self.known_entities:
				if isinstance(entity, FlashingIndicator):
					entity.remove = True

			text = ["Please click anywhere to place a treasure", "Now use the gui to adjust the value of the treasure"]
			indicator = FlashingIndicator(self, y=20, text=text[random.randint(0, len(text)-1)], duration=-1, colour=(92, 92, 92))
			self.known_entities.append(indicator)



			for obstacle in self.obstacles:
				obstacle.change_position()

class PauseMenu(Level):

	def __init__(self, parent):
		Level.__init__(self, size=(parent.get_rect().width, parent.get_rect().height))

		self.gui = Gui(self, size=(parent.get_rect().width, parent.get_rect().height), offset=(0, 0))

		component = PlayTitle("Paused", self.gui, offset=(parent.get_rect().width / 2 - 35, 300))
		self.gui.add_component(component)

		component = Button("Resume", 2, self.gui, offset=(parent.get_rect().width / 2 - 50, 350))
		component.name = "resume"
		self.gui.add_component(component)

		self.init = False

	def update(self, time, events):
		self.gui.update(time, events)