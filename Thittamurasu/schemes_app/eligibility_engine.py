import pandas as pd
import numpy as np
import pickle
import json
import os

def get_top_prioritized_schemes(sfdb_id, selected_domain, income, marital_status, disability_status):
    """
    Takes the user's inputs from the Django form, looks up their static profile,
    runs the ML model, applies domain/priority rules, and returns Top 3 schemes.
    """
    
    # 1. Load the SFDB Database to find the citizen's static details
    try:
        # Update these paths to match your Django project structure later
        # 1. Load the SFDB Database to find the citizen's static details
   
        df = pd.read_csv(r'D:\SA hackathon\Thittamurasu\sfdb_master_data.csv')
    except FileNotFoundError:
        return {"error": "SFDB Database not found."}

    # Find the citizen
    citizen = df[df['SFDB_ID'] == sfdb_id]
    if citizen.empty:
        return {"error": f"SFDB ID '{sfdb_id}' not found in the state database."}
    
    # Extract static details
    age = int(citizen['Age'].values[0])
    gender = citizen['Gender'].values[0]
    community = citizen['Community'].values[0]
    education = citizen['Education_Level'].values[0]
    occupation = citizen['Occupation'].values[0]

    # 2. Combine static details with the volatile details entered in the UI
    profile = {
        'Age': age,
        'Gender': gender,
        'Community': community,
        'Education_Level': education,
        'Occupation': occupation,
        'Annual_Income': int(income),
        'Marital_Status': marital_status,
        'Disability_Status': int(disability_status)
    }

    # 3. Load the trained ML Model and Encoders
    try:
        with open(r'D:\SA hackathon\Thittamurasu\thitta_murasu_model.pkl', 'rb') as f:
            saved_data = pickle.load(f)
            rf_model = saved_data['model']
            encoders = saved_data['encoders']
            features = saved_data['features']
    except FileNotFoundError:
        return {"error": "Machine Learning model not found. Train it first."}

    # Format data for ML prediction
    input_df = pd.DataFrame([profile])
    
    # Apply label encoders safely
    categorical_cols = ['Gender', 'Community', 'Education_Level', 'Occupation', 'Marital_Status']
    for col in categorical_cols:
        known_classes = list(encoders[col].classes_)
        val = input_df[col].values[0]
        if val not in known_classes:
            val = known_classes[0] # Fallback to prevent crashes
        input_df[col] = encoders[col].transform([val])

    # 4. Get ML Probabilities
    ml_probabilities = rf_model.predict_proba(input_df[features])[0]
    model_classes = rf_model.classes_

    # 5. Load the JSON Rulebook for Priority & Domain Filtering
    try:
        with open(r'D:\SA hackathon\CODING\TN_schemes_database.json', 'r', encoding='utf-8') as f:
            schemes_db = json.load(f)
    except FileNotFoundError:
        return {"error": "Schemes rulebook JSON not found."}
        
    scheme_lookup = {s['name']: s for s in schemes_db}
    
    # 6. Hybrid Filtering & Scoring
    scored_schemes = []
    
    for idx, scheme_name in enumerate(model_classes):
        if scheme_name == "General Welfare / No Specific Scheme":
            continue
            
        meta = scheme_lookup.get(scheme_name, {})
        if not meta:
            continue # Skip if scheme isn't in our JSON rulebook
            
        scheme_domain = meta.get("domain", "Other")
        base_priority = meta.get("base_priority_weight", 5)
        
        # Domain Filter Check
        if selected_domain != "All Domains" and scheme_domain != selected_domain:
            continue
            
        ml_confidence = ml_probabilities[idx]
        
        # Only consider schemes where the ML model shows at least a 2% mathematical probability
        if ml_confidence > 0.02:
            # Dynamic Priority Scoring
            dynamic_score = (ml_confidence * 100) + base_priority
            
            # Add vulnerability bonus points
            if profile['Annual_Income'] < 50000:
                dynamic_score += 3
            if profile['Marital_Status'] == 'Widow':
                dynamic_score += 2
                
            scored_schemes.append({
                "name": scheme_name,
                "domain": scheme_domain,
                "benefit": meta.get("benefit", "Check portal for details."),
                "confidence_score": round(ml_confidence * 100, 1),
                "final_priority": round(dynamic_score, 1)
            })
            
    # 7. Sort by Final Priority and get Top 3
    scored_schemes.sort(key=lambda x: x['final_priority'], reverse=True)
    top_3 = scored_schemes[:3]
    
    if not top_3:
        return {"status": "success", "results": []}
        
    return {"status": "success", "results": top_3, "static_profile": profile}