import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

# --- 1. MODEL TRAINING PHASE ---
def train_model():
    print("Loading dataset and training model...")
    file_path = 'D:\SA hackathon\CODING\Tn_rural_schemes_10k_v2.csv'
    
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"Dataset '{file_path}' not found! Please run the dataset generator first.")
        return None, None, None
        
    df = pd.read_csv(file_path)
    
    # Features and Target
    features = [
        'Age', 'Gender', 'Community', 'Annual_Income', 'Ration_Card_Type',
        'Education_Level', 'Occupation', 'Land_Holding_Acres', 'Marital_Status', 
        'Disability_Status', 'SHG_Member'
    ]
    target = 'Eligible_Scheme'
    
    X = df[features].copy()
    y = df[target]
    
    # Encode categorical variables
    encoders = {}
    categorical_cols = ['Gender', 'Community', 'Ration_Card_Type', 'Education_Level', 'Occupation', 'Marital_Status']
    
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    # Train Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    print("Model training complete!")
    return rf_model, encoders, features

# --- 2. GUI APPLICATION PHASE ---
def create_gui(model, encoders, feature_names):
    if model is None:
        return
        
    root = tk.Tk()
    root.title("Thitta-Murasu: Eligibility Dashboard")
    root.geometry("600x700")
    root.configure(bg="#f4f6f9")
    
    # Styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TLabel", background="#f4f6f9", font=("Arial", 11))
    style.configure("TButton", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white")
    
    # Header
    # header = tk.Label(root, text="கிராம-இணைப்பு (Grama-Connect)", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=10)
    # header.pack(fill=tk.X)
    
    subheader = tk.Label(root, text="Citizen Scheme Eligibility Portal", font=("Arial", 12), bg="#34495e", fg="white", pady=5)
    subheader.pack(fill=tk.X)
    
    # Form Frame
    form_frame = tk.Frame(root, bg="#f4f6f9", padx=20, pady=20)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    # Input Variables
    inputs = {}
    row_idx = 0
    
    def add_entry(label_text, var_name):
        nonlocal row_idx
        ttk.Label(form_frame, text=label_text).grid(row=row_idx, column=0, sticky="w", pady=5)
        entry = ttk.Entry(form_frame, width=30)
        entry.grid(row=row_idx, column=1, pady=5, padx=10)
        inputs[var_name] = entry
        row_idx += 1
        
    def add_dropdown(label_text, var_name, options):
        nonlocal row_idx
        ttk.Label(form_frame, text=label_text).grid(row=row_idx, column=0, sticky="w", pady=5)
        combo = ttk.Combobox(form_frame, values=options, state="readonly", width=28)
        combo.current(0)
        combo.grid(row=row_idx, column=1, pady=5, padx=10)
        inputs[var_name] = combo
        row_idx += 1

    # Form Fields
    add_entry("Age (Years):", "Age")
    add_dropdown("Gender:", "Gender", ["Male", "Female"])
    add_dropdown("Community:", "Community", ["BC", "MBC", "SC", "ST", "General"])
    add_entry("Annual Income (₹):", "Annual_Income")
    add_dropdown("Ration Card Type:", "Ration_Card_Type", ["PHH", "AAY", "NPHH"])
    add_dropdown("Education Level:", "Education_Level", ["Illiterate", "8th Pass", "10th Pass", "12th Pass", "Diploma", "Graduate"])
    add_dropdown("Occupation:", "Occupation", ["Agriculture", "Daily Wage", "Weaver", "Unemployed", "Self-Employed", "Student"])
    add_entry("Land Holding (Acres):", "Land_Holding_Acres")
    add_dropdown("Marital Status:", "Marital_Status", ["Single", "Married", "Widow", "Separated"])
    add_dropdown("Disability Status:", "Disability_Status", ["No", "Yes"])
    add_dropdown("SHG Member (Mahalir Thittam):", "SHG_Member", ["No", "Yes"])
    
    # Prediction Function
    def predict_eligibility():
        try:
            # 1. Gather data from GUI
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
            
            # 2. Format as DataFrame
            input_df = pd.DataFrame([data])
            
            # 3. Apply Encoders
            categorical_cols = ['Gender', 'Community', 'Ration_Card_Type', 'Education_Level', 'Occupation', 'Marital_Status']
            for col in categorical_cols:
                # Handle unseen labels just in case
                known_classes = list(encoders[col].classes_)
                if input_df[col][0] not in known_classes:
                    input_df[col] = known_classes[0] # Fallback to first class
                input_df[col] = encoders[col].transform(input_df[col])
                
            # 4. Predict
            prediction = model.predict(input_df[feature_names])[0]
            
            # 5. Display Result
            result_label.config(text=f"✅ Eligible Scheme:\n{prediction}", fg="#27ae60")
            
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure Age, Income, and Land Holding are numeric values.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Predict Button
    predict_btn = tk.Button(root, text="Check Eligibility & Notify", font=("Arial", 12, "bold"), bg="#e67e22", fg="white", command=predict_eligibility, pady=10)
    predict_btn.pack(pady=15)
    
    # Result Display
    result_frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE)
    result_frame.pack(fill=tk.X, padx=20, pady=10)
    
    result_label = tk.Label(result_frame, text="Enter details and click Predict", font=("Arial", 14, "bold"), bg="#ffffff", fg="#7f8c8d", pady=20)
    result_label.pack()

    root.mainloop()

# --- 3. EXECUTION ---
if __name__ == "__main__":
    trained_model, label_encoders, features_list = train_model()
    create_gui(trained_model, label_encoders, features_list)