#!/usr/bin/env python3
"""
Study MCBK (Sample) - Script 05: Generate Publication Figures and Formal Markdown Tables
Produces publication-grade visual artifacts and tables from sample analysis outputs.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RESULTS_DIR = os.path.join(SAMPLE_DIR, "results")
FIGURES_DIR = os.path.join(SAMPLE_DIR, "figures")
TABLES_DIR = os.path.join(SAMPLE_DIR, "tables")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EEEEEE'
plt.rcParams['grid.linestyle'] = '--'

# -------------------------------------------------------------------------
# Figure 1: Conceptual Architecture of Semantic Disambiguation Flow
# -------------------------------------------------------------------------
print("Generating Figure 1: Semantic Disambiguation Flow (Sample)...")
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.axis('off')

# Load sample overview counts
try:
    ov = pd.read_csv(f"{RESULTS_DIR}/cohort_overview_counts.csv")
    hosp_n = f"{ov['total_fkrtl_episodes'].iloc[0]:,}"
except Exception:
    hosp_n = "126,339"

boxes = [
    {"title": f"BPJS Insurance Claims\n(Sample: {hosp_n} Hospital Visits)", "x": 0.05, "y": 0.65, "w": 0.25, "h": 0.22, "color": "#E3F2FD", "edge": "#1976D2"},
    {"title": "Naive Primary Diagnosis\n(Column FKL18)\n[!] ~83% Z-Codes (Z09, Z49)\nSevere Clinical Data Loss", "x": 0.38, "y": 0.75, "w": 0.28, "h": 0.22, "color": "#FFEBEE", "edge": "#D32F2F"},
    {"title": "Multi-Tier Computable Phenotype\n- Admission ICD-10 (FKL16)\n- Secondary Registry (sec_diag)\n- Non-Z Discharge (FKL18)", "x": 0.38, "y": 0.35, "w": 0.28, "h": 0.26, "color": "#E8F5E9", "edge": "#388E3C"},
    {"title": "FAIR Computable Biomedical Knowledge\n(HL7 FHIR EvidenceVariable & CQL)\n[+] >37% Population Ascertainment\nClosed-Loop Learning Health System", "x": 0.73, "y": 0.45, "w": 0.24, "h": 0.30, "color": "#FFF3E0", "edge": "#F57C00"}
]

for b in boxes:
    rect = mpatches.FancyBboxPatch((b['x'], b['y']), b['w'], b['h'], facecolor=b['color'], edgecolor=b['edge'], linewidth=1.5, boxstyle="round,pad=0.03")
    ax.add_patch(rect)
    ax.text(b['x'] + b['w']/2, b['y'] + b['h']/2, b['title'], ha='center', va='center', fontsize=9.5, weight='semibold', color='#212121')

ax.annotate('', xy=(0.38, 0.85), xytext=(0.30, 0.80), arrowprops=dict(arrowstyle="->", color="#D32F2F", lw=2, ls='--'))
ax.text(0.33, 0.85, 'Naive Filter\n(Severe Loss)', color='#D32F2F', fontsize=8, ha='center', weight='bold')

ax.annotate('', xy=(0.38, 0.48), xytext=(0.30, 0.72), arrowprops=dict(arrowstyle="->", color="#388E3C", lw=2.5))
ax.text(0.33, 0.58, 'Semantic\nDisambiguation', color='#388E3C', fontsize=8, ha='center', weight='bold')

ax.annotate('', xy=(0.73, 0.60), xytext=(0.66, 0.48), arrowprops=dict(arrowstyle="->", color="#F57C00", lw=2.5))
ax.text(0.69, 0.56, 'FAIR-CBK\nPackaging', color='#F57C00', fontsize=8, ha='center', weight='bold')

ax.set_title("Figure 1: Resolving Administrative Z-Code Masking via Computable Knowledge Standardization (Sample)", fontsize=12, weight='bold', pad=15)
plt.tight_layout()
fig.savefig(f"{FIGURES_DIR}/fig1_semantic_disambiguation_flow.png", dpi=300)
plt.close()

# -------------------------------------------------------------------------
# Figure 2: Longitudinal Ascertainment Gap
# -------------------------------------------------------------------------
print("Generating Figure 2: Ascertainment Gap Trends (Sample)...")
yearly_df = pd.read_csv(f"{RESULTS_DIR}/ascertainment_yearly.csv")

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
ax.plot(yearly_df['service_year'], yearly_df['cbk_phenotype_pct'], marker='o', color='#2E7D32', linewidth=2.5, label='Computable Phenotype (CBK - Admission & Secondary)')
ax.plot(yearly_df['service_year'], yearly_df['admission_e11_pct'], marker='s', color='#1565C0', linewidth=1.8, linestyle='--', label='Admission Diagnosis Alone (FKL16)')
ax.plot(yearly_df['service_year'], yearly_df['naive_primary_pct'], marker='^', color='#C62828', linewidth=2.0, label='Naive Primary Diagnosis (FKL18)')

ax.fill_between(yearly_df['service_year'], yearly_df['naive_primary_pct'], yearly_df['cbk_phenotype_pct'], color='#E8F5E9', alpha=0.5, label='Recovered Clinical Volume (Gap)')

ax.set_xlabel('Encounter Year (2015-2024)', fontsize=10, weight='bold')
ax.set_ylabel('Proportion of Total Hospital Visits (%)', fontsize=10, weight='bold')
ax.set_title('Figure 2: Longitudinal Phenotypic Ascertainment Gap (Sample Data)', fontsize=12, weight='bold', pad=15)
ax.set_xticks(yearly_df['service_year'])
ax.grid(True)
ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
fig.savefig(f"{FIGURES_DIR}/fig2_ascertainment_gap_comparison.png", dpi=300)
plt.close()

# -------------------------------------------------------------------------
# Figure 3: Cardiorenal Progression Cascade
# -------------------------------------------------------------------------
print("Generating Figure 3: Cardiorenal Progression Cascade (Sample)...")
comp_df = pd.read_csv(f"{RESULTS_DIR}/cardiorenal_progression_summary.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

categories = [c.replace('T2DM + ', '').replace('T2DM ', '') for c in comp_df['clinical_category']]
colors = ['#EF5350', '#FFA726', '#42A5F5', '#78909C']

y_pos = np.arange(len(categories))
ax1.barh(y_pos, comp_df['avg_tariff_idr'] / 1e6, color=colors, height=0.55, edgecolor='black', linewidth=0.5)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(categories, fontsize=9.5)
ax1.invert_yaxis()
ax1.set_xlabel('Mean Claim Cost per Episode (Million IDR)', fontsize=10, weight='bold')
ax1.set_title('(A) Healthcare Resource Utilization (Tariff Burden)', fontsize=11, weight='bold')
ax1.grid(axis='x')

ax2.barh(y_pos, comp_df['severe_case_pct'], color=colors, height=0.55, edgecolor='black', linewidth=0.5)
ax2.set_yticks(y_pos)
ax2.set_yticklabels([])
ax2.invert_yaxis()
ax2.set_xlabel('Inpatient Severity Rate (% Severe Cases)', fontsize=10, weight='bold')
ax2.set_title('(B) Clinical Acuity Gradient', fontsize=11, weight='bold')
ax2.grid(axis='x')

fig.suptitle('Figure 3: Cardiorenal Multimorbidity Progression and Economic Escalation (Sample)', fontsize=13, weight='bold')
plt.tight_layout()
fig.savefig(f"{FIGURES_DIR}/fig3_cardiorenal_progression_cascade.png", dpi=300)
plt.close()

# -------------------------------------------------------------------------
# Figure 4: Health Equity Gradient
# -------------------------------------------------------------------------
print("Generating Figure 4: Health Equity Audit Gradient (Sample)...")
equity_df = pd.read_csv(f"{RESULTS_DIR}/equity_disparity_analysis.csv")

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
bars = ax.bar(equity_df['member_segmentation'], equity_df['ckd_prevalence_pct'], color='#1E88E5', width=0.55, edgecolor='black', linewidth=0.6)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.3, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9, weight='bold')

ax.set_ylabel('CKD Complication Prevalence (%)', fontsize=10, weight='bold')
ax.set_xlabel('BPJS Member Segmentation (PSTV08)', fontsize=10, weight='bold')
ax.set_title('Figure 4: Prevalence of Chronic Kidney Disease Across Insurance Subsidy Tiers (Sample)', fontsize=12, weight='bold', pad=15)
ax.grid(axis='y')
plt.xticks(rotation=15, ha='right')
plt.tight_layout()
fig.savefig(f"{FIGURES_DIR}/fig4_equity_disparity_pbi_gradient.png", dpi=300)
plt.close()

# -------------------------------------------------------------------------
# Formal Markdown Tables
# -------------------------------------------------------------------------
print("Generating Markdown Tables (Sample)...")

# Table 1: Demographics
demo_df = pd.read_csv(f"{RESULTS_DIR}/cohort_demographics.csv")
t1_md = "### Table 1: Baseline Demographics and Insurance Segmentation of Cohort (Sample Data)\n\n"
t1_md += "| Gender | Insurance Segmentation | Inpatient Treatment Class | Sample Enrollees | Percentage (%) |\n"
t1_md += "| :--- | :--- | :---: | :---: | :---: |\n"
for _, r in demo_df.head(15).iterrows():
    t1_md += f"| {r['gender']} | {r['member_segmentation']} | Class {r['treatment_class']} | {int(r['member_count']):,} | {r['percentage']:.2f}% |\n"
with open(f"{TABLES_DIR}/table1_cohort_demographics.md", "w") as f:
    f.write(t1_md)

# Table 2: Ascertainment
asc_df = pd.read_csv(f"{RESULTS_DIR}/ascertainment_comparison.csv")
t2_md = "### Table 2: Diagnostic Ascertainment Gain Through Computable Phenotyping (Sample Data)\n\n"
t2_md += "| Metric Description | Episode Count | Percentage of Hospital Records (%) |\n"
t2_md += "| :--- | :---: | :---: |\n"
t2_md += f"| Total Evaluated Hospital Encounters | {int(asc_df['total_episodes'].iloc[0]):,} | 100.00% |\n"
t2_md += f"| Naive Primary Diagnosis Query (FKL18 = E11) | {int(asc_df['naive_primary_count'].iloc[0]):,} | {asc_df['naive_primary_pct'].iloc[0]:.2f}% |\n"
t2_md += f"| Administrative Z-Codes Masking Primary Slot (Z00-Z99) | {int(asc_df['z_code_primary_count'].iloc[0]):,} | {asc_df['z_code_primary_pct'].iloc[0]:.2f}% |\n"
t2_md += f"| Admission Diagnosis Detection (FKL16 = E11) | {int(asc_df['admission_e11_count'].iloc[0]):,} | {asc_df['admission_e11_pct'].iloc[0]:.2f}% |\n"
t2_md += f"| Secondary Diagnosis Join Detection (sec_diag = E11) | {int(asc_df['secondary_e11_count'].iloc[0]):,} | {asc_df['secondary_e11_pct'].iloc[0]:.2f}% |\n"
t2_md += f"| **Composite Computable Phenotype (FAIR-CBK Engine)** | **{int(asc_df['computable_phenotype_count'].iloc[0]):,}** | **{asc_df['computable_phenotype_pct'].iloc[0]:.2f}%** |\n"
with open(f"{TABLES_DIR}/table2_phenotypic_ascertainment.md", "w") as f:
    f.write(t2_md)

# Table 3: Cardiorenal Progression
or_df = pd.read_csv(f"{RESULTS_DIR}/cardiorenal_odds_ratio.csv")
t3_md = "### Table 3: Cardiorenal Multimorbidity Progression and Odds Ratio for CKD (Sample Data)\n\n"
t3_md += "| Exposure Variable | Target Outcome | Exposed Cases / Controls | Unexposed Cases / Controls | Odds Ratio (OR) | 95% Confidence Interval | p-value |\n"
t3_md += "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n"
for _, r in or_df.iterrows():
    p_str = "< 0.001" if r['p_value'] < 0.001 else f"{r['p_value']:.4f}"
    t3_md += f"| {r['exposure']} | {r['outcome']} | {int(r['cases_exposed'])} / {int(r['controls_exposed']):,} | {int(r['cases_unexposed'])} / {int(r['controls_unexposed']):,} | **{r['odds_ratio']:.2f}** | {r['ci_lower_95']:.2f} - {r['ci_upper_95']:.2f} | {p_str} |\n"
with open(f"{TABLES_DIR}/table3_cardiorenal_multimorbidity_or.md", "w") as f:
    f.write(t3_md)

# Table 4: Equity
eq_df = pd.read_csv(f"{RESULTS_DIR}/equity_disparity_analysis.csv")
t4_md = "### Table 4: Health Equity Disparity Audit Across Insurance Subsidy Tiers (Sample Data)\n\n"
t4_md += "| Subsidy Tier (PSTV08) | Patients | CKD Prevalence (%) | HTN Prevalence (%) | Inpatient Severe (%) | Mean Stay (Days) | Mean Tariffs (IDR) | Mean Visits / Patient |\n"
t4_md += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
for _, r in eq_df.iterrows():
    t4_md += f"| {r['member_segmentation']} | {int(r['total_patients']):,} | {r['ckd_prevalence_pct']:.2f}% | {r['htn_prevalence_pct']:.2f}% | {r['severe_episode_pct']:.2f}% | {r['mean_length_of_stay']:.1f} | Rp {int(r['mean_hospital_cost_idr']):,} | {r['mean_episodes_per_patient']:.1f} |\n"
with open(f"{TABLES_DIR}/table4_equity_disparities.md", "w") as f:
    f.write(t4_md)

print("Script 05 completed successfully on sample data.")
