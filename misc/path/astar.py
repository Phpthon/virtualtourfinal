import pygame
from itertools import product
import math, random

class NodeGraph(object):

	def __init__(self, parent):
		self.nodes = None
		self.graph = None
		self.parent = parent
		self.init_map()

	def init_map(self, width=31, height=41):
		nodes = [[AStarGridNode(x, y) for y in range(height)] for x in range(width)]
		graph = {}
		for x, y in product(range(width), range(height)):
			node = nodes[x][y]
			graph[node] = []
			# loop for each adjacent node to the current node
			for i, j in product([-1, 0, 1], [-1, 0, 1]):
				# if the adjacent node is out of range, ignore it
				if not (0 <= x + i < width): continue
				if not (0 <= y + j < height): continue

				# add the adjacent node to the dictionary associating it to the index of the parent
				# (current) node
				graph[nodes[x][y]].append(nodes[x+i][y+j])
				nodes[x+i][y+j].xpos = ((x+i)*20)
				nodes[x+i][y+j].ypos = ((y+j)*20)
		self.nodes = nodes
		self.graph = graph

	def find_closest_node(self, x, y, spacing=20):
		# find the closest node to the supplied coordinates
		node = self.nodes[int(spacing * math.ceil(float(x)/spacing)/20)][int(spacing * math.ceil(float(y)/spacing)/20)]
		# get from the graph dictionary the adjacent nodes to the closest node found
		node_array = self.graph[node]

		mx, my = 1000, 1000
		selected_node = None
		# find the closest node to the supplied coordinates based on the adjacent nodes
		# of the 'closest' node to the supplied coordinates and return it
		for node in node_array:
			if abs(x - node.xpos) < mx or abs(y - node.ypos) < my:
				selected_node = node
				mx, my = abs(x - node.xpos), abs(y - node.ypos)

		return selected_node

class AStar(object):

	def __init__(self, graph):
		self.graph = graph
		self.obstacles = []
		self.object_rect = None

	def remove_obstacle(self, obstacle):
		self.obstacles.remove(obstacle)

	def add_obstacle(self, obstacle):
		if isinstance(obstacle, pygame.Rect):
			self.obstacles.append(obstacle)
		elif isinstance(obstacle, pygame.sprite.Sprite):
			self.obstacles.append(obstacle.rect)

	def check_collision(self, node, world):
		rect = self.object_rect.copy()
		rect.center = (node.xpos, node.ypos)
		for obstacle in world.obstacles:
			if rect.colliderect(obstacle):
				return True
		return False

	def heuristic(self, node, end):
		return abs(end.x - node.x) + abs(end.y - node.y)

	def search_thread(self, start, end, object_rect, world, q):
		q.put(self.search(start, end, object_rect, world))

	def search(self, start, end, object_rect, world):
		self.object_rect = object_rect
		openset = set()
		closedset = set()
		current = start
		openset.add(current)
		while openset:
			# find the smallest f value from the list
			current = min(openset, key=lambda o:o.g + o.h)
			# if the current node is the end node
			if current == end:
				# create an array of path nodes and back-trace appending nodes
				path = []
				while current is not start:
					path.append(current)
					current = current.parent
				path.append(current)
				#return path
				# reverse the array elements
				return path[::-1]
			openset.remove(current)
			closedset.add(current)
			for node in self.graph[current]:
				# if the node is in the closed set or the node is an obstacle
				# then don't process the current node
				# collision checker if statement
				#if node in closedset or self.check_collision(node, world):
				if node in closedset:
					continue
				# if the node exists in the openset
				if node in openset:
					# calculate its new movement cost from the current node
					new_g = current.g + current.move_cost(node)
					# if the current node movement cost is greater than the new move cost
					# set the new move cost for the node and set its parent as the current node
					if node.g > new_g:
						node.g = new_g
						node.parent = current
				else:
					# node does not exist in the openset so calculate the relevant information
					# and make it exist in the openset
					node.g = current.g + current.move_cost(node)
					node.h = self.heuristic(node, end)
					node.parent = current
					openset.add(node)
		# no path found, return null
		return None

class AStarGridNode(object):

	def __init__(self, x, y):

		self.g = 0
		self.h = 0
		self.parent = None
		self.x, self.y = x, y
		self.xpos, self.ypos = 0, 0

	def move_cost(self, other):
		# return the movement cost of the current node relative to another node
		# (diagonal being 14 and non-diagonal being 10)
		diagonal = abs(self.x - other.x) == 1 and abs(self.y - other.y) == 1
		return 14 if diagonal else 10