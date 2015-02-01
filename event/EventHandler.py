from abc import ABCMeta, abstractmethod

class EventDispatcher(object):

	_instance = None

	def __new__(cls, *args, **kwargs):
		# singleton design... If an instance exists, use that
		if not cls._instance:
			cls._instance = super(EventDispatcher, cls).__new__(cls, *args, **kwargs)
			cls._instance.device_list = []
		return cls._instance

	def register_handler(self, device):
		# Regsiter a new event handler
		self.device_list.append(device)

	def send_event(self, event):
		# Loop through all of the handlers and dispatch the event
		for device in self.device_list:
			device.event_handler(event)


class IEventHandler(object):

	__metaclass__ = ABCMeta

	@abstractmethod
	def event_handler(self, event):
		# abstract method to be implemented in all derived classes
		pass

	def __init__(self):
		# create the next handler and register the new handler
		EventDispatcher().register_handler(self)

	def send_event(self, event):
		# send event to dispatcher
		EventDispatcher().send_event(event)