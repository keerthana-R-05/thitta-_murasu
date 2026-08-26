import pandas as pd
import pickle
import json
import os


def get_top_prioritized_schemes(
    sfdb_id,
    selected_domain,
    income,
    marital_status,
    disability_status
):
    """
    Takes user inputs, finds the citizen in the SFDB,
    runs the ML model, applies domain/priority rules,
    and returns the Top 3 schemes.
    """

    # ---------------------------------------------------------
    # BASE PROJECT PATH
    # ---------------------------------------------------------
    # eligibility_engine.py
    #        ↓
    # schemes_app
    #        ↓
    # Thittamurasu
    #        ↓
    # ThittaMurasu
    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    # ---------------------------------------------------------
    # FILE PATHS
    # ---------------------------------------------------------
    SFDB_PATH = os.path.join(
        BASE_DIR,
        "Thittamurasu",
        "sfdb_master_data.csv"
    )

    MODEL_PATH = os.path.join(
        BASE_DIR,
        "Thittamurasu",
        "thitta_murasu_model.pkl"
    )

    SCHEMES_PATH = os.path.join(
        BASE_DIR,
        "CODING",
        "TN_schemes_database.json"
    )

    # ---------------------------------------------------------
    # 1. LOAD SFDB DATABASE
    # ---------------------------------------------------------
    try:
        df = pd.read_csv(SFDB_PATH)
        print(f"SFDB loaded: {len(df)} records")
    except Exception as e:
        print(f"SFDB loading error: {e}")
        return {
            "error": "SFDB Database not found."
        }

    # ---------------------------------------------------------
    # FIND CITIZEN
    # ---------------------------------------------------------
    sfdb_id = str(sfdb_id).strip()

    # Convert both sides to string to avoid
    # number/string mismatch
    df["SFDB_ID"] = df["SFDB_ID"].astype(str).str.strip()

    citizen = df[df["SFDB_ID"] == sfdb_id]

    if citizen.empty:
        return {
            "error": f"SFDB ID '{sfdb_id}' not found in the state database."
        }

    # ---------------------------------------------------------
    # 2. EXTRACT STATIC DETAILS
    # ---------------------------------------------------------
    age = int(citizen["Age"].values[0])
    gender = citizen["Gender"].values[0]
    community = citizen["Community"].values[0]
    education = citizen["Education_Level"].values[0]
    occupation = citizen["Occupation"].values[0]

    profile = {
        "Age": age,
        "Gender": gender,
        "Community": community,
        "Education_Level": education,
        "Occupation": occupation,
        "Annual_Income": int(income),
        "Marital_Status": marital_status,
        "Disability_Status": int(disability_status)
    }

    # ---------------------------------------------------------
    # 3. LOAD ML MODEL
    # ---------------------------------------------------------
    try:
        with open(MODEL_PATH, "rb") as f:
            saved_data = pickle.load(f)

        rf_model = saved_data["model"]
        encoders = saved_data["encoders"]
        features = saved_data["features"]

    except Exception as e:
        print(f"Model loading error: {e}")
        return {
            "error": "Machine Learning model not found. Train it first."
        }

    # ---------------------------------------------------------
    # 4. PREPARE DATA FOR ML MODEL
    # ---------------------------------------------------------
    input_df = pd.DataFrame([profile])

    categorical_cols = [
        "Gender",
        "Community",
        "Education_Level",
        "Occupation",
        "Marital_Status"
    ]

    for col in categorical_cols:

        if col not in encoders:
            continue

        known_classes = list(encoders[col].classes_)
        val = input_df[col].values[0]

        if val not in known_classes:
            val = known_classes[0]

        input_df[col] = encoders[col].transform([val])

    # ---------------------------------------------------------
    # 5. ML PREDICTION
    # ---------------------------------------------------------
    try:
        ml_probabilities = rf_model.predict_proba(
            input_df[features]
        )[0]

        model_classes = rf_model.classes_

    except Exception as e:
        print(f"ML prediction error: {e}")
        return {
            "error": "Unable to generate eligibility prediction."
        }

    # ---------------------------------------------------------
    # 6. LOAD SCHEME RULEBOOK
    # ---------------------------------------------------------
    try:
        with open(
            SCHEMES_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            schemes_db = json.load(f)

    except Exception as e:
        print(f"Scheme database error: {e}")
        return {
            "error": "Schemes rulebook JSON not found."
        }

    scheme_lookup = {
        s["name"]: s
        for s in schemes_db
    }

    # ---------------------------------------------------------
    # 7. HYBRID FILTERING AND SCORING
    # ---------------------------------------------------------
    scored_schemes = []

    for idx, scheme_name in enumerate(model_classes):

        if scheme_name == "General Welfare / No Specific Scheme":
            continue

        meta = scheme_lookup.get(
            scheme_name,
            {}
        )

        if not meta:
            continue

        scheme_domain = meta.get(
            "domain",
            "Other"
        )

        base_priority = meta.get(
            "base_priority_weight",
            5
        )

        # Domain filtering
        if (
            selected_domain != "All Domains"
            and scheme_domain != selected_domain
        ):
            continue

        ml_confidence = ml_probabilities[idx]

        # Minimum confidence
        if ml_confidence > 0.02:

            dynamic_score = (
                ml_confidence * 100
            ) + base_priority

            # Low income bonus
            if profile["Annual_Income"] < 50000:
                dynamic_score += 3

            # Widow bonus
            if profile["Marital_Status"] == "Widow":
                dynamic_score += 2

            scored_schemes.append({
                "name": scheme_name,
                "domain": scheme_domain,
                "benefit": meta.get(
                    "benefit",
                    "Check portal for details."
                ),
                "confidence_score": round(
                    ml_confidence * 100,
                    1
                ),
                "final_priority": round(
                    dynamic_score,
                    1
                )
            })

    # ---------------------------------------------------------
    # 8. SORT AND RETURN TOP 3
    # ---------------------------------------------------------
    scored_schemes.sort(
        key=lambda x: x["final_priority"],
        reverse=True
    )

    top_3 = scored_schemes[:3]

    return {
        "status": "success",
        "results": top_3,
        "static_profile": profile
    }