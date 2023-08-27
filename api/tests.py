import unittest
import requests


'''
the objects in database before testing are in database/testing_objects
'''


class TestAPI(unittest.TestCase):
	def test_helloWorld(self):
		url = 'http://127.0.0.1:8000/'
		response = requests.get(url)
		self.assertEqual(response.status_code, 200)

	def test_whoAmI(self):
		url = 'http://127.0.0.1:8000/who-am-i'
		headers = {"Authorization": "Token 69d7f16f0783564d84321c4eb1b205c8013852df"}
		response = requests.get(url, headers=headers)
		self.assertEqual(response.status_code, 200)

	def test_scenario(self):
		# First, Alice will create a loan request
		print('First')
		url = 'http://127.0.0.1:8000/create-loan'
		alice_headers = {"Authorization": "Token 74801e014c99da0e93fd71038e200c6a454d2a1d"}
		data = {'amount': 5000, 'period': 6, 'borrower_id': 14}
		response = requests.post(url, json=data, headers=alice_headers)
		loan_id = response.json()['id']
		self.assertEqual(response.status_code, 200)

		# Second, Bob will try to send an offer, but he cannot afford actually
		print('Second')
		url = f'http://127.0.0.1:8000/loans/{loan_id}/make-offer'
		bob_headers = {"Authorization": "Token 69d7f16f0783564d84321c4eb1b205c8013852df"}
		data = {'investor_id': 15, 'annual_interest': 0.15}
		response = requests.post(url, json=data, headers=bob_headers)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(response.text, "Credit is lower than expected.")

		# Third, Carol sends an offer
		print('Third')
		carol_headers = {"Authorization": "Token b678f09aefbce591d65da1cb98de1878ed5e3216"}
		data = {'investor_id': 16, 'annual_interest': 0.15}
		response = requests.post(url, json=data, headers=carol_headers)
		offer = response.json()
		offer_id = offer['id']
		self.assertEqual(response.status_code, 200)
		self.assertEqual(offer['total-interest'], 375)
		self.assertEqual(offer['total-deserved'], 5375)

		# Fourth, Alice accepts offer
		print('Fourth')
		url = f'http://127.0.0.1:8000/offers/{offer_id}/accept'
		data = {'borrower_id': 14}
		response = requests.patch(url, json=data, headers=alice_headers)
		self.assertEqual(response.status_code, 200)

		# Fifth checking Alice and Carol credits
		print('Fifth')
		alice_url = 'http://127.0.0.1:8000/borrowers/14'
		carol_url = 'http://127.0.0.1:8000/investors/16'
		alice = requests.get(alice_url).json()
		carol = requests.get(carol_url).json()
		self.assertEqual(alice['credit'], 6000)	# she was 1000 (+5000)
		self.assertEqual(carol['credit'], 997)	# she was 6000 (-5003)

		# A scheduler should call the method loan.attampt_complete() in database/models.Loan
		# to find if it's the time for the borrower to pay the deserved money to the investor.
