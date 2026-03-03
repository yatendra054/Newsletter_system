from django.urls import path, include
from assessment import views

urlpatterns = [
    path('', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:email>/', views.unsubscribe, name='unsubscribe'),

    path('send-campaign/', views.send_campaign, name='send_campaign'),
    path('send-campaign/<int:campaign_id>/', views.send_campaign, name='send_campaign_id'),
    path('campaign/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
]



