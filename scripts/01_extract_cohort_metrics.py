#!/usr/bin/env python3
"""
Study MCBK (Sample) - Script 01: Extract Cohort Demographics and Summary Metrics
Database: bpjs_dm_sample.duckdb (2,500 patient sample)
"""

import duckdb
import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DB_PATH = os.path.join(SAMPLE_DIR, "data", "bpjs_dm_sample.duckdb")
OUT_DIR = os.path.join(SAMPLE_DIR, "results")
os.makedirs(OUT_DIR, exist_ok=True)

print(f"Connecting to sample database: {DB_PATH}...")
con = duckdb.connect(DB_PATH, read_only=True)

# 1. Total summary counts
summary_counts = con.execute("""
    SELECT 
        (SELECT COUNT(*) FROM kepesertaan) AS total_members,
        (SELECT COUNT(*) FROM fkrtl) AS total_fkrtl_episodes,
        (SELECT COUNT(*) FROM fktp_kapitasi) AS total_fktp_kapitasi,
        (SELECT COUNT(*) FROM sec_diag_dm) AS total_sec_diagnoses
""").df()
summary_counts.to_csv(f"{OUT_DIR}/cohort_overview_counts.csv", index=False)
print("Overview Counts (Sample):\n", summary_counts)

# 2. Member Demographics (PSTV05 Gender, PSTV08 Segmentation, PSTV07 Class)
demographics = con.execute("""
    SELECT 
        CASE PSTV05 
            WHEN '1' THEN 'Male'
            WHEN '2' THEN 'Female'
            ELSE 'Unknown'
        END AS gender,
        PSTV08 AS member_segmentation,
        PSTV07 AS treatment_class,
        COUNT(*) AS member_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
    FROM kepesertaan
    GROUP BY PSTV05, PSTV08, PSTV07
    ORDER BY member_count DESC;
""").df()
demographics.to_csv(f"{OUT_DIR}/cohort_demographics.csv", index=False)
print(f"Demographics extracted ({len(demographics)} rows).")

# 3. Aggregated Segmentation Summary
segmentation_summary = con.execute("""
    SELECT 
        PSTV08 AS segmentation,
        COUNT(*) AS total_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM kepesertaan), 2) AS pct_of_cohort
    FROM kepesertaan
    GROUP BY PSTV08
    ORDER BY total_count DESC;
""").df()
segmentation_summary.to_csv(f"{OUT_DIR}/segmentation_summary.csv", index=False)
print("Segmentation Summary (Sample):\n", segmentation_summary)

con.close()
print("Script 01 completed successfully on sample data.")
