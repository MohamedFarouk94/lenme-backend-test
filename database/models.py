from django.db import models
from django.contrib.auth.models import User
from database.financial_operations import calculate_financial_data, do_transiction
from datetime import datetime


# Create your models here.
class Person(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	credit = models.FloatField(default=0)

	def can_afford(self, amount):
		return self.credit >= amount

	def update_credit(self, amount):
		self.credit += amount
		self.save()

	def to_dict(self):
		return {
			'id': self.user.id,
			'first-name': self.user.first_name,
			'last-name': self.user.last_name,
			'username': self.user.username,
			'email': self.user.email,
			'date-joined': self.user.date_joined,
			'credit': self.credit,
		}


class Investor(Person):
	plural = 'investors'


class Borrower(Person):
	plural = 'borrowers'


class Loan(models.Model):
	plural = 'loans'
	id = models.AutoField(primary_key=True)
	amount = models.FloatField()
	period = models.DurationField()
	fee = models.FloatField(default=3.0)
	borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
	investor = models.ForeignKey(Investor, null=True, on_delete=models.SET_NULL)
	annual_interest = models.FloatField(null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	date_funded = models.DateTimeField(null=True)
	status = models.CharField(max_length=10, choices=[("Pending", "Pending"), ("Funded", "Funded"), ("Completed", "Completed"), ("Problem", "Problem")], default='Pending')

	def get_offers(self):
		return [offer.to_dict() for offer in Offer.objects.filter(loan=self)]

	def funded(self, investor, annual_interest):
		self.status = 'Funded'
		self.investor = investor
		self.annual_interest = annual_interest
		do_transiction(self.amount, giver=self.investor, reciever=self.borrower)
		do_transiction(self.fee, giver=self.investor)
		self.investor.save()
		self.borrower.save()
		self.save()

	# Check if it's the time to repay
	def attempt_complete(self):
		if self.date_funded + self.period < datetime.now() or self.status != 'Funded':
			return 0

		total_deserved = self.to_dict()['total-deserved']
		if not self.borrower.can_afford(total_deserved):
			self.status = 'Problem'
			return -1

		self.status = 'Complete'
		do_transiction(total_deserved, giver=self.borrower, reciever=self.investor)
		return 1

	def calculate_financial_data(self):
		if self.status == 'Funded':
			return calculate_financial_data(self.amount, self.annual_interest, self.period)
		return None, None

	def to_dict(self):
		interest, deserved = self.calculate_financial_data()
		return {
			'id': self.id,
			'amount': self.amount,
			'period': self.period.days,
			'fee': self.fee,
			'borrower': self.borrower.user.id,
			'borrower-username': self.borrower.user.username,
			'investor': self.investor.user.id if self.investor else 'N/A',
			'investor-username': self.investor.user.username if self.investor else 'N/A',
			'annual-interest': self.annual_interest if self.annual_interest else 'N/A',
			'date-created': self.date_created,
			'date-funded': self.date_funded if self.date_funded else 'N/A',
			'offers-ids': [offer['id'] for offer in self.get_offers()],
			'total-interest': interest if interest else 'N/A',
			'total-deserved': deserved if deserved else 'N/A',
			'status': self.status,
		}


class Offer(models.Model):
	plural = 'offers'
	id = models.AutoField(primary_key=True)
	investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
	loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
	annual_interest = models.FloatField()
	status = models.CharField(max_length=10, choices=[("Pending", "Pending"), ("Declined", "Declined"), ("Accepted", "Accepted")], default='Pending')
	date_created = models.DateTimeField(auto_now_add=True)
	date_concluded = models.DateTimeField(null=True)

	def calculate_financial_data(self):
		interest, deserved = calculate_financial_data(self.loan.amount, self.annual_interest, self.loan.period)
		return interest, deserved

	def accept(self):
		self.status = 'Accepted'
		NOW = datetime.now()
		self.date_concluded = NOW
		self.loan.date_funded = NOW
		self.loan.save()
		self.save()
		print('#ACCEPTED#')

	def dcline(self):
		self.status = 'Declined'
		self.date_concluded = datetime.now()
		self.save()

	def to_dict(self):
		interest, deserved = self.calculate_financial_data()
		return {
			'id': self.id,
			'investor': self.investor.user.id,
			'investor-username': self.investor.user.username,
			'borrower': self.loan.borrower.user.id,
			'borrower-username': self.loan.borrower.user.username,
			'loan': self.loan.id,
			'amount': self.loan.amount,
			'period': self.loan.period.days,
			'annual-interest': self.annual_interest,
			'date-created': self.date_created,
			'date-concluded': self.date_concluded if self.date_concluded else 'N/A',
			'total-interest': interest,
			'total-deserved': deserved,
			'status': self.status
		}
