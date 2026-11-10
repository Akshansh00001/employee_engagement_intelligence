# Employee Engagement & Burnout Intelligence System
**Palo Alto Networks | Advanced HR Analytics & Streamlit Dashboard**

An exploratory people-analytics application designed to understand engagement patterns, workload-related exposure signals, career-stage trends, and group-level intervention opportunities.

## Dataset audit
- Rows: **1,470**
- Original columns: **31**
- Missing cells: **0**
- Duplicate rows: **0**
- Average engagement index: **68.08/100**
- Average work-life balance index: **69.03/100**
- Overtime share: **28.3%**
- Attrition rate: **16.12%**

These metrics are calculated from the supplied CSV. They are descriptive statistics, not causal conclusions.

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Project layout
- `data/raw/`: original supplied dataset
- `data/processed/`: enriched data with derived indicators
- `src/analytics.py`: validation, KPI engineering, clustering and tests
- `app.py`: Streamlit dashboard
- `reports/`: dataset profile and research report

## KPI definitions
1. **Engagement Index (0–100):** arithmetic mean of Job Involvement, Job Satisfaction, Environment Satisfaction and Relationship Satisfaction, scaled from 1–4 to 0–100.
2. **Work-Life Balance Index (0–100):** WorkLifeBalance scaled from 1–4 to 0–100.
3. **Burnout Exposure Score (0–100):** 50 points for overtime and 50 for WorkLifeBalance ≤2. High = both; Medium = one; Low = neither.
4. **Satisfaction Stability Score (0–100):** inverse of the within-employee standard deviation across the four satisfaction dimensions. This is a consistency indicator, not a validated psychometric scale.
5. **Workload Stress Indicator (0–100):** transparent heuristic combining overtime, travel frequency and a commute-distance flag. It is not a clinical or validated stress measure.

## Responsible-use limitations
- The dataset contains no direct burnout diagnosis or longitudinal engagement measurements.
- Burnout exposure is therefore a workload/balance screening proxy, not a diagnosis or prediction.
- Attrition is used only for contextual comparison, not as proof of disengagement or burnout.
- Clustering is exploratory segmentation, not a classifier of employee worth or performance.
- Do not use individual scores for hiring, firing, promotion, discipline or other consequential employment decisions. Prefer aggregated cohorts, confidentiality and human review.
- The data dictionary names Palo Alto Networks, but validate dataset provenance before representing it as actual company employee data.
