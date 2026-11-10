# Data Dictionary & KPI Guide

## Engagement dimensions
- JobInvolvement
- JobSatisfaction
- EnvironmentSatisfaction
- RelationshipSatisfaction

Each is expected to use an ordinal scale of 1–4.

## Risk rules
- High exposure: OverTime = Yes AND WorkLifeBalance ≤ 2
- Medium exposure: exactly one of those conditions is true
- Low exposure: neither condition is true

## Commute grouping
For descriptive comparison, use the dataset median DistanceFromHome as the cut-off for short vs long commute. Always display the cut-off used.

## Travel mapping
Non-Travel = 0, Travel Rarely = 15, Travel Frequently = 50 for the workload heuristic. Confirm category spelling from the actual file.

## Important caveats
These scores are project-defined operational indicators, not validated clinical measures. Satisfaction scales are ordinal; means are convenient summaries but should be complemented by distributions and non-parametric checks where appropriate.
