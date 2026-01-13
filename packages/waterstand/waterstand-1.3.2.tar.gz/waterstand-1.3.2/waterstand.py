"""
Ophalen van de waterstand. Gegevens komen van https://waterinfo.rws.nl/ en de gegevens voor vandaag
en morgen worden er uit gehaald.
"""
from datetime import datetime, timedelta
from time import sleep

import requests
from requests import Response


def leesjson(url: str) -> dict:
  """
  Haal JSON van de URL op
  :param url: URL waar de JSON opgehaald moet worden
  :type url: str
  :return: JSON
  :rtype: dict
  """
  maxpogingen: int = 3
  for poging in range(maxpogingen):
    try:
      headers: dict[str, str] = {'Accept': 'application/json'}
      resp: Response = requests.get(url,
                                    headers=headers,
                                    verify=False,
                                    timeout=10,
                                    allow_redirects=False)
      if resp.status_code == 200:
        contentjson: dict = resp.json()
        contentjson['resultaat'] = 'OK'
        return contentjson
      return {'resultaat': 'NOK',
              'error': f'Statuscode {resp.status_code} van RWS'}
    except (ConnectionError,
            TimeoutError,
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException) as error:
      if poging < maxpogingen - 1:
        print(f'Error: Data ophalen mislukt vanwege {error}\nURL: {url}, pogingen: {poging}')
        sleep((poging + 1) * 10)
  return {'resultaat': 'NOK',
          'error': 'Error: Data ophalen mislukt vanwege teveel pogingen'}


def leeswaterstandjson(naam: str, afkorting: str) -> dict:
  """
  Lees de informatie van bepaalde locatie van de API van RWS.
  :param naam: Naam van de locatie
  :type naam: str
  :param afkorting: Afkorting van de locatie
  :type afkorting: str
  :return: JSON met de waardes van de waterstanden
  :rtype: dict
  """
  url: str = 'https://waterinfo.rws.nl/api/chart/get' + \
             f'?mapType=waterhoogte&locationCodes={naam}({afkorting})&values=-48,48'
  return leesjson(url)


def bepaalstanden(waterstandjson: dict) -> dict:
  """
  Haal de noodzakelijke gegevens van de waterstand uit de gegevens van RWS.
  :param waterstandjson: Dict met de gegevens van de waterstanden
  :type waterstandjson: dict
  :return: JSON met de waardes van de waterstanden
  :rtype: dict
  """
  if waterstandjson['resultaat'] == 'NOK':
    return waterstandjson
  try:
    laatstetijdgemeten: str = waterstandjson['t0']
    voorspeldestanden: list = []
    gemetenstanden: list = []
    for serie in waterstandjson['series']:
      if serie['isPrediction']:
        voorspeldestanden = serie['data']
      else:
        gemetenstanden = serie['data']

    hoogtenu: int = -999
    stand: dict
    for stand in gemetenstanden:
      if stand['dateTime'] == laatstetijdgemeten:
        hoogtenu = stand['value']

    if laatstetijdgemeten.endswith(':00Z'):
      tijdpatroon: str = '%Y-%m-%dT%H:%M:%SZ'
    elif '+' in laatstetijdgemeten:
      tijdpatroon = '%Y-%m-%dT%H:%M:%S+02:00'
    else:
      laatstetijdgemeten = f'{laatstetijdgemeten[:12]}:00:00Z'
      tijdpatroon = '%Y-%m-%dT%H:%M:%SZ'


    laatstetijdobj: datetime = datetime.strptime(laatstetijdgemeten, tijdpatroon) \
                               + timedelta(hours=1)
    weergavetijd: str = laatstetijdobj.strftime('%d-%m %H:%M')
    morgenobj: datetime = laatstetijdobj + timedelta(days=1)
    morgentekst: str = morgenobj.strftime(tijdpatroon)

    hoogtemorgen: int = hoogtenu
    for stand in voorspeldestanden:
      if stand['dateTime'] == morgentekst:
        hoogtemorgen = stand['value']
    returnjson = {'resultaat': 'OK',
                  'tijd': weergavetijd,
                  'nu': hoogtenu,
                  'morgen': hoogtemorgen}
    return returnjson
  except(KeyError, TypeError) as error:
    return {'resultaat': 'NOK', 'error': error}


def haalwaterstand(naam: str, afkorting: str) -> dict:
  """
  Haal de waterstand van een locatie bij RWS en haal de noodzakelijke waarden daar uit.
  :param naam: Naam van de locatie
  :type naam: str
  :param afkorting: Afkorting van de locatie
  :type afkorting: str
  :return: JSON met de waardes van de waterstanden
  :rtype: dict
  """
  contentjson: dict = leeswaterstandjson(naam, afkorting)
  return bepaalstanden(contentjson)
