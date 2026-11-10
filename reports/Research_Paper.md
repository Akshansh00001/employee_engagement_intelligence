# Employee Engagement & Burnout Intelligence
## Exploratory Research Report

### Abstract
This project constructs transparent employee-experience indicators from a cross-sectional HR dataset and explores how satisfaction, overtime, work-life balance, travel and career-stage variables vary across employee groups. The analysis is diagnostic and descriptive; it does not establish causality or diagnose burnout.

### 1. Dataset and data quality
The supplied dataset contains **1,470 records** and **31 fields**. The initial file contains **0 missing cells** and **0 duplicate rows**. The four satisfaction dimensions and WorkLifeBalance are validated against their expected 1–4 ordinal range. Invalid or missing values are handled by median imputation in the reusable preprocessing pipeline; the current source file has no missing cells.

### 2. Methodology
- Validate schema, types, duplicates and ordinal scales.
- Compute Engagement Index as the mean of four engagement dimensions, scaled to 0–100.
- Compute Work-Life Balance Index on a 0–100 scale.
- Create a transparent exposure flag: overtime (50 points) plus low balance (50 points for rating ≤2).
- Compare engagement across overtime, travel, commute, department, role, job level and tenure.
- Use Welch's t-test and one-way ANOVA as exploratory group comparisons.
- Use K-Means and PCA for exploratory segmentation and visualization.
- Compare engagement by attrition status as context only.

### 3. Dataset-level descriptive results
| Indicator | Result |
|---|---:|
| Average engagement index | 68.08/100 |
| Average work-life balance index | 69.03/100 |
| Overtime share | 28.3% |
| High exposure group | 8.57% |
| Medium exposure group | 40.0% |
| Low exposure group | 51.43% |
| Attrition rate | 16.12% |
| Engagement: stayed | 69.09/100 |
| Engagement: left | 62.82/100 |

### 4. Interpretation and recommendations
The indicators should be interpreted as group-level signals requiring further investigation. HR teams can review workload distribution where overtime and low balance co-occur, examine career progression and role clarity where engagement is lower in particular tenure cohorts, and use confidential listening sessions to understand local causes. Repeat measurements over time are required to identify deterioration rather than a one-time snapshot.

### 5. Limitations
The dataset is cross-sectional and has no direct burnout label, longitudinal engagement history, working-hours quantity, or validated clinical measure. The risk score is a transparent heuristic. Statistical differences do not prove causal effects. The data's company provenance should be verified before attributing findings to Palo Alto Networks.

### 6. Conclusion
The system provides a reproducible framework for employee-experience diagnostics and preventive group-level review. It should complement—not replace—employee voice, HR expertise, privacy safeguards and longitudinal measurement.
