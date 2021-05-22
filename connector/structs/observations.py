import rest.util as util
import psycopg2
import time
import datetime
from time import gmtime,strftime
from dateutil import tz

class Observations:
	
	include = ["timestamp",
        "air_temperature",
        "barometric_pressure",
        "station_pressure",
        "pressure_trend",
        "sea_level_pressure",
        "relative_humidity",
        "precip",
        "precip_minutes_local_day",
        "wind_avg",
        "wind_direction",
        "wind_gust",
        "solar_radiation",
        "uv",
        "brightness",
        "lightning_strike_count",
        "feels_like",
        "heat_index",
        "wind_chill",
        "dew_point",
        "air_density"]

	def __init__(self,stationId):
		self.data = {}
		self.items = {}
		self.stationId = stationId

		self.update()

	def update(self):
		self.data = util.get('observations/station/%d' % self.stationId )

		for i in self.data['obs'][0]:
			self.items[i] = self.data['obs'][0][i]

	def toF(self,cel):
		return (cel * 1.8) + 32


	def dailyBackfill(self, deviceId, Full = False):

		print "Rebuilding entire database"
		i = 0
		conn = psycopg2.connect("dbname='weather' user='postgres' host='127.0.0.1' password='postgres'")
		cur = conn.cursor()

		cur.execute("""SELECT * FROM data.statistics ORDER BY timestamp DESC""")
		records = cur.fetchall()
		
		from_zone = tz.gettz('UTC')
		to_zone = tz.gettz('America/Chicago')

		today = datetime.datetime.utcnow()


		high = -999.0
		low = 999.0 
		rain = 0.0
		day = -1

		last = None
		if not Full:
			cur.execute("""SELECT * FROM data.calculations ORDER BY timestamp DESC LIMIT 1""")
			record = cur.fetchall()
			lastTime = record[0][-1]

			last = datetime.datetime.fromtimestamp(lastTime)
			u = last.replace(tzinfo=from_zone)
			last = u.astimezone(to_zone)


		for record in records:
			date = datetime.datetime.fromtimestamp(record[-2])
			utc = date.replace(tzinfo=from_zone)
			date = utc.astimezone(to_zone)

			if date.date() != today.date():
				if date.day != day:
					day = date.day
					high = -999
					low = 999 
					rain = 0.0

				if record[0] > high:
					high = record[0]

				if record[0] < low:
					low = record[0]

				if record[5] > rain:
					rain = record[5]

				if not Full:
					if date <= last:
						print date
						print last
						break 

				if date.hour == 0 and date.minute == 0:
					try:
						cur.execute("""INSERT INTO data."calculations"("timestamp","high","low","rain") VALUES (%s,%s,%s,%s);""", \
						(record[-2], high,
						low,
						rain
						))
						conn.commit()
					except Exception as e:
						pass

		print "Finished installation, run ./start"



	def backFill(self, deviceId):

		conn = psycopg2.connect("dbname='weather' user='postgres' host='127.0.0.1' password='postgres'")
		cur = conn.cursor()

		cur.execute("""SELECT * FROM data.statistics ORDER BY timestamp DESC LIMIT 1""")
		record = cur.fetchall()
		lastTime = record[0][-2]

		if time.time()-60 > lastTime:
			daysSince = int(((time.time() - lastTime) / 60 / 60 / 24)) + 1
			print "Rebuild last %d days" % daysSince
			for i in range(daysSince):
				self.data = util.get('observations/device/%d/?day_offset=%d' % (deviceId,i))
				for item in self.data['obs']:
					if int(item[0]) > lastTime:
						try:
							cur.execute("""INSERT INTO data."statistics"("timestamp","air_temperature","barometric_pressure","station_pressure","sea_level_pressure","relative_humidity","precip","precip_minutes_local_day","wind_avg","wind_direction","wind_gust","solar_radiation","uv","brightness","lightning_strike_count","feels_like","heat_index","wind_chill","dew_point","air_density") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", \
							(float(item[0]),	float(self.toF(item[7])),
							float(item[6]),
							float(item[6]),	
							float(0),	
							int(item[8]),	
							float(item[18]),	
							int(item[17]),	
							float(item[2]),	
							float(item[4]),	
							float(item[3]),	
							int(item[11]),	
							float(item[10]),	
							int(item[9]),	
							int(item[15]),	
							float(self.toF(item[7])),	
							float(self.toF(item[7])),	
							float(self.toF(item[7])),	
							float(0),	
							float(0)))
							conn.commit()
						except:
							pass

	def backFillAll(self, deviceId):
		print "Rebuilding entire database"
		i = 0
		conn = psycopg2.connect("dbname='weather' user='postgres' host='127.0.0.1' password='postgres'")
		cur = conn.cursor()

		while True:
			self.data = util.get('observations/device/%d/?day_offset=%d' % (deviceId,i))

			if self.data['obs'] == None:
				break
			else:
				for item in self.data['obs']:
					try:
						cur.execute("""INSERT INTO data."statistics"("timestamp","air_temperature","barometric_pressure","station_pressure","sea_level_pressure","relative_humidity","precip","precip_minutes_local_day","wind_avg","wind_direction","wind_gust","solar_radiation","uv","brightness","lightning_strike_count","feels_like","heat_index","wind_chill","dew_point","air_density") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", \
						(float(item[0]),	float(self.toF(item[7])),
						float(item[6]),
						float(item[6]),	
						float(0),	
						int(item[8]),	
						float(item[18]),	
						int(item[17]),	
						float(item[2]),	
						float(item[4]),	
						float(item[3]),	
						int(item[11]),	
						float(item[10]),	
						int(item[9]),	
						int(item[15]),	
						float(self.toF(item[7])),	
						float(self.toF(item[7])),	
						float(self.toF(item[7])),	
						float(0),	
						float(0)))
						conn.commit()
					except Exception as e:
						pass
				i += 1
				



	def uploadCurrent(self):


		conn = psycopg2.connect("dbname='weather' user='postgres' host='127.0.0.1' password='postgres'")
		cur = conn.cursor()
		cur.execute("""INSERT INTO data."statistics"("timestamp","air_temperature","barometric_pressure","station_pressure","sea_level_pressure","relative_humidity","precip","precip_minutes_local_day","wind_avg","wind_direction","wind_gust","solar_radiation","uv","brightness","lightning_strike_count","feels_like","heat_index","wind_chill","dew_point","air_density") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", \
		(float(self.items['timestamp']),	float(self.toF(self.items['air_temperature'])),
		float(self.items['barometric_pressure']),
		float(self.items['station_pressure']),	
		float(self.items['sea_level_pressure']),	
		int(self.items['relative_humidity']),	
		float(self.items['precip_accum_local_day']),	
		int(self.items['precip_minutes_local_day']),	
		float(self.items['wind_avg']),	
		float(self.items['wind_direction']),	
		float(self.items['wind_gust']),	
		int(self.items['solar_radiation']),	
		float(self.items['uv']),	
		int(self.items['brightness']),	
		int(self.items['lightning_strike_count']),	
		float(self.toF(self.items['feels_like'])),	
		float(self.toF(self.items['heat_index'])),	
		float(self.toF(self.items['wind_chill'])),	
		float(self.toF(self.items['dew_point'])),	
		float(self.items['air_density'])))
		conn.commit()
