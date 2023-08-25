from rest_framework.response import Response
from rest_framework.decorators import api_view
from database.models import Investor, Borrower, Loan, Offer
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from datetime import timedelta, datetime


class_by_plural = {cls.plural: cls for cls in [Investor, Borrower, Loan, Offer]}


@api_view(['GET'])
def helloWorld(request):
	return Response({'first_word': 'Hello,', 'second_word': 'world!'})


@api_view(['GET'])
def getAll(request, *args, **kwargs):
	if kwargs['cls'] == 'create-loan':
		response = HttpResponse('')
		response.status_code = 405
		return response
	cls = class_by_plural.get(kwargs['cls'], None)
	if not cls:
		raise Http404
	return Response([obj.to_dict() for obj in cls.objects.all()])


@api_view(['GET'])
def getOne(request, *args, **kwargs):
	cls = class_by_plural.get(kwargs['cls'], None)
	if not cls:
		raise Http404
	return Response(get_object_or_404(cls, id=kwargs['id']).to_dict())


@api_view(['GET'])
def getLoanOffers(request, *args, **kwargs):
	loan = get_object_or_404(Loan, id=kwargs['id'])
	return Response([offer.to_dict() for offer in Offer.objects.filter(loan=loan)])


@api_view(['POST'])
def createLoan(request):
	# Make sure that the sender is a borrower

	# Make sure that the body contains amount, period and borrower_id
	if sum([1 for k in ['amount', 'period', 'borrower_id'] if k in request.data]) < 3:
		return HttpResponseBadRequest()

	# Make sure that the sender's id is borrower_id

	# Create loan
	amount, period, borrower_id = request.data['amount'], request.data['period'], request.data['borrower_id']
	loan = Loan.objects.create(amount=amount, period=timedelta(days=period * 30), borrower=Borrower.objects.get(id=borrower_id))
	return Response(loan.to_dict())


@api_view(['POST'])
def makeOffer(request, **kwargs):
	# Make sure that the sender is an investor

	# Make sure that the body contains investor_id, annual_interest
	if sum([1 for k in ['investor_id', 'annual_interest'] if k in request.data]) < 2:
		return HttpResponseBadRequest()

	# Make sure that the sender's id is investor_id

	# Make sure that the loan exists and its status is pending
	loan_id = kwargs['id']
	loan = get_object_or_404(Loan, id=loan_id)
	if loan.status != 'Pending':
		return HttpResponseBadRequest()

	# Checking the paying ability
	investor_id, annual_interest = request.data['investor_id'], request.data['annual_interest']
	investor = Investor.objects.get(id=investor_id)
	if investor.credit < loan.amount + loan.fee:
		return HttpResponseForbidden()

	# Make offer
	offer = Offer.objects.create(investor=investor, annual_interest=annual_interest, loan=loan)
	return Response(offer.to_dict())


@api_view(['PATCH'])
def acceptOffer(request, **kwargs):
	# Make sure that the sender is a borrower

	# Make sure that the body contains borrower_id
	if 'borrower_id' not in request.data:
		return HttpResponseBadRequest()

	# Make sure that the offer exists and its status is pending
	offer = get_object_or_404(Offer, id=kwargs['id'])
	if offer.status != 'Pending':
		return HttpResponseBadRequest()

	# Accepting the offer and declining any other offer on the same loan
	loan = offer.loan
	all_offers = [offer_ for offer_ in Offer.objects.filter(loan=loan)]
	for offer_ in all_offers:
		if offer_ == offer:
			offer_.status = 'Accepted'
		else:
			offer_.status = 'Declined'
		offer_.offer_concluded = datetime.now()
		offer_.save()

	# Transfering money
	offer.investor.credit -= loan.amount + loan.fee
	loan.borrower.credit += loan.amount

	# Making the loan status is Funded
	loan.status = 'Funded'
	loan.investor = offer.investor
	loan.annual_interest = offer.annual_interest
	loan.loan_funded = datetime.now()

	loan.save()
	offer.investor.save()
	loan.borrower.save()
	return Response(offer.to_dict())
