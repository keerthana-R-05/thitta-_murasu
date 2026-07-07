import pandas as pd
import numpy as np
import random

def generate_tn_synthetic_data_v2(num_records=10000):
    data = []
    
    tn_districts = ['Theni', 'Madurai', 'Dindigul', 'Ramanathapuram', 'Virudhunagar', 
                    'Sivaganga', 'Thoothukudi', 'Tirunelveli', 'Tenkasi', 'Kanyakumari']
    
    for i in range(1, num_records + 1):
        # 1. Base Demographics
        district = random.choice(tn_districts)
        dist_code = district[:3].upper()
        citizen_id = f"TN-{dist_code}-{random.randint(100000, 999999)}"
        
        age = random.randint(17, 85)
        gender = np.random.choice(['Male', 'Female'], p=[0.48, 0.52])
        community = np.random.choice(['BC', 'MBC', 'SC', 'ST', 'General'], p=[0.40, 0.30, 0.20, 0.05, 0.05])
        
        # IMPROVEMENT 1: Realistic Income Skew (Majority under 1 Lakh)
        income = int(np.random.choice(
            [random.randint(15000, 40000), random.randint(40000, 72000), 
             random.randint(72000, 120000), random.randint(120000, 250000)],
            p=[0.3, 0.4, 0.2, 0.1]
        ))
        
        # IMPROVEMENT 2: Smart Ration Card Type
        if income < 72000:
            ration_card = np.random.choice(['PHH', 'AAY'], p=[0.8, 0.2])
        elif income < 120000:
            ration_card = 'PHH'
        else:
            ration_card = 'NPHH'
            
        education = np.random.choice(
            ['Illiterate', '8th Pass', '10th Pass', '12th Pass', 'Diploma', 'Graduate'], 
            p=[0.15, 0.20, 0.30, 0.20, 0.05, 0.10]
        )
        
        if age < 21:
            marital_status = 'Single'
        elif age > 65:
            marital_status = np.random.choice(['Married', 'Widow'], p=[0.6, 0.4])
        else:
            marital_status = np.random.choice(['Single', 'Married', 'Widow', 'Separated'], p=[0.2, 0.65, 0.1, 0.05])
            
        disability_status = np.random.choice([0, 1], p=[0.96, 0.04])
        shg_member = np.random.choice([0, 1], p=[0.6, 0.4]) if gender == 'Female' and age >= 18 else 0
        
        if age < 22:
            occupation = 'Student'
        elif age >= 65:
            occupation = 'Unemployed'
        else:
            occupation = np.random.choice(
                ['Agriculture', 'Daily Wage', 'Weaver', 'Unemployed', 'Self-Employed'],
                p=[0.4, 0.35, 0.05, 0.1, 0.1]
            )

        # IMPROVEMENT 3: Land Holding for Farmers (in Acres)
        if occupation == 'Agriculture':
            land_acres = round(random.uniform(0.5, 5.0), 1)
        else:
            land_acres = 0.0

        # 4. Upgraded Scheme Logic
        scheme = "Not Eligible / General Public"
        
        if disability_status == 1:
            scheme = "Differently Abled Pension Scheme"
        elif gender == 'Female' and age >= 17 and age <= 23 and education in ['12th Pass', 'Diploma', 'Graduate']:
            scheme = "Pudhumai Penn Scheme (Moovalur Ramamirtham)"
        elif gender == 'Female' and marital_status == 'Widow' and ration_card in ['PHH', 'AAY']:
            scheme = "Destitute Widow Pension Scheme"
        elif age >= 60 and ration_card in ['PHH', 'AAY']:
            scheme = "Indira Gandhi National Old Age Pension"
        # New Agricultural Scheme based on Land Holding
        elif occupation == 'Agriculture' and land_acres <= 2.5:
            scheme = "Uzhavar Pathukappu Thittam (Marginal Farmer)"
        elif gender == 'Female' and shg_member == 1 and age <= 55:
            scheme = "Mahalir Thittam (SHG Loan Scheme)"
        elif ration_card == 'PHH' and occupation in ['Daily Wage', 'Agriculture'] and marital_status == 'Married':
            scheme = "Kalaignarin Kanavu Illam (Housing)"
        elif occupation in ['Daily Wage', 'Agriculture'] and age >= 18 and age <= 59:
            scheme = "MGNREGS (100 Days Rural Employment)"
            
        data.append([
            citizen_id, district, age, gender, community, income, ration_card,
            education, occupation, land_acres, marital_status, disability_status, 
            shg_member, scheme
        ])

    columns = [
        'Citizen_ID', 'District', 'Age', 'Gender', 'Community', 'Annual_Income', 'Ration_Card_Type',
        'Education_Level', 'Occupation', 'Land_Holding_Acres', 'Marital_Status', 'Disability_Status', 
        'SHG_Member', 'Eligible_Scheme'
    ]
    df = pd.DataFrame(data, columns=columns)
    return df

if __name__ == "__main__":
    print("Generating 10,000 rows of upgraded TN demographic data...")
    dataset = generate_tn_synthetic_data_v2(10000)
    dataset.to_csv('tn_rural_schemes_10k_v2.csv', index=False)
    print("Success! Dataset saved as tn_rural_schemes_10k_v2.csv")