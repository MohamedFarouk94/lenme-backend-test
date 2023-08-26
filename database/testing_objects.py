from database.models import Investor, Borrower
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def add_user(first_name=None, last_name=None, username=None, email=None, password=None, credit=0, cls='Investor'):
	user = User.objects.create_user(username=username,
			first_name=first_name,
			last_name=last_name,
			email=email,
			password=password)

	if cls == 'Borrower':
		person = Borrower.objects.create(user=user, credit=credit)
	else:
		person = Investor.objects.create(user=user, credit=credit)

	token = Token.objects.create(user=user)

	return person, token.key


def add_users():
	alice, alice_key = add_user(first_name='Alice', last_name='Attal', username='alice', email='alice@gmail.com', password='123456', credit=1000, cls='Borrower')
	bob, bob_key = add_user(first_name='Bob', last_name='Bradley', username='bob', email='bob@gmail.com', password='123456', credit=3000)
	carol, carol_key = add_user(first_name='Carol', last_name='Cena', username='carol', email='carol@gmail.com', password='123456', credit=6000)
	dave, dave_key = add_user(first_name='Dave', last_name='Draper', username='dave', email='dave@gmail.com', password='123456', credit=8000)
	eve, eve_key = add_user(first_name='Eve', last_name='Echo', username='eve', email='eve@gmail.com', password='123456', credit=10000)

	return [alice, bob, carol, dave, eve], [alice_key, bob_key, carol_key, dave_key, eve_key]


'''
tokens:
{'alice': '74801e014c99da0e93fd71038e200c6a454d2a1d',
 'bob': '69d7f16f0783564d84321c4eb1b205c8013852df',
 'carol': 'b678f09aefbce591d65da1cb98de1878ed5e3216',
 'dave': 'b21b3f49d8a0479667123d5edc499c416979e152',
 'eve': '881159bd473a5dabf688f1dff83f49949de2bf78'}

'''


def delete_users():
	for user in User.objects.all():
		user.delete()
