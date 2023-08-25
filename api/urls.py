from django.urls import path, re_path
from . import views


urlpatterns = [
	path('', views.helloWorld),
	path('loans/<int:id>/offers', views.getLoanOffers),
	path('loans/<int:id>/make-offer', views.makeOffer),
	path('offers/<int:id>/accept', views.acceptOffer),
	re_path(r'(?P<cls>\binvestors\b|borrowers\b|loans\b|offers)/(?P<id>\d+)$', views.getOne),
	re_path(r'(?P<cls>\binvestors\b|borrowers\b|loans\b|offers)$', views.getAll),
	path('create-loan', views.createLoan)
]
