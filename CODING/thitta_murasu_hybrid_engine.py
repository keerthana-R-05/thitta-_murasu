import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# --- 1. SCHEME METADATA (DOMAIN & PRIORITY RULES) ---
# This maps the ML output classes to domains and priority weights
scheme_metadata = {
    "Pudhumai Penn Scheme (Moovalur Ramamirtham)": {"domain": "Educational Welfare", "priority": 10, "benefit": "Rs. 1,000/month for girls' higher education"},
    "Destitute Widow Pension Scheme": {"domain": "Women Welfare", "priority": 10, "benefit": "Financial assistance for destitute widows"},
    "Indira Gandhi National Old Age Pension": {"domain": "Senior Citizen Welfare", "priority": 10, "benefit": "Monthly pension of Rs. 1,200"},
    "Uzhavar Pathukappu Thittam (Marginal Farmer)": {"domain": "Agriculture Welfare", "priority": 8, "benefit": "Comprehensive welfare for marginal farmers"},
    "Mahalir Thittam (SHG Loan Scheme)": {"domain": "Women Welfare", "priority": 8, "benefit": "Credit linkage through Self Help Groups"},
    "Kalaignarin Kanavu Illam (Housing)": {"domain": "Rural Development", "priority": 9, "benefit": "Financial aid for concrete houses"},
    "MGNREGS (100 Days Rural Employment)": {"domain": "Rural Development", "priority": 7, "benefit": "100 days guaranteed wage employment"},
    "Differently Abled Pension Scheme": {"domain": "Welfare of Differently Abled", "priority": 10, "benefit": "Monthly pension for differently abled"},
    "Not Eligible / General Public": {"domain": "None", "priority": 0, "benefit": "N/A"}
}

# --- 2. MACHINE LEARNING TRAINING PHASE ---
def train_hybrid_model():
    print("Initializing Hybrid Engine: Loading data and training Random Forest...")
    file_path = 'D:\SA hackathon\CODING\Tn_rural_schemes_10k_v2.csv'
    
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"Dataset '{file_path}' not found! Run dataset generator.")
        return None, None, None, None
        
    df = pd.read_csv(file_path)
    
    features = ['Age', 'Gender', 'Community', 'Annual_Income', 'Ration_Card_Type',
                'Education_Level', 'Occupation', 'Land_Holding_Acres', 'Marital_Status', 
                'Disability_Status', 'SHG_Member']
    target = 'Eligible_Scheme'
    
    X = df[features].copy()
    y = df[target]
    
    encoders = {}
    categorical_cols = ['Gender', 'Community', 'Ration_Card_Type', 'Education_Level', 'Occupation', 'Marital_Status']
    
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    # Train Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    # Get the exact order of classes the model learned
    model_classes = rf_model.classes_ 
    
    print("Hybrid ML Engine training complete!")
    return rf_model, encoders, features, model_classes

# --- 3. GUI & RECOMMENDATION ENGINE ---
def create_gui(model, encoders, feature_names, model_classes):
    if model is None:
        return
        
    root = tk.Tk()
    root.title("Thitta-Murasu: Hybrid ML & Domain Eligibility Engine")
    root.geometry("680x800")
    root.configure(bg="#ecf0f1")
    
    style = ttk.Style()
    style.theme_use('clam')
    
    # Headers
    tk.Label(root, text="திட்ட முரசு (Thitta-Murasu)", font=("Arial", 16, "bold"), bg="#2980b9", fg="white", pady=10).pack(fill=tk.X)
    tk.Label(root, text="Hybrid ML & Domain Filtering Dashboard", font=("Arial", 11, "italic"), bg="#34495e", fg="white", pady=5).pack(fill=tk.X)
    
    form_frame = tk.Frame(root, bg="#ecf0f1", padx=20, pady=10)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    inputs = {}
    row_idx = 0
    
    def add_dropdown(label_text, var_name, options):
        nonlocal row_idx
        tk.Label(form_frame, text=label_text, bg="#ecf0f1", font=("Arial", 10)).grid(row=row_idx, column=0, sticky="w", pady=5)
        combo = ttk.Combobox(form_frame, values=options, state="readonly", width=32)
        combo.current(0)
        combo.grid(row=row_idx, column=1, pady=5, padx=10)
        inputs[var_name] = combo
        row_idx += 1
        
    def add_entry(label_text, var_name):
        nonlocal row_idx
        tk.Label(form_frame, text=label_text, bg="#ecf0f1", font=("Arial", 10)).grid(row=row_idx, column=0, sticky="w", pady=5)
        entry = ttk.Entry(form_frame, width=34)
        entry.grid(row=row_idx, column=1, pady=5, padx=10)
        inputs[var_name] = entry
        row_idx += 1

    # Domain Selector
    tk.Label(form_frame, text="Select Scheme Domain:", bg="#ecf0f1", font=("Arial", 11, "bold"), fg="#c0392b").grid(row=row_idx, column=0, sticky="w", pady=15)
    domain_combo = ttk.Combobox(form_frame, values=[
        "All Domains", "Educational Welfare", "Women Welfare", 
        "Senior Citizen Welfare", "Agriculture Welfare", "Rural Development", "Welfare of Differently Abled"
    ], state="readonly", width=32)
    domain_combo.current(0)
    domain_combo.grid(row=row_idx, column=1, pady=15, padx=10)
    row_idx += 1

    # User Inputs
    add_entry("Age (Years):", "Age")
    add_dropdown("Gender:", "Gender", ["Female", "Male"])
    add_dropdown("Community:", "Community", ["BC", "MBC", "SC", "ST", "General"])
    add_entry("Annual Income (₹):", "Annual_Income")
    add_dropdown("Ration Card Type:", "Ration_Card_Type", ["PHH", "AAY", "NPHH"])
    add_dropdown("Education Level:", "Education_Level", ["Illiterate", "8th Pass", "10th Pass", "12th Pass", "Diploma", "Graduate"])
    add_dropdown("Occupation:", "Occupation", ["Agriculture", "Daily Wage", "Weaver", "Unemployed", "Self-Employed", "Student"])
    add_entry("Land Holding (Acres):", "Land_Holding_Acres")
    add_dropdown("Marital Status:", "Marital_Status", ["Single", "Married", "Widow", "Separated"])
    add_dropdown("Disability Status:", "Disability_Status", ["No", "Yes"])
    add_dropdown("SHG Member (Mahalir Thittam):", "SHG_Member", ["No", "Yes"])
    
    def process_hybrid_prediction():
        try:
            # 1. Format Input Data
            data = {
                'Age': int(inputs['Age'].get()),
                'Gender': inputs['Gender'].get(),
                'Community': inputs['Community'].get(),
                'Annual_Income': int(inputs['Annual_Income'].get()),
                'Ration_Card_Type': inputs['Ration_Card_Type'].get(),
                'Education_Level': inputs['Education_Level'].get(),
                'Occupation': inputs['Occupation'].get(),
                'Land_Holding_Acres': float(inputs['Land_Holding_Acres'].get() or 0.0),
                'Marital_Status': inputs['Marital_Status'].get(),
                'Disability_Status': 1 if inputs['Disability_Status'].get() == "Yes" else 0,
                'SHG_Member': 1 if inputs['SHG_Member'].get() == "Yes" else 0
            }
            input_df = pd.DataFrame([data])
            selected_domain = domain_combo.get()
            
            # 2. Encode categorical data for ML
            categorical_cols = ['Gender', 'Community', 'Ration_Card_Type', 'Education_Level', 'Occupation', 'Marital_Status']
            for col in categorical_cols:
                known_classes = list(encoders[col].classes_)
                if input_df[col][0] not in known_classes:
                    input_df[col] = known_classes[0] 
                input_df[col] = encoders[col].transform(input_df[col])
                
            # 3. GET ML PROBABILITIES (The AI part)
            ml_probabilities = model.predict_proba(input_df[feature_names])[0]
            
            # 4. HYBRID FILTERING & SCORING (The Rule-Based part)
            scored_schemes = []
            
            for idx, scheme_name in enumerate(model_classes):
                if scheme_name == "Not Eligible / General Public":
                    continue
                    
                meta = scheme_metadata.get(scheme_name, {"domain": "Other", "priority": 1, "benefit": "Details pending"})
                
                # Filter by Domain
                if selected_domain != "All Domains" and meta["domain"] != selected_domain:
                    continue
                
                # Calculate Hybrid Score: (ML Confidence * 100) + Base Priority
                # This ensures the model's top mathematical pick stays high, but priority rules influence ties
                ml_confidence = ml_probabilities[idx]
                if ml_confidence > 0.01: # Only consider if ML thinks there is some chance
                    hybrid_score = (ml_confidence * 100) + meta["priority"]
                    scored_schemes.append({
                        "name": scheme_name,
                        "domain": meta["domain"],
                        "benefit": meta["benefit"],
                        "confidence": ml_confidence,
                        "score": hybrid_score
                    })
            
            # 5. Sort by Hybrid Score and get Top 3
            scored_schemes.sort(key=lambda x: x['score'], reverse=True)
            top_3 = scored_schemes[:3]
            
            # 6. Render Output
            for widget in result_frame.winfo_children():
                widget.destroy()
                
            if not top_3:
                tk.Label(result_frame, text="No eligible schemes found in this domain.", fg="#e74c3c", bg="white", font=("Arial", 11, "bold")).pack(pady=10)
            else:
                tk.Label(result_frame, text=f"🏆 Top {len(top_3)} AI-Prioritized Schemes:", fg="#27ae60", bg="white", font=("Arial", 12, "bold")).pack(pady=5)
                
                for i, scheme in enumerate(top_3, 1):
                    badge_color = ["#f1c40f", "#bdc3c7", "#cd7f32"][i-1] if i <= 3 else "#bdc3c7"
                    
                    frame = tk.Frame(result_frame, bg="white")
                    frame.pack(fill=tk.X, pady=4)
                    
                    tk.Label(frame, text=f"#{i}", font=("Arial", 11, "bold"), bg=badge_color, fg="black", width=3).pack(side=tk.LEFT, padx=5)
                    
                    text_frame = tk.Frame(frame, bg="white")
                    text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    tk.Label(text_frame, text=scheme['name'], font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=tk.X)
                    # Show the judge that the ML is working by displaying the ML Match Confidence
                    tk.Label(text_frame, text=f"Benefit: {scheme['benefit']} | ML Match: {scheme['confidence']:.0%}", font=("Arial", 9), bg="white", fg="#7f8c8d", anchor="w").pack(fill=tk.X)

        except Exception as e:
            messagebox.showerror("Error", f"Processing error: {str(e)}")

    tk.Button(root, text="Run Hybrid Eligibility Engine", font=("Arial", 12, "bold"), bg="#8e44ad", fg="white", command=process_hybrid_prediction, pady=10).pack(pady=10)
    
    result_frame = tk.Frame(root, bg="white", bd=2, relief=tk.GROOVE, padx=10, pady=10)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    root.mainloop()

# --- 4. EXECUTION ---
if __name__ == "__main__":
    trained_model, label_encoders, features_list, classes_list = train_hybrid_model()
    create_gui(trained_model, label_encoders, features_list, classes_list)