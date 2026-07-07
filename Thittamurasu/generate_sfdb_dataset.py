import pandas as pd
import numpy as np
import random
import string

def generate_sfdb_dataset(num_records=10000):
    print(f"Generating {num_records} rows for the State Family Database (SFDB)...")
    data = []
    
    # Tamil Nadu specific districts [cite: 483]
    tn_districts = ['Theni', 'Madurai', 'Ramanathapuram', 'Chennai', 'Coimbatore', 
                    'Tirunelveli', 'Kanyakumari', 'Trichy', 'Salem', 'Vellore']
    
    # Helper to generate alphanumeric "Fake Aadhaar" (e.g., TN-A1B2-C3D4)
    def generate_sfdb_id():
        chars = string.ascii_uppercase + string.digits
        part1 = ''.join(random.choices(chars, k=4))
        part2 = ''.join(random.choices(chars, k=4))
        return f"TN-{part1}-{part2}"

    # Helper to generate fake Indian mobile numbers
    def generate_mobile():
        return f"+91{random.choice(['9', '8', '7', '6'])}{random.randint(100000000, 999999999)}"

    for i in range(num_records):
        sfdb_id = generate_sfdb_id()
        mobile_num = generate_mobile()
        district = random.choice(tn_districts)
        
        # Base Demographics (Stored in DB)
        age = random.randint(16, 85)
        gender = np.random.choice(['Male', 'Female'], p=[0.49, 0.51])
        community = np.random.choice(['BC', 'MBC', 'SC', 'ST', 'General'], p=[0.40, 0.30, 0.20, 0.05, 0.05])
        
        education = np.random.choice(
            ['Illiterate', '8th Pass', '10th Pass', '12th Pass', 'Diploma', 'Graduate'], 
            p=[0.15, 0.20, 0.30, 0.20, 0.05, 0.10]
        )
        
        if age < 22:
            occupation = 'Student'
        elif age >= 65:
            occupation = 'Unemployed'
        else:
            occupation = np.random.choice(
                ['Agriculture', 'Daily Wage', 'Weaver', 'Unemployed', 'Self-Employed'],
                p=[0.4, 0.35, 0.05, 0.1, 0.1]
            )

        # Volatile Demographics (What user enters to check eligibility)
        income = int(np.random.choice(
            [random.randint(15000, 40000), random.randint(40000, 80000), 
             random.randint(80000, 150000), random.randint(150000, 300000)],
            p=[0.3, 0.4, 0.2, 0.1]
        ))
        
        if age < 21:
            marital_status = 'Single'
        elif age > 65:
            marital_status = np.random.choice(['Married', 'Widow'], p=[0.6, 0.4])
        else:
            marital_status = np.random.choice(['Single', 'Married', 'Widow', 'Separated'], p=[0.2, 0.65, 0.1, 0.05])
            
        disability_status = np.random.choice([0, 1], p=[0.95, 0.05])

        # Exact Scheme Logic based on TN Zero Series PDF
        scheme = "General Welfare / No Specific Scheme"
        
        # 1. Pudhumai Penn (Moovalur Ramamirtham) [cite: 142]
        if gender == 'Female' and 17 <= age <= 23 and education in ['12th Pass', 'Diploma', 'Graduate']:
            scheme = "Pudhumai Penn Scheme"
            
        # 2. Tamil Pudhalvan Thittam [cite: 154]
        elif gender == 'Male' and 17 <= age <= 23 and education in ['12th Pass', 'Diploma', 'Graduate']:
            scheme = "Tamil Pudhalvan Thittam"
            
        # 3. Differently Abled Pension
        elif disability_status == 1:
            scheme = "Differently Abled Pension Scheme"
            
        # 4. Dr. Dharmambal Ammaiyar Widow Remarriage [cite: 278] / Destitute Widow
        elif gender == 'Female' and marital_status == 'Widow':
            if income < 100000:
                scheme = "Destitute Widow Pension Scheme"
            else:
                scheme = "Dr. Dharmambal Ammaiyar Widow Remarriage Assistance"
                
        # 5. Indira Gandhi National Old Age Pension [cite: 356]
        elif age >= 60 and income < 100000:
            scheme = "Indira Gandhi National Old Age Pension"
            
        # 6. Kalaignar Magalir Urimai Thogai Thittam [cite: 142]
        elif gender == 'Female' and age >= 21 and income < 250000 and marital_status in ['Married', 'Widow', 'Separated']:
            scheme = "Kalaignar Magalir Urimai Thogai"
            
        # 7. Uzhavar Aluvalar Thodarbu Thittam [cite: 381]
        elif occupation == 'Agriculture':
            scheme = "Uzhavar Aluvalar Thodarbu Thittam"
            
        # 8. MGNREGS [cite: 483]
        elif occupation == 'Daily Wage' and 18 <= age <= 59:
            scheme = "MGNREGS (100 Days Work)"

        data.append([
            sfdb_id, mobile_num, district, age, gender, community, 
            education, occupation, income, marital_status, 
            disability_status, scheme
        ])

    columns = [
        'SFDB_ID', 'Mobile_Number', 'District', 'Age', 'Gender', 'Community', 
        'Education_Level', 'Occupation', 'Annual_Income', 'Marital_Status', 
        'Disability_Status', 'Eligible_Scheme'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    
    # Save the master dataset
    df.to_csv('sfdb_master_data.csv', index=False)
    print("Success! 'sfdb_master_data.csv' created with 10,000 rows.")
    print("\nSample of generated SFDB IDs:")
    print(df[['SFDB_ID', 'Mobile_Number', 'Eligible_Scheme']].head())

if __name__ == "__main__":
    generate_sfdb_dataset()