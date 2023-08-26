def calculate_annual_interest(amount, annual_interest_rate):
	return amount * annual_interest_rate


def calculate_actual_interest(annual_interest_amount, period):
	return annual_interest_amount * period.days / 360


def calculate_interest(amount, annual_interest_rate, period):
	annual_interest_amount = calculate_annual_interest(amount, annual_interest_rate)
	return calculate_actual_interest(annual_interest_amount, period)


def calculate_deserved_amount(amount, annual_interest_rate, period):
	return amount + calculate_interest(amount, annual_interest_rate, period)


def calculate_financial_data(amount, annual_interest_rate, period):
	interest = calculate_interest(amount, annual_interest_rate, period)
	deserved = calculate_deserved_amount(amount, annual_interest_rate, period)
	return interest, deserved


def check_if_can_afford(amount, giver):
	return giver.can_afford(amount)


def do_transiction(amount, giver=None, reciever=None):
	n_transictions = 0
	if giver:
		giver.update_credit(-amount)
		n_transictions += 1
	if reciever:
		reciever.update_credit(amount)
		n_transictions += 1

	return n_transictions
