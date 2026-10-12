#!/usr/bin/env python3
"""
Study MCBK (Sample) - Script 04: Health Equity Disparity Audit Across BPJS Subsidies
Analyzes whether state-subsidized poor members (PBI) experience greater disease severity,
higher CKD complication burdens, and differential referral utilization compared to non-subsidized members.
"""

import duckdb
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(SAMPLE_DIR, "data", "bpjs_dm_sample.duckdb")
OUT_DIR = os.path.join(SAMPLE_DIR, "results")
os.makedirs(OUT_DIR, exist_ok=True)

print(f"Connecting to sample database: {DB_PATH} for health equity disparity audit...")
con = duckdb.connect(DB_PATH, read_only=True)

# 1. Equity metrics grouped by PSTV08 member segmentation
equity_metrics = con.execute("""
    WITH patient_level_complications AS (
        SELECT 
            f.PSTV01 AS patient_id,
            COUNT(DISTINCT f.FKL02) AS total_hospital_episodes,
            AVG(f.FKL22) AS avg_hospital_stay,
            AVG(f.FKL32) AS avg_hospital_cost,
            MAX(CASE WHEN f.FKL23 LIKE '%Berat%' THEN 1 ELSE 0 END) AS has_severe_episode,
            MAX(CASE WHEN f.FKL16 LIKE 'N18%' OR s.has_ckd = 1 THEN 1 ELSE 0 END) AS has_kidney_complication,
            MAX(CASE WHEN f.FKL16 LIKE 'I10%' OR f.FKL16 LIKE 'I11%' OR f.FKL16 LIKE 'I12%' OR f.FKL16 LIKE 'I13%' 
                          OR s.has_htn = 1 THEN 1 ELSE 0 END) AS has_hypertension
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
        k.PSTV08 AS member_segmentation,
        COUNT(DISTINCT k.PSTV01) AS total_patients,
        ROUND(100.0 * COUNT(CASE WHEN p.has_kidney_complication = 1 THEN 1 END) / COUNT(*), 2) AS ckd_prevalence_pct,
        ROUND(100.0 * COUNT(CASE WHEN p.has_hypertension = 1 THEN 1 END) / COUNT(*), 2) AS htn_prevalence_pct,
        ROUND(100.0 * COUNT(CASE WHEN p.has_severe_episode = 1 THEN 1 END) / COUNT(*), 2) AS severe_episode_pct,
        ROUND(AVG(p.avg_hospital_stay), 2) AS mean_length_of_stay,
        ROUND(AVG(p.avg_hospital_cost), 0) AS mean_hospital_cost_idr,
        ROUND(AVG(p.total_hospital_episodes), 1) AS mean_episodes_per_patient
    FROM kepesertaan k
    LEFT JOIN patient_level_complications p ON k.PSTV01 = p.patient_id
    WHERE k.PSTV08 IN ('PBI APBN', 'PBI APBD', 'PBPU', 'PPU', 'BUKAN PEKERJA')
    GROUP BY k.PSTV08
    ORDER BY ckd_prevalence_pct DESC;
""").df()

equity_metrics.to_csv(f"{OUT_DIR}/equity_disparity_analysis.csv", index=False)
print("Equity Disparity Analysis (Sample):\n", equity_metrics)

con.close()
print("Script 04 completed successfully on sample data.")
