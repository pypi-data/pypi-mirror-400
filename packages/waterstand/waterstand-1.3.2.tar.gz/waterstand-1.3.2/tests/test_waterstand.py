""" testen voor de package waterstand """
import json
import unittest
from unittest.mock import patch, MagicMock, ANY

from requests.exceptions import HTTPError, Timeout, RequestException

import waterstand


def create_mock_response(filenaam, httpstatus=200):
  """ maak een response van de testdata """
  with open(filenaam, 'r', encoding='utf-8') as fid:
    testdata = json.loads(fid.read().encode('utf-8'))

  print(testdata)

  mock_response = MagicMock()
  mock_response.status_code = httpstatus
  mock_response.json.return_value = testdata
  mock_response.__enter__.return_value = mock_response
  return mock_response


class TestWaterstand(unittest.TestCase):
  """ Class voor het testen van de package waterstand """

  @patch('requests.get')
  def test_haalwaterstand(self, mock_requestsget):
    """ test van de normale flow """
    mock_requestsget.return_value = create_mock_response('tests/testdata.json')

    response = waterstand.haalwaterstand('Katerveer', 'KATV')
    verwacht = {'resultaat': 'OK', 'tijd': '23-11 16:50', 'nu': 84.0, 'morgen': 89.0}

    self.assertEqual(response, verwacht)

  @patch('requests.get')
  def test_haalwaterstand_timeformat(self, mock_requestsget):
    """ test 2 van de normale flow """
    mock_requestsget.return_value = create_mock_response('tests/testdata2.json')

    response = waterstand.haalwaterstand('Katerveer', 'KATV')
    verwacht = {'resultaat': 'OK', 'tijd': '23-11 16:50', 'nu': -999, 'morgen': 89.0}

    self.assertEqual(response, verwacht)

  @patch('requests.get', side_effect=HTTPError('', 0, '', None, None))
  @patch('waterstand.sleep', return_value=None)
  def test_haalwaterstand_httperror(self, mock_sleep, mock_requestsget):
    """ test van een HTTP-fout bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_requestsget.call_count == 3
    assert mock_sleep.call_count == 2

  @patch('requests.get', side_effect=TimeoutError)
  @patch('waterstand.sleep', return_value=None)
  def test_haalwaterstand_timeouterror(self, mock_sleep, mock_requestsget):
    """ test van een time-out bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_requestsget.call_count == 3
    assert mock_sleep.call_count == 2

  @patch('requests.get', side_effect=ConnectionError)
  @patch('waterstand.sleep', return_value=None)
  def test_haalwaterstand_connectionerror(self, mock_sleep, mock_requestsget):
    """ Test van een connection error bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_requestsget.call_count == 3
    assert mock_sleep.call_count == 2

  @patch('requests.get', side_effect=Timeout())
  @patch('waterstand.sleep', return_value=None)
  def test_haalwaterstand_timeout(self, mock_sleep, mock_requestsget):
    """ Test van een Time-out bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_requestsget.call_count == 3
    assert mock_sleep.call_count == 2

  @patch('requests.get', side_effect=RequestException())
  @patch('waterstand.sleep', return_value=None)
  def test_haalwaterstand_requestexception(self, mock_sleep, mock_requestsget):
    """ Test van een algemene exceptie bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_requestsget.call_count == 3
    assert mock_sleep.call_count == 2

  @patch('requests.get', side_effect=[RequestException(),
                                      create_mock_response('tests/testdata.json'),
                                      ])
  @patch('waterstand.sleep', return_value=None)
  def test_haalwaterstand_requestexception_eenmalig(self, mock_sleep, mock_requestsget):
    """ Test van een algemene exceptie bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'OK', 'tijd': '23-11 16:50', 'nu': 84.0, 'morgen': 89.0}
    self.assertEqual(response, expected)
    assert mock_requestsget.call_count == 2
    assert mock_sleep.call_count == 1

  @patch('requests.get')
  def test_haalwaterstand_geen200(self, mock_requestsget):
    """ geen status 200 bij ophalen data """
    mock_requestsget.return_value = create_mock_response('tests/testdata.json', 400)

    response = waterstand.haalwaterstand('Katerveer', 'KATV')
    verwacht = {'resultaat': 'NOK', 'error': ANY}

    self.assertEqual(response, verwacht)

  @patch('requests.get')
  def test_haalwaterstand_geendata(self, mock_requestsget):
    """ geen data als output """
    mock_requestsget.return_value = create_mock_response('tests/testdata3.json')

    response = waterstand.haalwaterstand('Katerveer', 'KATV')
    verwacht = {'resultaat': 'NOK', 'error': ANY}

    self.assertEqual(response, verwacht)
