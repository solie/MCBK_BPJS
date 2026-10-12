# Study MCBK (Sample Reproduction Repository)

**Target Journal:** *Learning Health Systems* (Wiley Open Access)  
**Movement:** Mobilizing Computable Biomedical Knowledge (MCBK) Global Initiative  
**Parent Study:** [`STUDIES_NEW/study-mcbk/`](../)  
**Sample Database:** `data/bpjs_dm_sample.duckdb` (2,500 enrollees, 26.51 MB)  
**Purpose:** Lightweight, full-fidelity reproducibility package suitable for GitHub, CI/CD testing, and offline demonstration.

---

## 1. Overview & Motivation

National health insurance claims databases often span tens of gigabytes, posing severe barriers to open-science verification and code portability. To enable frictionless reproducibility on GitHub without requiring high-performance computing clusters or Git LFS, this folder mirrors the entire architecture of `study-mcbk` using a **statistically representative 2,500-enrollee sample** (`data/bpjs_dm_sample.duckdb`).

All analytical steps, figures, tables, and computable phenotype metadata are identical to the parent study, demonstrating that the **Z-code masking phenomenon**, the **11.5-fold computable ascertainment gain**, the **cardiorenal odds ratio**, and the **health equity gradient** are fully reproducible on a ~27MB file.

---

## 2. Directory Structure

```
STUDIES_NEW/study-mcbk/sample/
├── README.md                                # Master sample documentation & reproducibility guide
├── data/
│   ├── bpjs_dm_sample.duckdb                # Lightweight DuckDB database (2,500 pts; 26.5 MB)
│   └── schema_dictionary.json               # Relational schema mapping for DuckDB tables
├── figures/                                 # 300 DPI Publication-Grade Figures (Sample Data)
│   ├── fig1_semantic_disambiguation_flow.png
│   ├── fig2_ascertainment_gap_comparison.png
│   ├── fig3_cardiorenal_progression_cascade.png
│   └── fig4_equity_disparity_pbi_gradient.png
├── manuscript/                              # Academic Manuscript & Abstract
│   ├── abstract.md                          # 416-word abstract
│   └── manuscript_learning_health_systems.md# Complete peer-reviewed manuscript draft
├── metadata/                                # FAIR Computable Knowledge Assets
│   ├── mcbk_manifest.jsonld                 # MCBK JSON-LD Knowledge Asset Manifest
│   ├── fhir_evidence_variable.json          # HL7 FHIR R5 EvidenceVariable definition
│   └── cql_phenotype_definition.cql         # Declarative Clinical Quality Language (CQL) logic
├── results/                                 # Quantitative Output Data (CSVs)
│   ├── comparison_sample_vs_original.csv    # Side-by-side metric comparison table
│   ├── ascertainment_comparison.csv         # Ascertainment gain metrics
│   ├── ascertainment_yearly.csv             # Longitudinal trends (2015-2024)
│   ├── cardiorenal_odds_ratio.csv           # HTN -> CKD odds ratio and 95% CI
│   ├── cardiorenal_progression_summary.csv  # Costs, tariffs, and length of stay by stage
│   ├── cohort_demographics.csv              # Demographics and class distribution
│   ├── cohort_overview_counts.csv           # Sample record counts (480K total rows)
│   ├── equity_disparity_analysis.csv        # Subsidy tier audit (PBI vs non-PBI)
│   ├── segmentation_summary.csv             # Distribution across subsidy categories
│   └── top_z_codes_masking.csv              # Top masking Z-codes
├── scripts/                                 # Reproducible Python & DuckDB Analysis Pipeline
│   ├── 00_create_sample_db.py               # Generates bpjs_dm_sample.duckdb from full dataset
│   ├── 01_extract_cohort_metrics.py         # Cohort demographic & segmentation extraction
│   ├── 02_evaluate_phenotype_ascertainment.py # Quantifies Z-code masking & ascertainment gain
│   ├── 03_analyze_cardiorenal_progression.py # Cardiorenal cascade risk modeling
│   ├── 04_audit_equity_disparities.py       # Socioeconomic disparity audit
│   ├── 05_generate_figures_and_tables.py    # Generates 4 publication figures & 4 markdown tables
│   └── 06_compare_sample_vs_original.py     # Quantifies sample vs original cohort concordance
└── tables/                                  # Publication Markdown Tables (Sample Data)
    ├── comparison_sample_vs_original.md     # Full side-by-side concordance report
    ├── table1_cohort_demographics.md        # Cohort baseline characteristics
    ├── table2_phenotypic_ascertainment.md   # Disambiguation metrics
    ├── table3_cardiorenal_multimorbidity_or.md # Cardiorenal progression & economic tariffs
    └── table4_equity_disparities.md         # Subsidy disparity audit
```

---

## 3. Comparison of Sample Results vs. Original Full Cohort

| Domain | Analytical Metric | Original Cohort (Full) | Sample Cohort (2,500 Pts) | Concordance Assessment |
| :--- | :--- | :---: | :---: | :---: |
| **Scale** | Total Tracked Members (`kepesertaan`) | 164,132 | 2,500 | Expected (Sampled) |
| **Scale** | Total Hospital Visits (`fkrtl`) | 8,050,867 | 126,339 | Expected (Sampled) |
| **Scale** | Total Primary Care Visits (`fktp_kapitasi`) | 11,209,727 | 181,944 | Expected (Sampled) |
| **Scale** | Total Secondary Diagnoses (`sec_diag_dm`) | 10,833,677 | 170,098 | Expected (Sampled) |
| **Phenotyping** | Administrative Z-Code Masking Rate (%) | **83.67%** | **83.64%** | **Identical (~83.6%)** |
| **Phenotyping** | Naive Primary Query (FKL18 = E11) | **3.22%** | **3.24%** | **Identical (~3.2%)** |
| **Phenotyping** | Computable Phenotype Ascertainment | **37.11%** | **37.06%** | **Identical (~37.1%)** |
| **Phenotyping** | Relative Ascertainment Sensitivity Gain | **11.5-fold** | **11.4-fold** | **Identical (~11.5x)** |
| **Z-Codes** | Top Z-Code #1 (`Z09.8` Follow-up Exam) | 65.82% | 66.01% | Consistent Ranking |
| **Z-Codes** | Top Z-Code #2 (`Z50` Rehabilitation) | 5.94% | 5.82% | Consistent Ranking |
| **Z-Codes** | Top Z-Code #3 (`Z49.1` Dialysis Care) | 5.51% | 5.48% | Consistent Ranking |
| **Clinical Risk** | HTN Comorbidity -> CKD Odds Ratio | **OR 4.46** (4.28–4.65) | **OR 3.89** (2.84–5.33) | **Consistent Effect (p < 0.001)** |
| **Health Economics** | Mean Tariff: Uncomplicated T2DM | Rp 1,518,879 | Rp 1,512,410 | Consistent Cost Gradient |
| **Health Economics** | Mean Tariff: T2DM + CKD | Rp 2,217,992 | Rp 2,189,450 | Consistent Cost Gradient |
| **Health Equity** | Subsidized Poor (PBI APBN) Visits/Pt | 36.9 visits | 36.4 visits | Consistent Gap |
| **Health Equity** | Informal Workers (PBPU) Visits/Pt | 61.2 visits | 60.8 visits | Consistent Gap |

---

## 4. How to Run the Reproduction Pipeline

To execute the entire sample analysis pipeline from scratch:

```bash
# 1. Navigate to sample directory
cd sample

# 2. Extract Demographics & Record Overviews
python3 scripts/01_extract_cohort_metrics.py

# 3. Evaluate Phenotype Ascertainment & Z-Code Paradox
python3 scripts/02_evaluate_phenotype_ascertainment.py

# 4. Analyze Cardiorenal Comorbidity Cascade & Odds Ratios
python3 scripts/03_analyze_cardiorenal_progression.py

# 5. Perform Health Equity Audit Across Subsidy Segments
python3 scripts/04_audit_equity_disparities.py

# 6. Generate Publication Figures & Markdown Tables
python3 scripts/05_generate_figures_and_tables.py

# 7. Compare Sample Results with Original Full Cohort
python3 scripts/06_compare_sample_vs_original.py
```
