from django.db import models


# Create your models here.
class Investor(models.Model):
	plural = 'investors'
	id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=20)
	second_name = models.CharField(max_length=20)
	user_name = models.CharField(max_length=50, unique=True)
	email = models.EmailField(max_length=256, unique=True)
	birth_date = models.DateField(null=True)
	address = models.CharField(max_length=256, blank=True)
	credit = models.FloatField(default=0)
	account_created = models.DateTimeField(auto_now_add=True)
	# api_key_hashed = models.CharField(max_length=15, unique=True)

	def save(self, *awargs, **kwargs):
		super(Investor, self).save(*awargs, **kwargs)

	def to_dict(self):
		return {
			'id': self.id,
			'First Name': self.first_name,
			'Second Name': self.second_name,
			'user_name': self.user_name,
			'email': self.email,
			'account_created': self.account_created,
			'credit': self.credit,
		}


class Borrower(models.Model):
	plural = 'borrowers'
	id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length=20)
	second_name = models.CharField(max_length=20)
	user_name = models.CharField(max_length=50, unique=True)
	email = models.EmailField(max_length=256, unique=True)
	birth_date = models.DateField(null=True)
	address = models.CharField(max_length=256, blank=True)
	credit = models.FloatField(default=0)
	account_created = models.DateTimeField(auto_now_add=True)
	# api_key_hashed = models.CharField(max_length=15, unique=True)

	def save(self, *awargs, **kwargs):
		super(Borrower, self).save(*awargs, **kwargs)

	def to_dict(self):
		return {
			'id': self.id,
			'First Name': self.first_name,
			'Second Name': self.second_name,
			'user_name': self.user_name,
			'email': self.email,
			'account_created': self.account_created,
			'credit': self.credit,
		}


class Loan(models.Model):
	plural = 'loans'
	id = models.AutoField(primary_key=True)
	amount = models.FloatField()
	period = models.DurationField()
	fee = models.FloatField(default=3.0)
	borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
	investor = models.ForeignKey(Investor, null=True, on_delete=models.SET_NULL)
	annual_interest = models.FloatField(null=True)
	loan_created = models.DateTimeField(auto_now_add=True)
	loan_funded = models.DateTimeField(null=True)
	status = models.CharField(max_length=10, choices=[("Pending", "Pending"), ("Funded", "Funded"), ("Completed", "Completed"), ("Problem", "Problem")], default='Pending')

	def save(self, *awargs, **kwargs):
		super(Loan, self).save(*awargs, **kwargs)

	def to_dict(self):
		return {
			'id': self.id,
			'amount': self.amount,
			'period': self.period,
			'fee': self.fee,
			'borrower': self.borrower.id,
			'investor': self.investor.id if self.investor else 'N/A',
			'annual interest': self.annual_interest if self.annual_interest else 'N/A',
			'loan created': self.loan_created,
			'loan_funded': self.loan_funded if self.loan_funded else 'N/A',
			'status': self.status
		}


class Offer(models.Model):
	plural = 'offers'
	id = models.AutoField(primary_key=True)
	investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
	loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
	annual_interest = models.FloatField()
	status = models.CharField(max_length=10, choices=[("Pending", "Pending"), ("Declined", "Declined"), ("Accepted", "Accepted")], default='Pending')
	offer_created = models.DateTimeField(auto_now_add=True)
	offer_concluded = models.DateTimeField(null=True)

	def save(self, *awargs, **kwargs):
		super(Offer, self).save(*awargs, **kwargs)

	def to_dict(self):
		return {
			'id': self.id,
			'investor': self.investor.id,
			'loan': self.loan.id,
			'annual interest': self.annual_interest,
			'offer_created': self.offer_created,
			'offer_concluded': self.offer_concluded if self.offer_concluded else 'N/A',
			'status': self.status
		}
