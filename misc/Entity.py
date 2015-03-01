from misc.Constants import *
import random, pygame, copy, time, threading, Queue
from abc import ABCMeta, abstractmethod
from event.EventHandler import *
from event.Events import *

# holds information about a landmark
class Landmark(object):
	def __init__(self, landmark):
		self.name = landmark["name"]
		self.rect = pygame.Rect(landmark["coords"][0], landmark["coords"][1], landmark["dimensions"][0], landmark["dimensions"][1])

# abstract class containing the update method to be implemented by all subclasses
class Entity(object):

	__metaclass__ = ABCMeta

	def __init__(self):
		self.remove = False

	# abstractmethod - must be implemented in all subclasses
	@abstractmethod
	def update(self, time, events):
		raise NotImplementedError("Subclasses must implement the abstract method")

class RemovableEntity(Entity, pygame.sprite.Sprite):

	def __init__(self):
		Entity.__init__(self)
		pygame.sprite.Sprite.__init__(self)

class ScoreIndicator(RemovableEntity):

	def __init__(self, parent, x, y, score, colour=(34, 49, 63)):
		RemovableEntity.__init__(self)
		self.parent = parent
		# put the treasure at a random position on the map
		self.x, self.y = x, y
		# get the image path from the json settings and load it
		self.font = pygame.font.SysFont(MAIN_FONT, 16)

		self.image = self.font.render(str(score), 1, colour)
		self.rect = pygame.Rect(self.x, self.y, self.image.get_rect().width, self.image.get_rect().height)
		self.previous_rect = self.rect.copy()

		# move the text 30 pixels
		self.movement = 30
		# the initial alpha value
		self.current_alpha = 0

		self.timer = 0
		self.remove = False

	def update(self, timer, events):

		self.previous_rect = self.rect.copy()

		self.timer += timer
		if self.timer > 1:
			# remove the object from the list on the next cycle
			self.remove = True
			return

		self.rect.y = self.y - (self.timer * self.movement)
		#self.current_alpha = int(255 - (self.timer * 255))

		#self.image.set_alpha(self.current_alpha)

		self.parent.blit(self.image, self.rect)

class ScoreRemoveIndicator(RemovableEntity):

	def __init__(self, parent, x, y, score):
		RemovableEntity.__init__(self)
		self.parent = parent
		# put the treasure at a random position on the map
		self.x, self.y = x, y
		# get the image path from the json settings and load it
		self.font = pygame.font.SysFont(MAIN_FONT, 16)

		self.image = self.font.render(" - " + str(score), 1, (255, 0, 0))
		self.rect = pygame.Rect(self.x, self.y, self.image.get_rect().width, self.image.get_rect().height)
		self.previous_rect = self.rect.copy()

		# move the text 30 pixels
		self.movement = 30
		# the initial alpha value
		self.current_alpha = 0

		self.timer = 0
		self.remove = False

	def update(self, timer, events):

		self.previous_rect = self.rect.copy()

		self.timer += timer
		if self.timer > 1:
			# remove the object from the list on the next cycle
			self.remove = True
			return

		self.rect.y = self.y - (self.timer * self.movement)
		#self.current_alpha = int(255 - (self.timer * 255))

		#self.image.set_alpha(self.current_alpha)

		self.parent.blit(self.image, self.rect)


class FlashingIndicator(RemovableEntity):

	def __init__(self, parent, y=-1, text="null", duration=-1, colour=(255, 51, 51)):
		RemovableEntity.__init__(self)
		self.parent = parent
		# put the treasure at a random position on the map

		font = pygame.font.SysFont(MAIN_FONT, 12)
		surface = font.render(text, 1, colour)

		mainsurface = pygame.Surface((surface.get_rect().width + 50, surface.get_rect().height + 10))
		mainsurface.fill((242, 242, 242))

		mainsurface.blit(surface, ((mainsurface.get_rect().width/2) - (surface.get_rect().width/2), (mainsurface.get_rect().height/2) - (surface.get_rect().height/2)))
		if y == -1:
			y = (parent.rect.height/2) - (mainsurface.get_rect().height/2)

		self.rect = pygame.Rect((parent.rect.width/2) - (mainsurface.get_rect().width/2), y, mainsurface.get_rect().width, mainsurface.get_rect().height)
		self.previous_rect = self.rect.copy()

		self.image = mainsurface
		self.duration = duration

		self.timer = 0
		self.remove = False

		self.amount = 255
		self.direction = 1
		self.current = 50

		self.timer_opaque = 1

	def update(self, timer, events):

		if self.duration != -1:
			self.timer += timer
			if self.timer > self.duration:
				# remove the object from the list on the next cycle
				self.remove = True
				return
		else:
			if self.remove:
				return

		self.previous_rect = self.rect.copy()

		self.timer_opaque += timer
		self.current += timer * self.direction * self.amount

		if self.timer_opaque < 1:
			self.current = 255
		elif self.current > 255:
			self.direction = -1
			self.current = 255
			self.timer_opaque = 0
		elif self.current < 50:
			self.direction = 1
			self.current = 50

		self.image.set_alpha(math.ceil(self.current))
		self.parent.blit(self.image, self.rect)

# treasure class extending entity and sprite class within the pygame library
# holds information about any given treasure on the map
class Treasure(Entity, pygame.sprite.Sprite):

	sprites = None

	def __init__(self, parent):
		Entity.__init__(self)
		pygame.sprite.Sprite.__init__(self)

		if Treasure.sprites is None:
			sprites = pygame.image.load("assets/img/treasure_sprites.png")
			Treasure.sprites = [sprites.subsurface(0, 0, 32, 32)
								, sprites.subsurface(32, 0, 32, 32)
								, sprites.subsurface(64, 0, 32, 32)]
			self.sprites = Treasure.sprites

		self.parent = parent
		# put the treasure at a random position on the map
		self.x = random.randint(50, self.parent.rect.width - 100)
		self.y = random.randint(50, self.parent.rect.height - 100)
		# get the image path from the json settings and load it
		self.image = self.sprites[0]
		self.rect = pygame.Rect(self.x, self.y, self.image.get_rect().width, self.image.get_rect().height)
		self.previous_rect = self.rect.copy()

		self.score = 0
		self.set_score(random.randint(0, 990))

	def set_score(self, score):
		if score < 250:
			self.image = self.sprites[0]
		elif score < 500:
			self.image = self.sprites[1]
		else:
			self.image = self.sprites[2]
		self.score = score

	def update(self, timer, events):
		self.previous_rect = self.rect.copy()
		# draw the current treasure if the user has opted to display treasures
		if self.parent.display_treasures:
			self.parent.blit(self.image, self.rect)

# cloud class extends entity and sprite class within pygame library
# holds information about any given storm/cloud on the map
class Cloud(Entity, pygame.sprite.Sprite):

	sprites = None

	def __init__(self, parent):
		Entity.__init__(self)
		pygame.sprite.Sprite.__init__(self)
		# load the cloud sprites into a static variable for reuse
		if Cloud.sprites == None:
			sprites = pygame.image.load("assets/img/cloud_sprites.png")
			Cloud.sprites = [sprites.subsurface(0, 0, 36, 31)
							, sprites.subsurface(36, 0, 36, 31)
							, sprites.subsurface(72, 0, 36, 31)]
		self.parent = parent
		self.sprites = Cloud.sprites
		self.rect = self.sprites[0].get_rect(center=(random.randint(100, parent.rect.width - 100), random.randint(100, parent.rect.height - 100)))
		self.timer = 0.0
		self.flash_period = random.uniform(0.5, 1)
		self.current_image = 0
		self.image = self.sprites[self.current_image]
		self.previous_rect = self.rect.copy()
		self.in_collision = False

	def update(self, time, events):
		if not self.parent.display_traps:
			return

		self.previous_rect = self.rect.copy()
		self.timer += time

		# if the flash period has been exceeded, generate a new flash period and change the cloud sprite
		if self.timer > self.flash_period:
			self.timer = 0
			self.generate_flash_period()

			gen = False
			while not gen:
				rand = random.randint(0, len(self.sprites) - 1)
				if not rand == self.current_image:
					self.current_image = rand
					gen = True
			self.image = self.sprites[self.current_image]

		self.parent.blit(self.image, self.rect)

	def generate_flash_period(self):
		self.flash_period = random.uniform(0.5, 1)

	def change_position(self):
		self.rect = self.sprites[0].get_rect(center=(random.randint(100, self.parent.rect.width - 100), random.randint(100, self.parent.rect.height - 100)))


class Robot(Entity, pygame.sprite.Sprite, IEventHandler):

	def __init__(self, parent, x=150, y=150):
		Entity.__init__(self)
		pygame.sprite.Sprite.__init__(self)
		IEventHandler.__init__(self)

		self.type = ""
		self.image = pygame.image.load("assets/img/plane.png")
		self.image_static = self.image.copy()
		self.rect = self.image.get_rect().copy()
		self.rect.x = 50
		self.rect.y = 50

		self.x = self.rect.x
		self.y = self.rect.y

		self.bearing = 0.0
		self.velocity = 200
		self.previous_velocity = self.velocity

		self.parent = parent

		self.previous_rect = self.rect.copy()

		self.collisioncount = 0
		self.score = 0

	def event_handler(self, event):
		
		if event.istype(LightChangeEvent) and event.status is 0:
			if not self.velocity == 0:
				self.previous_velocity = self.velocity
				self.velocity = 0
		if event.istype(LightChangeEvent) and event.status is 1:
			if not self.velocity == 0:
				self.previous_velocity = self.velocity
				self.velocity = 0
		if event.istype(LightChangeEvent) and event.status is 2:
			self.velocity = self.previous_velocity

	# encapsulation - bearing must be maintained between 0 and 360 degrees
	def set_bearing(self, value):
		if value > 360: value -= 360
		if value < 0: value += 360
		self.bearing = value

	# determines the bearing which the robot should take between two points (x, y)
	def determine_direction(self, start, end):
		self.target = end
		xg, yg = True, True
		if start[0] > end[0] and start[1] > end[1]:
			self.xg, self.yg = False, False
			self.bearing = 360.0 - degrees( math.atan( (float(abs(start[0] - end[0]))) / float(abs(start[1] - end[1])) ) )
			
		if start[0] < end[0] and start[1] > end[1]:
			self.xg, self.yg = True, False
			self.bearing = degrees( math.atan( (float(abs(start[0] - end[0]))) / float(abs(start[1] - end[1])) ) )
			
		if start[0] > end[0] and start[1] < end[1]:
			self.xg, self.yg = False, True
			self.bearing = 180.0 + degrees( math.atan( (float(abs(start[0] - end[0]))) / float(abs(start[1] - end[1])) ) )

		if start[0] < end[0] and start[1] < end[1]:
			self.xg, self.yg = True, True
			self.bearing = 180.0 - degrees( math.atan( (float(abs(start[0] - end[0]))) / float(abs(start[1] - end[1])) ) )

		if start[0] == end[0]:
			if start[1] > end[1]:
				self.xg, self.yg = True, False
				self.bearing = 0.0
			elif start[1] < end[1]:
				self.xg, self.yg = True, True
				self.bearing = 180.0

		if start[1] == end[1]:
			if start[0] > end[0]:
				self.xg, self.yg = False, True
				self.bearing = 270.0
			elif start[0] < end[0]:
				self.xg, self.yg = True, True
				self.bearing = 90.0

class RobotManual(Robot):

	def __init__(self, parent):
		Robot.__init__(self, parent)
		self.timer = 0.0
		self.angle_movement = -1

	def update(self, time, events):

		self.previous_rect = self.rect.copy()

		self.timer += time

		if self.timer > 2 and not self.velocity == 0:
			self.set_bearing(self.bearing + self.angle_movement)
			if self.timer > random.uniform(3.0, 4.0):
				self.timer = 2
				self.angle_movement *= -1

		# determine dx and dy from the current bearing
		bearing = bearing_conversion(self.bearing, self.velocity * time)
		self.x += bearing[2]
		self.y += bearing[3]

		self.rect.x = self.x
		self.rect.y = self.y

		self.image = pygame.transform.rotate(self.image_static, abs(360 - self.bearing))
		self.rect = self.image.get_rect(center=self.rect.center)

		# if the robot is out of the bounds of the map, change its bearing
		update = False
		if self.rect.right > self.parent.rect.width: self.rect.right = self.parent.rect.width; self.x = self.parent.rect.width - self.rect.width; update = True
		if self.rect.left < 0: self.rect.left = 0; self.x = 0; update = True
		if self.rect.top < 0: self.rect.top = 0; self.y = 0; update = True
		if self.rect.bottom > self.parent.rect.height: self.rect.bottom = self.parent.rect.height; self.y = self.parent.rect.height - self.rect.height; update = True

		if update:
			self.set_bearing(self.bearing + 45)

		self.parent.blit(self.image, self.rect)

class RobotAI(Robot):

	def __init__(self, parent):
		Robot.__init__(self, parent)
		self.type = "ai"
		self.rect.center = (394.0, 295.0)

		self.target = (0.0, 0.0)

		self.xg = True
		self.yg = True

		self.paththread = None
		self.threadqueue = Queue.Queue()
		self.pathnodes = []
		self.pathdone = True

		self.treasure = None

	def update(self, time, events):

		self.previous_rect = self.image.get_rect(x=self.rect.x, y=self.rect.y)
		
		# if no path exists, start to calculate a new path to a random treasure
		if len(self.pathnodes) == 0:
			if self.paththread == None or not self.paththread.is_alive():
				if len(self.parent.treasures) > 0 and self.pathdone:
					self.pathdone = False
					start_node = self.parent.nodegraph.find_closest_node(self.rect.center[0], self.rect.center[1])

					min_treasure = None
					min_distance = None
					for treasure in self.parent.treasures:
						distance = math.hypot(abs(start_node.xpos - treasure.rect.center[0]), abs(start_node.ypos - treasure.rect.center[1]))
						if min_treasure is None or distance < min_distance:
							min_treasure = treasure
							min_distance = distance

					if min_treasure is not None:
						self.paththread = threading.Thread(target=self.parent.astar.search_thread, args=(start_node, self.parent.nodegraph.find_closest_node(min_treasure.rect.center[0], min_treasure.rect.center[1]), self.rect, self.parent, self.threadqueue))
						self.paththread.start()
						self.treasure = treasure
		# check the queue to see if any of the paths have been found
		try:
			new_path = self.threadqueue.get_nowait()
			if not new_path == None:
				for item in new_path:
					self.pathnodes.append((item.xpos, item.ypos))
				self.determine_direction(self.rect.center, self.pathnodes.pop(0))
			else:
				self.pathdone = True
		except Queue.Empty:
			pass
		
		# determine dx and dy from the current bearing
		bearing = bearing_conversion(self.bearing, self.velocity * time)
		xb = self.x
		yb = self.y
		self.x += bearing[2]
		self.y += bearing[3]

		self.rect.x = self.x
		self.rect.y = self.y

		# check to see if the robot has exceeded its target position
		if ((self.rect.center[0] >= self.target[0]) == self.xg) and ((self.rect.center[1] >= self.target[1]) == self.yg):
			
			# roll back to the previous position to prevent jumping
			self.x = xb
			self.y = yb
			self.rect.x = self.x
			self.rect.y = self.y

			# if a path exists, determine the bearing to take from the current location
			# to the next node in the path array
			if not len(self.pathnodes) == 0:
				self.determine_direction(self.rect.center, self.pathnodes.pop(0))
				if len(self.pathnodes) == 0:
					self.pathdone = True
			# if the treasure no longer exists, empty the path and change the path status to complete
			# so that a new path is calculated
			if self.treasure not in self.parent.treasures:
				self.pathdone = True
				self.pathnodes = []
		# transform the original image according to the current bearing
		self.image = pygame.transform.rotate(self.image_static, abs(360 - self.bearing))
		self.parent.blit(self.image, self.rect)
