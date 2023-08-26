from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from database.models import Investor, Borrower, Loan, Offer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from database.financial_operations import check_if_can_afford
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication, BaseAuthentication, RemoteUserAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta


class_by_plural = {cls.plural: cls for cls in [Investor, Borrower, Loan, Offer]}


@api_view(['GET'])
def helloWorld(request):
	return Response({'first_word': 'Hello,', 'second_word': 'world!'})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def whoAmI(request, format=None):
	print('#######################Who are you?#########################')
	content = {'user': str(request.user), 'auth': str(request.auth)}
	return Response(content)


@api_view(['GET'])
def getAll(request, *args, **kwargs):
	cls = class_by_plural.get(kwargs['cls'], None)
	if not cls:
		raise Http404
	return Response([obj.to_dict() for obj in cls.objects.all()])


@api_view(['GET'])
def getOne(request, *args, **kwargs):
	cls = class_by_plural.get(kwargs['cls'], None)
	id = kwargs['id']

	if not cls:
		raise Http404

	if cls in [Investor, Borrower]:
		user = get_object_or_404(User, id=id)
		person = get_object_or_404(cls, user=user)
		return Response(person.to_dict())

	return Response(get_object_or_404(cls, id=kwargs['id']).to_dict())


@api_view(['GET'])
def getLoanOffers(request, *args, **kwargs):
	loan = get_object_or_404(Loan, id=kwargs['id'])
	return Response([offer.to_dict() for offer in Offer.objects.filter(loan=loan)])


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def createLoan(request):
	# Make sure that the body contains amount, period and borrower_id (period here is in months)
	if sum([1 for k in ['amount', 'period', 'borrower_id'] if k in request.data]) < 3:
		return HttpResponseBadRequest("bad request 1")

	# Make sure that the sender's id is borrower_id
	amount, period, borrower_id = request.data['amount'], request.data['period'], request.data['borrower_id']
	try:
		amount, period, borrower_id = int(amount), int(period), int(borrower_id)
	except Exception:
		return HttpResponseBadRequest("bad request 2")
	borrower = get_object_or_404(Borrower, user__id=borrower_id)
	if request.user.id != borrower.user.id:
		return HttpResponseForbidden("permission denied")

	# Create loan
	loan = Loan.objects.create(amount=amount, period=timedelta(days=period * 30), borrower=borrower)
	return Response(loan.to_dict())


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def makeOffer(request, **kwargs):
	# Make sure that the body contains investor_id, annual_interest
	if sum([1 for k in ['investor_id', 'annual_interest'] if k in request.data]) < 2:
		return HttpResponseBadRequest()

	# Getting investor
	investor_id, annual_interest = request.data['investor_id'], request.data['annual_interest']
	try:
		investor_id = int(investor_id)
		annual_interest = float(annual_interest)
		investor = Investor.objects.get(user__id=investor_id)
	except Exception:
		return HttpResponseBadRequest()

	# Make sure that the sender id is the investor id
	if request.user.id != investor.user.id:
		return HttpResponseForbidden("permission denied.")

	# Make sure that the loan exists and its status is pending
	loan_id = kwargs['id']
	loan = get_object_or_404(Loan, id=loan_id)
	if loan.status != 'Pending':
		return HttpResponseBadRequest()

	# Checking paying ability
	if not check_if_can_afford(loan.amount + loan.fee, investor):
		return HttpResponseForbidden("Credit is lower than expected.")

	# Make offer
	offer = Offer.objects.create(investor=investor, annual_interest=annual_interest, loan=loan)
	return Response(offer.to_dict())


@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def acceptOffer(request, **kwargs):
	# Make sure that the body contains borrower_id
	if 'borrower_id' not in request.data:
		return HttpResponseBadRequest()

	# Getting borrower
	borrower_id = request.data['borrower_id']
	try:
		borrower_id = int(borrower_id)
		borrower = Borrower.objects.get(user__id=borrower_id)
	except Exception:
		return HttpResponseBadRequest()

	# Make sure that the sender is the borrower
	if request.user.id != borrower.user.id:
		return HttpResponseForbidden()

	# Make sure that the offer exists and its status is pending
	offer = get_object_or_404(Offer, id=kwargs['id'])
	if offer.status != 'Pending':
		return HttpResponseBadRequest()

	# Accepting the offer and declining any other offer on the same loan
	loan = offer.loan
	all_offers = [offer_ for offer_ in Offer.objects.filter(loan=loan)]
	for offer_ in all_offers:
		if offer_ == offer:
			offer_.accept()
		else:
			offer_.decline()

	# Transfering money
	loan.funded(offer.investor, offer.annual_interest)

	return Response(offer.to_dict())
