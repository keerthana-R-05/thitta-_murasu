from django.urls import path
from . import views

urlpatterns = [
    # 1. Main Landing Page
    path('', views.home_dashboard, name='home'),
    
    # 2. Individual Eligibility Predictor
    path('check-eligibility/', views.check_eligibility, name='check_eligibility'),
    
    # 3. Official Outreach Dashboard (Excel View)
    path('bulk-outreach/', views.bulk_outreach, name='bulk_outreach'),
    
    # 4. API Endpoint for Twilio SMS
    path('send-live-sms/', views.send_live_sms, name='send_live_sms'),

    path('domain-schemes/<str:domain_name>/', views.domain_schemes, name='domain_schemes'),
]