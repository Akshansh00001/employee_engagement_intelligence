import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

SAT_COLS = ["JobInvolvement", "JobSatisfaction", "EnvironmentSatisfaction", "RelationshipSatisfaction"]
ORDINAL_COLS = SAT_COLS + ["WorkLifeBalance"]

def load_data(path="data/raw/Palo Alto Networks.csv"):
    return pd.read_csv(path)

def validate_and_enrich(raw):
    df = raw.copy()
    df.columns = df.columns.str.strip()
    required = SAT_COLS + ["WorkLifeBalance", "OverTime", "BusinessTravel", "DistanceFromHome", "Attrition"]
    missing_cols = sorted(set(required) - set(df.columns))
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    for col in ORDINAL_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Values outside 1-4 are treated as invalid/missing, not silently accepted.
        df.loc[~df[col].between(1, 4), col] = np.nan
        df[col] = df[col].fillna(df[col].median())
    df["OverTime"] = df["OverTime"].astype(str).str.strip().str.title()
    df["BusinessTravel"] = df["BusinessTravel"].astype(str).str.strip()
    df["EngagementIndex"] = df[SAT_COLS].mean(axis=1).div(4).mul(100).round(2)
    df["WorkLifeBalanceIndex"] = df["WorkLifeBalance"].div(4).mul(100).round(2)
    df["SatisfactionStabilityScore"] = (
        100 - (df[SAT_COLS].std(axis=1, ddof=0) / 1.5 * 100).clip(0, 100)
    ).round(2)
    overtime = df["OverTime"].eq("Yes").astype(int)
    low_balance = df["WorkLifeBalance"].le(2).astype(int)
    df["BurnoutExposureScore"] = (overtime * 50 + low_balance * 50).astype(int)
    df["BurnoutRisk"] = np.select(
        [df["BurnoutExposureScore"].eq(100), df["BurnoutExposureScore"].eq(50)],
        ["High", "Medium"], default="Low"
    )
    travel_map = {
        "Non-Travel": 0, "Travel_Rarely": 15, "Travel Frequently": 50,
        "Travel_Frequently": 50, "Frequently": 50, "Rarely": 15
    }
    travel_score = df["BusinessTravel"].map(travel_map).fillna(0)
    commute_score = np.where(df["DistanceFromHome"] >= df["DistanceFromHome"].median(), 15, 0)
    df["WorkloadStressIndicator"] = (overtime * 50 + travel_score + commute_score).clip(0, 100).round(0)
    return df

def group_engagement(df, column):
    return (df.groupby(column, dropna=False)
              .agg(Employees=("EngagementIndex","size"),
                   Engagement=("EngagementIndex","mean"),
                   WorkLifeBalance=("WorkLifeBalanceIndex","mean"),
                   OvertimeShare=("OverTime", lambda s: s.eq("Yes").mean()*100),
                   HighExposureShare=("BurnoutRisk", lambda s: s.eq("High").mean()*100))
              .reset_index()
              .round(2))

def run_clustering(df, n_clusters=4):
    cols = SAT_COLS + ["WorkLifeBalance", "YearsAtCompany", "YearsInCurrentRole", "DistanceFromHome"]
    X = df[cols].apply(pd.to_numeric, errors="coerce").fillna(df[cols].median())
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    k = min(max(2, int(n_clusters)), max(2, len(df)-1))
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(Xs)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(Xs)
    out = df.copy()
    out["Cluster"] = labels.astype(str)
    out["PCA1"], out["PCA2"] = coords[:,0], coords[:,1]
    sil = silhouette_score(Xs, labels) if len(set(labels)) > 1 and len(df) > k else np.nan
    return out, model, scaler, pca, float(sil)

def statistical_tests(df):
    overtime_yes = df.loc[df.OverTime.eq("Yes"), "EngagementIndex"]
    overtime_no = df.loc[df.OverTime.eq("No"), "EngagementIndex"]
    t = stats.ttest_ind(overtime_yes, overtime_no, equal_var=False, nan_policy="omit")
    groups = [g["EngagementIndex"].values for _,g in df.groupby("BusinessTravel") if len(g)>1]
    a = stats.f_oneway(*groups) if len(groups)>=2 else (np.nan,np.nan)
    return {
        "overtime_t_stat": float(t.statistic), "overtime_p_value": float(t.pvalue),
        "travel_f_stat": float(a.statistic), "travel_p_value": float(a.pvalue)
    }
