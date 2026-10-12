#!/usr/bin/env python3
"""
Script: 00_create_sample_db.py
Purpose: Generate a lightweight, representative sample DuckDB database (2,500 patients, ~27MB)
         from bpjs_dm_2015_2024.duckdb for GitHub reproducibility and offline testing.
"""

import duckdb
import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.abspath(os.path.join(script_dir, ".."))
    root_dir = os.path.abspath(os.path.join(sample_dir, "..", ".."))
    
    src_db = os.path.join(root_dir, "bpjs_dm_2015_2024.duckdb")
    if not os.path.exists(src_db):
        src_db = os.path.abspath("bpjs_dm_2015_2024.duckdb")
        
    dest_db = os.path.join(sample_dir, "data", "bpjs_dm_sample.duckdb")
    
    print("================================================================================")
    print("CREATING LIGHTWEIGHT REPRODUCIBILITY SAMPLE DATABASE")
    print("================================================================================")
    print(f"Source Database: {src_db}")
    print(f"Target Database: {dest_db}")
    
    if os.path.exists(dest_db):
        print(f"Removing existing target file: {dest_db}")
        os.remove(dest_db)
        
    os.makedirs(os.path.dirname(dest_db), exist_ok=True)
    
    dest_con = duckdb.connect(dest_db)
    dest_con.execute(f"ATTACH '{src_db}' AS src (READ_ONLY);")
    
    # 1. Sample 2,500 patients using fixed seed 42
    print("Sampling 2,500 members from kepesertaan (seed 42)...")
    dest_con.execute("""
        CREATE TABLE kepesertaan AS 
        SELECT * FROM src.kepesertaan 
        USING SAMPLE 2500 (reservoir, 42);
    """)
    n_pts = dest_con.execute("SELECT COUNT(*) FROM kepesertaan;").fetchone()[0]
    print(f"  kepesertaan sampled: {n_pts:,} rows")
    
    # 2. Extract matching hospital episodes
    print("Extracting corresponding hospital episodes (fkrtl)...")
    dest_con.execute("""
        CREATE TABLE fkrtl AS 
        SELECT * FROM src.fkrtl 
        WHERE PSTV01 IN (SELECT PSTV01 FROM kepesertaan);
    """)
    n_fkrtl = dest_con.execute("SELECT COUNT(*) FROM fkrtl;").fetchone()[0]
    print(f"  fkrtl extracted: {n_fkrtl:,} rows")
    
    # 3. Extract matching primary care encounters
    print("Extracting corresponding primary care visits (fktp_kapitasi)...")
    dest_con.execute("""
        CREATE TABLE fktp_kapitasi AS 
        SELECT * FROM src.fktp_kapitasi 
        WHERE PSTV01 IN (SELECT PSTV01 FROM kepesertaan);
    """)
    n_fktp = dest_con.execute("SELECT COUNT(*) FROM fktp_kapitasi;").fetchone()[0]
    print(f"  fktp_kapitasi extracted: {n_fktp:,} rows")
    
    # 4. Extract matching secondary diagnosis records
    print("Extracting corresponding secondary diagnoses (sec_diag_dm)...")
    dest_con.execute("""
        CREATE TABLE sec_diag_dm AS 
        SELECT * FROM src.sec_diag_dm 
        WHERE fkl02 IN (SELECT FKL02 FROM fkrtl);
    """)
    n_sec = dest_con.execute("SELECT COUNT(*) FROM sec_diag_dm;").fetchone()[0]
    print(f"  sec_diag_dm extracted: {n_sec:,} rows")
    
    dest_con.execute("DETACH src;")
    dest_con.execute("CHECKPOINT;")
    dest_con.close()
    
    size_mb = os.path.getsize(dest_db) / (1024 * 1024)
    print("================================================================================")
    print(f"Sample Database Created Successfully!")
    print(f"File Path: {dest_db}")
    print(f"File Size: {size_mb:.2f} MB (GitHub friendly < 50MB)")
    print(f"Total Rows: {n_pts + n_fkrtl + n_fktp + n_sec:,}")
    print("================================================================================\n")

if __name__ == "__main__":
    main()
