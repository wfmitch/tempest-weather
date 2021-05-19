import rest.util as util
import psycopg2

class Stations:
	
	def __init__(self):
		self.data = {}
		self.items = {}
		self.stationId = None
		self.deviceId = None
		self.update()

	def update(self):
		self.data = util.get('stations')['stations'][0]

		for i in self.data['station_items']:
			self.items[i['item']] = i
			self.stationId = i['station_id']
			self.deviceId = i['device_id']
