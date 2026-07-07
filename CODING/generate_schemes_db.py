import json
import os

def generate_schemes_database():
    print("Generating Tamil Nadu Schemes Master Database...")
    
    # Structured dataset of schemes with their exact eligibility parameters
    schemes_data = [
        {
            "scheme_id": "TN-EDU-001",
            "name": "Pudhumai Penn Thittam (Moovalur Ramamirtham)",
            "domain": "Educational Welfare",
            "benefit": "Rs. 1,000 per month for Girl students pursuing higher education.",
            "base_priority_weight": 9,
            "eligibility_rules": {
                "required_gender": ["Female"],
                "min_age": 16,
                "max_age": 25,
                "required_education": ["6th to 12th", "Degree/Diploma"]
            }
        },
        {
            "scheme_id": "TN-EDU-002",
            "name": "Tamil Pudhalvan Thittam",
            "domain": "Educational Welfare",
            "benefit": "Rs. 1,000 per month for Boy students studying in Govt schools.",
            "base_priority_weight": 9,
            "eligibility_rules": {
                "required_gender": ["Male"],
                "min_age": 16,
                "max_age": 25,
                "required_education": ["6th to 12th", "Degree/Diploma"]
            }
        },
        {
            "scheme_id": "TN-WOM-001",
            "name": "Kalaignar Magalir Urimai Thogai Thittam",
            "domain": "Women Welfare",
            "benefit": "Rs. 1,000 per month financial assistance for women heads of households.",
            "base_priority_weight": 10,
            "eligibility_rules": {
                "required_gender": ["Female"],
                "min_age": 21,
                "max_age": 100,
                "max_income": 250000
            }
        },
        {
            "scheme_id": "TN-MAR-001",
            "name": "Dr. Dharmambal Ammaiyar Widow Remarriage Assistance",
            "domain": "Marriage Assistance",
            "benefit": "Up to Rs. 50,000 assistance + 8 gram gold coin. No income limit.",
            "base_priority_weight": 10,
            "eligibility_rules": {
                "required_gender": ["Female"],
                "required_marital_status": ["Widow"]
            }
        },
        {
            "scheme_id": "TN-SEN-001",
            "name": "Indira Gandhi National Old Age Pension",
            "domain": "Senior Citizen Welfare",
            "benefit": "Monthly pension of Rs. 1,200 for senior citizens.",
            "base_priority_weight": 10,
            "eligibility_rules": {
                "min_age": 60,
                "max_age": 120,
                "max_income": 100000
            }
        },
        {
            "scheme_id": "TN-POV-001",
            "name": "Chief Minister's Thayumanavar Thittam",
            "domain": "Poverty Eradication",
            "benefit": "Comprehensive poverty eradication support to bring families out of extreme poverty.",
            "base_priority_weight": 10,
            "eligibility_rules": {
                "max_income": 50000
            }
        },
        {
            "scheme_id": "TN-AGR-001",
            "name": "Uzhavar Aluvalar Thodarbu Thittam 2.0",
            "domain": "Agriculture Welfare",
            "benefit": "Direct access to agricultural extension officers for modern crop tech dissemination.",
            "base_priority_weight": 7,
            "eligibility_rules": {
                "required_occupation": ["Agriculture"]
            }
        },
        {
            "scheme_id": "TN-WOM-002",
            "name": "Mahalir Thittam (SHG Loan Scheme)",
            "domain": "Women Welfare",
            "benefit": "Financial assistance, skill training, and credit linkage through Self Help Groups.",
            "base_priority_weight": 8,
            "eligibility_rules": {
                "required_gender": ["Female"],
                "min_age": 18,
                "max_age": 55
            }
        },
        {
            "scheme_id": "TN-HOU-001",
            "name": "Kalaignarin Kanavu Illam (Rural Housing)",
            "domain": "Rural Development",
            "benefit": "Financial aid for constructing concrete houses to create a 'Hut-Free Tamil Nadu'.",
            "base_priority_weight": 9,
            "eligibility_rules": {
                "max_income": 100000,
                "required_occupation": ["Agriculture", "Daily Wage"]
            }
        },
        {
            "scheme_id": "TN-EMP-001",
            "name": "MGNREGS (100 Days Rural Employment)",
            "domain": "Rural Development",
            "benefit": "Guaranteed 100 days of wage employment in a financial year.",
            "base_priority_weight": 8,
            "eligibility_rules": {
                "min_age": 18,
                "max_age": 59,
                "required_occupation": ["Agriculture", "Daily Wage", "Unemployed"]
            }
        }
    ]

    # Save to a JSON file
    filename = "tn_schemes_database.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schemes_data, f, indent=4, ensure_ascii=False)
        
    print(f"Success! {len(schemes_data)} schemes exported to '{filename}'.")
    print("This JSON file can now be directly loaded into your Node.js or Python backend for cross-checking.")

if __name__ == "__main__":
    generate_schemes_database()