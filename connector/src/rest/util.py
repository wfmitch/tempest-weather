import requests
import log as log

restUrl = 'https://swd.weatherflow.com/swd/rest/'
authKey = '17b72aa4-2a8c-49ce-b720-f0412266e86a'

headers = {
  'Authorization': 'Bearer %s' % authKey
}


def get(endpoint, payload = {}):
	try:
		response = requests.request("GET", restUrl+str(endpoint), headers=headers, data=payload)
		if response.json()['status']['status_code'] == 0:
			return response.json()
		else:
			log.error("Unable to connect to /%s" % str(endpoint))

	except Exception as e:
		log.error(e)

	return None

