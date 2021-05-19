import requests
import log as log

restUrl = 'https://swd.weatherflow.com/swd/rest/'
headers = {}
auth = False

def authorize():
	global headers, auth
	f = open("/proj/auth.key", "r")
	authKey = f.read().strip()

	headers = {
  	'Authorization': 'Bearer %s' % authKey
	}
	auth = True

def get(endpoint, payload = {}):
	if not auth:
		authorize()

	try:
		response = requests.request("GET", restUrl+str(endpoint), headers=headers, data=payload)
		if response.json()['status']['status_code'] == 0:
			return response.json()
		else:
			log.error("Unable to connect to /%s" % str(endpoint))

	except Exception as e:
		log.error(e)

	return None

