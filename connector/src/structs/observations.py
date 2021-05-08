import rest.util as util

class Observations:
	
	def __init__(self,stationId):
		self.data = {}
		self.items = {}
		self.stationId = stationId

		self.update()

	def update(self):
		self.data = util.get('observations/station/%d' % self.stationId )

		for i in self.data['obs'][0]:
			self.items[i] = self.data['obs'][0][i]
		print self.items
