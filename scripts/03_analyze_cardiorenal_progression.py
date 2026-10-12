#!/usr/bin/env python3
"""
Study MCBK (Sample) - Script 03: Cardiorenal Multimorbidity Progression Cascade
Analyzes clinical progression from uncomplicated T2DM to hypertensive cardiorenal disease and end-stage CKD.
"""

import duckdb
import pandas as pd
import numpy as np
import scipy.stats as stats
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(SAMPLE_DIR, "data", "bpjs_dm_sample.duckdb")
OUT_DIR = os.path.join(SAMPLE_DIR, "results")
os.makedirs(OUT_DIR, exist_ok=True)

print(f"Connecting to sample database: {DB_PATH} for cardiorenal analysis...")
con = duckdb.connect(DB_PATH, read_only=True)

# 1. Comorbidity Prevalence and Resource Utilization by Complication Status
print("Extracting complication status and health economic utilization (Sample)...")
complication_stats = con.execute("""
    WITH episode_complications AS (
        SELECT 
            f.FKL02 AS episode_id,
            f.PSTV01 AS patient_id,
            f.FKL22 AS length_of_stay,
            f.FKL23 AS severity,
            f.FKL32 AS tariff_idr,
            -- Complication Indicators across admission (FKL16) and secondary (sec_diag)
            CASE WHEN (f.FKL16 LIKE 'I10%' OR f.FKL16 LIKE 'I11%' OR f.FKL16 LIKE 'I12%' OR f.FKL16 LIKE 'I13%')
                      OR s.has_htn = 1 THEN 1 ELSE 0 END AS has_hypertension,
            CASE WHEN f.FKL16 LIKE 'N18%' OR s.has_ckd = 1 THEN 1 ELSE 0 END AS has_ckd,
            CASE WHEN (f.FKL16 LIKE 'I12%' OR f.FKL16 LIKE 'I13%') 
                      OR (has_hypertension = 1 AND has_ckd = 1) THEN 1 ELSE 0 END AS has_cardiorenal_syndrome
        FROM fkrtl f
        LEFT JOIN (
            SELECT 
                fkl02,
                MAX(CASE WHEN dx_code LIKE 'I10%' OR dx_code LIKE 'I11%' OR dx_code LIKE 'I12%' OR dx_code LIKE 'I13%' THEN 1 ELSE 0 END) AS has_htn,
                MAX(CASE WHEN dx_code LIKE 'N18%' THEN 1 ELSE 0 END) AS has_ckd
            FROM sec_diag_dm
            GROUP BY fkl02
        ) s ON f.FKL02 = s.fkl02
    )
    SELECT 
        CASE 
            WHEN has_cardiorenal_syndrome = 1 THEN 'T2DM + Cardiorenal Syndrome (HTN & CKD)'
            WHEN has_ckd = 1 THEN 'T2DM + Chronic Kidney Disease'
            WHEN has_hypertension = 1 THEN 'T2DM + Hypertension Alone'
            ELSE 'T2DM Uncomplicated / Other'
        END AS clinical_category,
        COUNT(*) AS episode_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fkrtl), 2) AS episode_pct,
        ROUND(AVG(length_of_stay), 2) AS avg_length_of_stay,
        ROUND(AVG(tariff_idr), 0) AS avg_tariff_idr,
        ROUND(MEDIAN(tariff_idr), 0) AS median_tariff_idr,
        ROUND(100.0 * COUNT(CASE WHEN severity LIKE '%Berat%' THEN 1 END) / COUNT(*), 2) AS severe_case_pct
    FROM episode_complications
    GROUP BY clinical_category
    ORDER BY avg_tariff_idr DESC;
""").df()
complication_stats.to_csv(f"{OUT_DIR}/cardiorenal_progression_summary.csv", index=False)
print("Complication Progression Summary (Sample):\n", complication_stats)

# 2. Risk Odds Ratios for Developing End-Stage CKD (N18)
print("Computing patient-level odds ratios for cardiorenal progression (Sample)...")
patient_risk = con.execute("""
    WITH patient_level AS (
        SELECT 
            f.PSTV01 AS patient_id,
            MAX(CASE WHEN f.FKL16 LIKE 'I10%' OR f.FKL16 LIKE 'I11%' OR f.FKL16 LIKE 'I12%' OR f.FKL16 LIKE 'I13%' 
                          OR s.has_htn = 1 THEN 1 ELSE 0 END) AS exposed_htn,
            MAX(CASE WHEN f.FKL16 LIKE 'N18%' OR s.has_ckd = 1 THEN 1 ELSE 0 END) AS outcome_ckd
        FROM fkrtl f
        LEFT JOIN (
            SELECT 
                fkl02,
                MAX(CASE WHEN dx_code LIKE 'I10%' OR dx_code LIKE 'I11%' OR dx_code LIKE 'I12%' OR dx_code LIKE 'I13%' THEN 1 ELSE 0 END) AS has_htn,
                MAX(CASE WHEN dx_code LIKE 'N18%' THEN 1 ELSE 0 END) AS has_ckd
            FROM sec_diag_dm
            GROUP BY fkl02
        ) s ON f.FKL02 = s.fkl02
        GROUP BY f.PSTV01
    )
    SELECT 
        exposed_htn,
        outcome_ckd,
        COUNT(*) AS patient_count
    FROM patient_level
    GROUP BY exposed_htn, outcome_ckd;
""").df()

contingency = patient_risk.pivot(index="exposed_htn", columns="outcome_ckd", values="patient_count").fillna(0)
print("Contingency Matrix (HTN vs CKD, Sample):\n", contingency)

try:
    a = contingency.loc[1, 1]
    b = contingency.loc[1, 0]
    c = contingency.loc[0, 1]
    d = contingency.loc[0, 0]
    
    odds_ratio, p_value = stats.fisher_exact([[a, b], [c, d]])
    log_or = np.log(odds_ratio)
    se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d)
    ci_lower = np.exp(log_or - 1.96 * se_log_or)
    ci_upper = np.exp(log_or + 1.96 * se_log_or)
    
    or_df = pd.DataFrame([{
        "exposure": "Hypertension (I10-I13)",
        "outcome": "Chronic Kidney Disease (N18)",
        "cases_exposed": int(a),
        "controls_exposed": int(b),
        "cases_unexposed": int(c),
        "controls_unexposed": int(d),
        "odds_ratio": round(odds_ratio, 2),
        "ci_lower_95": round(ci_lower, 2),
        "ci_upper_95": round(ci_upper, 2),
        "p_value": p_value
    }])
    or_df.to_csv(f"{OUT_DIR}/cardiorenal_odds_ratio.csv", index=False)
    print("Odds Ratio Analysis (Sample):\n", or_df.T)
except Exception as e:
    print("Contingency calculation warning:", e)

con.close()
print("Script 03 completed successfully on sample data.")
