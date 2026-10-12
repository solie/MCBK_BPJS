#!/usr/bin/env python3
"""
Study MCBK (Sample) - Script 02: Evaluate Phenotype Ascertainment and the Z-Code Phenomenon
Quantifies the semantic gap between naive billing queries and standardized computable phenotyping.
"""

import duckdb
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(SAMPLE_DIR, "data", "bpjs_dm_sample.duckdb")
OUT_DIR = os.path.join(SAMPLE_DIR, "results")
os.makedirs(OUT_DIR, exist_ok=True)

print(f"Connecting to sample database: {DB_PATH} for ascertainment evaluation...")
con = duckdb.connect(DB_PATH, read_only=True)

# 1. Overall Episode Ascertainment Comparison
print("Evaluating overall episode ascertainment (Sample)...")
overall_comparison = con.execute("""
    WITH episode_flags AS (
        SELECT 
            f.FKL02 AS episode_id,
            EXTRACT(YEAR FROM f.FKL03) AS service_year,
            CASE WHEN f.FKL18 LIKE 'E11%' THEN 1 ELSE 0 END AS naive_primary_e11,
            CASE WHEN f.FKL18 LIKE 'Z%' THEN 1 ELSE 0 END AS is_z_code,
            CASE WHEN f.FKL16 LIKE 'E11%' THEN 1 ELSE 0 END AS admission_e11,
            CASE WHEN s.e11_sec = 1 THEN 1 ELSE 0 END AS secondary_e11
        FROM fkrtl f
        LEFT JOIN (
            SELECT fkl02, 1 AS e11_sec 
            FROM sec_diag_dm 
            WHERE dx_code LIKE 'E11%' 
            GROUP BY fkl02
        ) s ON f.FKL02 = s.fkl02
    )
    SELECT 
        COUNT(*) AS total_episodes,
        SUM(naive_primary_e11) AS naive_primary_count,
        ROUND(100.0 * SUM(naive_primary_e11) / COUNT(*), 2) AS naive_primary_pct,
        SUM(is_z_code) AS z_code_primary_count,
        ROUND(100.0 * SUM(is_z_code) / COUNT(*), 2) AS z_code_primary_pct,
        SUM(admission_e11) AS admission_e11_count,
        ROUND(100.0 * SUM(admission_e11) / COUNT(*), 2) AS admission_e11_pct,
        SUM(secondary_e11) AS secondary_e11_count,
        ROUND(100.0 * SUM(secondary_e11) / COUNT(*), 2) AS secondary_e11_pct,
        COUNT(CASE WHEN admission_e11 = 1 OR secondary_e11 = 1 OR naive_primary_e11 = 1 THEN 1 END) AS computable_phenotype_count,
        ROUND(100.0 * COUNT(CASE WHEN admission_e11 = 1 OR secondary_e11 = 1 OR naive_primary_e11 = 1 THEN 1 END) / COUNT(*), 2) AS computable_phenotype_pct
    FROM episode_flags;
""").df()
overall_comparison.to_csv(f"{OUT_DIR}/ascertainment_comparison.csv", index=False)
print("Overall Ascertainment Comparison (Sample):\n", overall_comparison.T)

# 2. Ascertainment by Year (2015 - 2024)
print("Evaluating ascertainment trends by year (Sample)...")
yearly_ascertainment = con.execute("""
    WITH episode_flags AS (
        SELECT 
            f.FKL02 AS episode_id,
            EXTRACT(YEAR FROM f.FKL03) AS service_year,
            CASE WHEN f.FKL18 LIKE 'E11%' THEN 1 ELSE 0 END AS naive_primary_e11,
            CASE WHEN f.FKL18 LIKE 'Z%' THEN 1 ELSE 0 END AS is_z_code,
            CASE WHEN f.FKL16 LIKE 'E11%' THEN 1 ELSE 0 END AS admission_e11,
            CASE WHEN s.e11_sec = 1 THEN 1 ELSE 0 END AS secondary_e11
        FROM fkrtl f
        LEFT JOIN (
            SELECT fkl02, 1 AS e11_sec 
            FROM sec_diag_dm 
            WHERE dx_code LIKE 'E11%' 
            GROUP BY fkl02
        ) s ON f.FKL02 = s.fkl02
        WHERE EXTRACT(YEAR FROM f.FKL03) BETWEEN 2015 AND 2024
    )
    SELECT 
        service_year,
        COUNT(*) AS total_episodes,
        SUM(naive_primary_e11) AS naive_primary_count,
        ROUND(100.0 * SUM(naive_primary_e11) / COUNT(*), 2) AS naive_primary_pct,
        SUM(is_z_code) AS z_code_count,
        ROUND(100.0 * SUM(is_z_code) / COUNT(*), 2) AS z_code_pct,
        SUM(admission_e11) AS admission_e11_count,
        ROUND(100.0 * SUM(admission_e11) / COUNT(*), 2) AS admission_e11_pct,
        COUNT(CASE WHEN admission_e11 = 1 OR secondary_e11 = 1 OR naive_primary_e11 = 1 THEN 1 END) AS cbk_phenotype_count,
        ROUND(100.0 * COUNT(CASE WHEN admission_e11 = 1 OR secondary_e11 = 1 OR naive_primary_e11 = 1 THEN 1 END) / COUNT(*), 2) AS cbk_phenotype_pct
    FROM episode_flags
    GROUP BY service_year
    ORDER BY service_year;
""").df()
yearly_ascertainment.to_csv(f"{OUT_DIR}/ascertainment_yearly.csv", index=False)
print("Yearly Ascertainment Summary (Sample):\n", yearly_ascertainment[["service_year", "total_episodes", "naive_primary_pct", "z_code_pct", "cbk_phenotype_pct"]])

# 3. Top Z-Codes Masking Clinical Diagnoses
print("Identifying top Z-codes masking clinical diagnoses (Sample)...")
top_z_codes = con.execute("""
    SELECT 
        SUBSTRING(FKL18, 1, 3) AS z_code_3d,
        FKL18A AS diagnosis_name,
        COUNT(*) AS frequency,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fkrtl WHERE FKL18 LIKE 'Z%'), 2) AS pct_of_z_codes
    FROM fkrtl
    WHERE FKL18 LIKE 'Z%'
    GROUP BY SUBSTRING(FKL18, 1, 3), FKL18A
    ORDER BY frequency DESC
    LIMIT 10;
""").df()
top_z_codes.to_csv(f"{OUT_DIR}/top_z_codes_masking.csv", index=False)
print("Top Z-Codes (Sample):\n", top_z_codes)

con.close()
print("Script 02 completed successfully on sample data.")
