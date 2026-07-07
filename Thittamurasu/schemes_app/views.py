# # schemes_app/views.py

# import json
# # import os
# import pandas as pd
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from twilio.rest import Client

# # Import your custom eligibility engine
# from .eligibility_engine import get_top_prioritized_schemes

# # --- DATA PRE-LOADING ---
# CSV_PATH = 'eligible_candidates_outreach.xlsx - Sheet1.csv'
# EXCEL_PATH = r'D:\SA hackathon\Thittamurasu\eligible_candidates_outreach.xlsx'

# try:
#     SFDB_DATA = pd.read_csv(CSV_PATH)
# except Exception as e:
#     print(f"Error loading SFDB CSV: {e}")
#     SFDB_DATA = pd.DataFrame()

# # 1. Enhanced Home Dashboard View
# def home_dashboard(request):
#     """Renders the high-impact dashboard with live stats from the SFDB."""
#     stats = {
#         'total_citizens': len(SFDB_DATA),
#         'total_matches': len(SFDB_DATA[SFDB_DATA['Matched_Scheme'] != 'General Welfare']) if not SFDB_DATA.empty else 0,
#         'accuracy': "98.4%",
#         'sms_sent': "1,240+" # Simulated for demo
#     }
    
#     # Categorized Schemes for UI display
#     domains = [
#         {'name': 'Women Welfare', 'icon': '👩', 'count': 15, 'desc': 'Urimai Thogai, Widow Pension'},
#         {'name': 'Senior Citizen', 'icon': '👴', 'count': 10, 'desc': 'Old Age Pension, Social Security'},
#         {'name': 'Agriculture', 'icon': '🌾', 'count': 12, 'desc': 'PM-Kisan, Uzhavar Thittam'},
#         {'name': 'Education', 'icon': '🎓', 'count': 8, 'desc': 'Tamil Pudhalvan, Scholarships'},
#     ]
    
#     return render(request, 'schemes_app/home.html', {'stats': stats, 'domains': domains})

# # 2. Individual Eligibility Checker View
# def check_eligibility(request):
#     context = {}
#     if request.method == "POST":
#         sfdb_id = request.POST.get('sfdb_id', '').strip()
#         domain = request.POST.get('domain', 'All Domains')
#         income_raw = request.POST.get('income')
#         income = int(income_raw) if income_raw and income_raw.isdigit() else 0
#         marital = request.POST.get('marital_status', 'Single')
#         pwd_raw = request.POST.get('disability')
#         pwd = int(pwd_raw) if pwd_raw and pwd_raw.isdigit() else 0
        
#         try:
#             response = get_top_prioritized_schemes(sfdb_id, domain, income, marital, pwd)
#             context['schemes'] = response.get("results", [])
#             context['sfdb_id'] = sfdb_id
#         except Exception as e:
#             context['error_message'] = "System busy. Please try again."
            
#     return render(request, 'schemes_app/eligibility.html', context)

# # 3. Bulk Outreach Dashboard View
# def bulk_outreach(request):
#     candidates = []
#     try:
#         if os.path.exists(EXCEL_PATH):
#             df = pd.read_excel(EXCEL_PATH)
#             candidates = df[df['Matched_Scheme'] != 'General Welfare'].to_dict('records')
#     except:
#         pass
#     return render(request, 'schemes_app/bulk_outreach.html', {'candidates': candidates})

# # 4. Live SMS Trigger View
# @csrf_exempt 
# def send_live_sms(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             # Paste your Twilio credentials here
#             # TWILIO_ACCOUNT_SID = 
#             # TWILIO_AUTH_TOKEN = 'enter'
#             # TWILIO_PHONE_NUMBER = 'enter'
#             client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#             message = client.messages.create(body=data.get('message'), from_=TWILIO_PHONE_NUMBER, to=data.get('mobile'))
#             return JsonResponse({"status": "success", "sid": message.sid})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)})
#     return JsonResponse({"status": "invalid"})

# def domain_schemes(request, domain_name):
#     """Lists all schemes under a specific domain with their eligibility rules."""
    
#     # This data is structured based on your TN Govt Schemes PDF
#     all_schemes = {
#         'Women Welfare': [
#             {'name': 'Kalaignar Magalir Urimai Thogai', 'eligibility': 'Age > 21, Annual Income < ₹2.5 Lakh, Land < 5 Acres.', 'benefit': 'Monthly ₹1000 via DBT.'},
#             {'name': 'Pudhumai Penn Scheme', 'eligibility': 'Girls who studied 6th-12th in Govt Schools.', 'benefit': 'Monthly ₹1000 for Higher Education.'},
#             {'name': 'Destitute Widow Pension', 'eligibility': 'Widows with no support, Income < ₹24,000/year.', 'benefit': 'Monthly ₹1200 + Rice.'}
#         ],
#         'Senior Citizen': [
#             {'name': 'Indira Gandhi Old Age Pension', 'eligibility': 'Age 60+, Below Poverty Line.', 'benefit': 'Monthly ₹1200.'},
#             {'name': 'Differently Abled Pension', 'eligibility': '40% or more disability, no age limit.', 'benefit': 'Monthly ₹1500.'}
#         ],
#         'Agriculture': [
#             {'name': 'Uzhavar Aluvalar Thodarbu Thittam', 'eligibility': 'Small/Marginal Farmers with Land Records.', 'benefit': 'Technical guidance & Input subsidy.'},
#             {'name': 'Kalaignarin Kanavu Illam', 'eligibility': 'Rural homeless families, specifically huts/kucha houses.', 'benefit': 'Financial aid for concrete house construction.'}
#         ],
#         'Education': [
#             {'name': 'Tamil Pudhalvan Thittam', 'eligibility': 'Boys from Govt Schools (6th-12th) entering Higher Ed.', 'benefit': 'Monthly ₹1000 for degrees/diplomas.'}
#         ]
#     }

#     selected_schemes = all_schemes.get(domain_name, [])
    
#     return render(request, 'schemes_app/domain_schemes.html', {
#         'domain': domain_name,
#         'schemes': selected_schemes
#     })