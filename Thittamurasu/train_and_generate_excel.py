import pandas as pd
import numpy as np
import json
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

def build_hybrid_engine_and_excel():
    print("🚀 Step 1: Loading Datasets...")
    
    # 1. Load the SFDB Master Data (This acts as our training data AND our village upload)
    try:
        df = pd.read_csv(r'D:\SA hackathon\thittamurasu\sfdb_master_data.csv')
    except FileNotFoundError:
        print("Error: sfdb_master_data.csv not found. Please run the generator script first.")
        return

    # 2. Load the JSON Rulebook (For post-ML prioritization)
    try:
        with open(r'D:\SA hackathon\CODING\TN_schemes_database.json', 'r', encoding='utf-8') as f:
            schemes_db = json.load(f)
    except FileNotFoundError:
        print("Error: tn_schemes_database.json not found.")
        return

    print("🧠 Step 2: Training the Machine Learning Model...")
    # Define features for training
    features = ['Age', 'Gender', 'Community', 'Education_Level', 'Occupation', 
                'Annual_Income', 'Marital_Status', 'Disability_Status']
    target = 'Eligible_Scheme'

    X = df[features].copy()
    y = df[target]

    # Encode categorical variables
    encoders = {}
    categorical_cols = ['Gender', 'Community', 'Education_Level', 'Occupation', 'Marital_Status']
    
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le

    # Train the Random Forest Model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    # Save the model and encoders for Django to use later
    with open('thitta_murasu_model.pkl', 'wb') as f:
        pickle.dump({'model': rf_model, 'encoders': encoders, 'features': features}, f)
    print("✅ Model trained and saved as 'thitta_murasu_model.pkl'")

    print("📊 Step 3: Generating Bulk SMS Excel for Panchayat Officials...")
    
    # Simulate a Panchayat official uploading 50 random citizens from their village
    village_batch = df.sample(n=50, random_state=99).copy()
    
    # Prepare lists to hold our generated SMS data
    top_schemes_list = []
    sms_tamil_list = []
    sms_english_list = []

    # Map JSON rules to a quick lookup dictionary for benefits and domains
    scheme_lookup = {s['name']: s for s in schemes_db}

    # Process each citizen in the uploaded batch
    for index, row in village_batch.iterrows():
        # Get ML prediction
        input_data = row[features].to_frame().T
        
        # Apply encoders
        for col in categorical_cols:
            known_classes = list(encoders[col].classes_)
            val = input_data[col].values[0]
            if val not in known_classes:
                val = known_classes[0]
            input_data[col] = encoders[col].transform([val])[0]
            
        predicted_scheme = rf_model.predict(input_data)[0]
        
        # If no scheme is found, leave messages blank
        if predicted_scheme == "General Welfare / No Specific Scheme":
            top_schemes_list.append("General Welfare")
            sms_tamil_list.append("தற்போது குறிப்பிட்ட திட்டங்கள் ஏதுமில்லை. பஞ்சாயத்து அலுவலகத்தை அணுகவும்.")
            sms_english_list.append("No specific schemes matched currently. Please contact the Panchayat office.")
            continue
            
        # Get scheme details from JSON rulebook
        scheme_details = scheme_lookup.get(predicted_scheme, {})
        scheme_domain = scheme_details.get('domain', 'Welfare')
        
        top_schemes_list.append(predicted_scheme)
        
        # Generate the exact SMS strings
        tamil_msg = f"திட்ட முரசு: நீங்கள் '{predicted_scheme}' திட்டத்திற்கு தகுதியானவர். விண்ணப்பிக்க தேவையான ஆவணங்களுடன் உங்கள் பஞ்சாயத்து / இ-சேவை மையத்தை அணுகவும்."
        english_msg = f"Thitta-Murasu Alert: You are eligible for '{predicted_scheme}'. Please visit your nearest e-Sevai/Panchayat office with required documents to apply."
        
        sms_tamil_list.append(tamil_msg)
        sms_english_list.append(english_msg)

    # Append the new columns to the DataFrame
    village_batch['Matched_Scheme'] = top_schemes_list
    village_batch['SMS_Tamil'] = sms_tamil_list
    village_batch['SMS_English'] = sms_english_list
    
    # Reorder columns so it looks clean for the official
    output_columns = ['SFDB_ID', 'Mobile_Number', 'Age', 'Gender', 'Annual_Income', 
                      'Matched_Scheme', 'SMS_Tamil', 'SMS_English']
    
    final_excel_df = village_batch[output_columns]
    
    # Export to Excel
    excel_filename = 'eligible_candidates_outreach.xlsx'
    final_excel_df.to_excel(excel_filename, index=False)
    
    print(f"✅ Success! Bulk outreach file saved as '{excel_filename}'")
    print("Opening a preview of the Excel output:")
    print(final_excel_df[['SFDB_ID', 'Mobile_Number', 'Matched_Scheme']].head())

if __name__ == "__main__":
    build_hybrid_engine_and_excel()