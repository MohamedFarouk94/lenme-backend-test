from django.urls import path, re_path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
	path('', views.helloWorld, name='hello_world'),
	path('api-token-auth/', obtain_auth_token),
	path('who-am-i', views.whoAmI, name='who_am_i'),
	path('loans/<int:id>/offers', views.getLoanOffers),
	path('loans/<int:id>/make-offer', views.makeOffer),
	path('offers/<int:id>/accept', views.acceptOffer),
	re_path(r'(?P<cls>\binvestors\b|borrowers\b|loans\b|offers)/(?P<id>\d+)$', views.getOne),
	re_path(r'(?P<cls>\binvestors\b|borrowers\b|loans\b|offers)$', views.getAll),
	path('create-loan', views.createLoan)
]
