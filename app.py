import streamlit as st
import pandas as pd
import plotly.express as px
from src.analytics import load_data, validate_and_enrich, group_engagement, run_clustering, statistical_tests, SAT_COLS

st.set_page_config(page_title="Employee Engagement Intelligence", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #111827; border: 1px solid #263449; padding: 14px; border-radius: 12px;}
h1,h2,h3 {letter-spacing: -.3px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return validate_and_enrich(load_data())

try:
    data = get_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

st.sidebar.title("PAN | People Intelligence")
page = st.sidebar.radio("Navigate", [
    "Engagement Overview", "Burnout Risk", "Role & Career", "Statistical & ML", "Manager Action Panel"
])
st.sidebar.caption("Exploratory workforce analytics • Not a clinical burnout assessment")

departments = sorted(data["Department"].dropna().unique().tolist())
roles = sorted(data["JobRole"].dropna().unique().tolist())
sel_dept = st.sidebar.multiselect("Department", departments, default=departments)
sel_role = st.sidebar.multiselect("Job role", roles, default=roles)
overtime_filter = st.sidebar.selectbox("Overtime", ["All", "Yes", "No"])
threshold = st.sidebar.slider("Low-engagement threshold", 0, 100, 60)
tenure_min, tenure_max = int(data.YearsAtCompany.min()), int(data.YearsAtCompany.max())
tenure = st.sidebar.slider("Years at company", tenure_min, tenure_max, (tenure_min, tenure_max))
f = data[data.Department.isin(sel_dept) & data.JobRole.isin(sel_role) &
         data.YearsAtCompany.between(tenure[0], tenure[1])]
if overtime_filter != "All":
    f = f[f.OverTime.eq(overtime_filter)]
if f.empty:
    st.warning("No employees match the selected filters.")
    st.stop()

st.title("Employee Engagement & Burnout Intelligence")
st.caption("Palo Alto Networks | Employee experience diagnostics and preventive people analytics")
st.caption(f"Filtered population: {len(f):,} employees")

def metric_row(frame):
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Engagement Index", f"{frame.EngagementIndex.mean():.1f}/100")
    c2.metric("Work-Life Balance", f"{frame.WorkLifeBalanceIndex.mean():.1f}/100")
    c3.metric("High Exposure", f"{(frame.BurnoutRisk.eq('High').mean()*100):.1f}%")
    c4.metric("Overtime Share", f"{(frame.OverTime.eq('Yes').mean()*100):.1f}%")

if page == "Engagement Overview":
    metric_row(f)
    left,right = st.columns(2)
    with left:
        st.subheader("Satisfaction distribution")
        long = f[SAT_COLS].melt(var_name="Dimension", value_name="Rating")
        st.plotly_chart(px.histogram(long, x="Rating", color="Dimension", barmode="group",
                                     category_orders={"Rating":[1,2,3,4]}, title="Ratings across four dimensions"), use_container_width=True)
    with right:
        st.subheader("Engagement by department")
        g = group_engagement(f, "Department").sort_values("Engagement")
        st.plotly_chart(px.bar(g, x="Engagement", y="Department", orientation="h",
                               color="Engagement", range_color=(0,100), title="Average engagement score"), use_container_width=True)
    st.subheader("Engagement score distribution")
    st.plotly_chart(px.histogram(f, x="EngagementIndex", nbins=20, color="Department"), use_container_width=True)

elif page == "Burnout Risk":
    metric_row(f)
    st.subheader("Exposure classification")
    risk = f["BurnoutRisk"].value_counts().rename_axis("Risk").reset_index(name="Employees")
    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.pie(risk, names="Risk", values="Employees", hole=.55, title="Burnout exposure groups"), use_container_width=True)
    with c2:
        st.plotly_chart(px.density_heatmap(f, x="WorkLifeBalance", y="EngagementIndex",
                         histfunc="count", title="Work-life balance vs engagement"), use_container_width=True)
    st.subheader("Overtime and work-life balance")
    cross = f.groupby(["OverTime","WorkLifeBalance"], observed=False).size().reset_index(name="Employees")
    st.plotly_chart(px.density_heatmap(cross, x="WorkLifeBalance", y="OverTime", z="Employees",
                                      title="Employee counts by overtime and balance"), use_container_width=True)
    st.info("High = overtime AND balance ≤2; Medium = exactly one condition; Low = neither. These are operational exposure flags, not diagnoses.")

elif page == "Role & Career":
    metric_row(f)
    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(group_engagement(f,"JobRole"), x="JobRole", y="Engagement",
                               color="Engagement", title="Engagement by job role"), use_container_width=True)
    with c2:
        st.plotly_chart(px.line(group_engagement(f,"JobLevel"), x="JobLevel", y="Engagement",
                                markers=True, title="Engagement by job level"), use_container_width=True)
    tenure_df = f.copy()
    tenure_df["TenureBand"] = pd.cut(tenure_df["YearsAtCompany"], bins=[-1,1,3,5,10,100],
                                     labels=["0–1","2–3","4–5","6–10","10+"])
    st.plotly_chart(px.line(group_engagement(tenure_df,"TenureBand"), x="TenureBand", y="Engagement",
                            markers=True, title="Engagement across company tenure"), use_container_width=True)
    st.plotly_chart(px.scatter(f, x="YearsInCurrentRole", y="EngagementIndex", color="YearsSinceLastPromotion",
                               hover_data=["JobRole","JobLevel"], title="Current-role tenure and engagement"), use_container_width=True)

elif page == "Statistical & ML":
    metric_row(f)
    tests = statistical_tests(f)
    st.subheader("Statistical comparisons")
    a,b = st.columns(2)
    a.metric("Overtime vs non-overtime p-value", f"{tests['overtime_p_value']:.4g}")
    b.metric("Travel-group ANOVA p-value", f"{tests['travel_p_value']:.4g}")
    st.caption("Welch's t-test compares mean engagement by overtime. One-way ANOVA compares engagement across travel categories. Statistical association is not causation.")
    st.subheader("Exploratory employee pattern clustering")
    k = st.slider("Number of clusters", 2, 7, 4)
    clustered, model, scaler, pca, sil = run_clustering(f, k)
    st.metric("Silhouette score", f"{sil:.3f}" if pd.notna(sil) else "N/A")
    st.plotly_chart(px.scatter(clustered, x="PCA1", y="PCA2", color="Cluster",
                               hover_data=["EngagementIndex","WorkLifeBalance","OverTime","JobRole"],
                               title="PCA view of K-Means employee segments"), use_container_width=True)
    st.dataframe(clustered.groupby("Cluster").agg(Employees=("Cluster","size"),
                 Engagement=("EngagementIndex","mean"), Balance=("WorkLifeBalanceIndex","mean"),
                 OvertimeShare=("OverTime",lambda s:s.eq("Yes").mean()*100)).round(2), use_container_width=True)

elif page == "Manager Action Panel":
    metric_row(f)
    low = f[f.EngagementIndex <= threshold]
    st.subheader("Priority group indicators")
    c1,c2,c3 = st.columns(3)
    c1.metric("Below threshold", len(low))
    c2.metric("Below threshold + overtime", int((low.OverTime=="Yes").sum()))
    c3.metric("Below threshold + low balance", int((low.WorkLifeBalance<=2).sum()))
    st.subheader("Department-level intervention priorities")
    priority = group_engagement(f,"Department")
    priority["PriorityScore"] = (100-priority["Engagement"])*.5 + priority["HighExposureShare"]*.3 + priority["OvertimeShare"]*.2
    priority = priority.sort_values("PriorityScore", ascending=False)
    st.dataframe(priority, use_container_width=True)
    st.markdown("""
    **Suggested review actions**
    - Review workload allocation and overtime patterns in groups with elevated exposure.
    - Conduct confidential listening sessions where engagement dimensions are consistently low.
    - Examine career progression, role clarity and manager support in tenure groups with lower engagement.
    - Reassess group-level indicators over time before concluding an intervention worked.
    """)
    st.warning("Do not use these indicators to rank, discipline, or make employment decisions about individual employees. Use aggregated groups and human review.")

with st.expander("Data quality & definitions"):
    st.write(f"Rows: {len(data):,} | Columns: {len(data.columns):,} | Missing cells in raw data: {int(load_data().isna().sum().sum())} | Duplicate rows: {int(load_data().duplicated().sum())}")
    st.write("Engagement = mean of four 1–4 dimensions scaled to 0–100. Stability = inverse within-row dispersion. Risk classification uses overtime and work-life balance ≤2.")
