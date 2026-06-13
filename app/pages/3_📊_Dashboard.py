import streamlit as st
import pandas as pd
import os
import plotly.express as px
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import style_excel

st.set_page_config(page_title="Dashboard Tổng Quan", page_icon="📊", layout="wide")

# ── Nạp giao diện CSS & Plotly Dark Theme ──────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if not os.path.exists(css_path):
    css_path = os.path.join(os.path.dirname(__file__), "..", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.title("📊 Dashboard Phân Tích Tổng Quan")
st.write("Hiển thị các chỉ số KPI, phân phối features và công cụ tìm kiếm sản phẩm.")

# ── Đường dẫn file ───────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "processed_retail_data.csv")
CLST_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "clustering_results.csv")
RAW_PATH  = os.path.join(BASE_DIR, "..", "..", "data", "raw", "retail_store_inventory.csv")

FEATURE_COLS = [
    "total_sales", "sale_frequency", "revenue",
    "sales_variance", "avg_inventory", "stock_turnover", "fill_rate",
]

COLORS = {
    "Bán chạy": "#2ecc71", "Tồn kho cao": "#e74c3c",
    "Bán chậm": "#e67e22", "Ổn định": "#3498db",
}

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    if os.path.exists(CLST_PATH):
        clst = pd.read_csv(CLST_PATH)[["product_id", "store_id", "Cluster_Name", "Cluster_HC", "Cluster_KM"]]
        df = df.merge(clst, on=["product_id", "store_id"], how="left")
    return df

@st.cache_data
def load_raw_kpis():
    """Tính KPI thực từ raw data."""
    if not os.path.exists(RAW_PATH):
        return None
    raw = pd.read_csv(RAW_PATH)
    raw.columns = (raw.columns.str.strip().str.lower()
                   .str.replace(" ", "_").str.replace("/", "_"))
    raw["revenue"] = raw["units_sold"] * raw["price"]
    return {
        "total_revenue":    raw["revenue"].sum(),
        "total_units_sold": raw["units_sold"].sum(),
        "avg_units_sold":   raw["units_sold"].mean(),
        "avg_inventory":    raw["inventory_level"].mean(),
        "avg_price":        raw["price"].mean(),
        "n_stores":         raw["store_id"].nunique(),
        "n_products":       raw["product_id"].nunique(),
        "date_range":       f"{raw['date'].min()[:7]} → {raw['date'].max()[:7]}",
    }

if not os.path.exists(DATA_PATH):
    st.error("Không tìm thấy file `processed_retail_data.csv`. Hãy chạy `preprocessing.ipynb` trước.")
    st.stop()

df    = load_data()
kpis  = load_raw_kpis()

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.subheader("💡 Chỉ Số Vận Hành Thiết Yếu")

if kpis:
    # KPI từ raw data — giá trị thực, có ý nghĩa
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Tổng sản phẩm", kpis["n_products"])
    with col2:
        st.metric("🏪 Số cửa hàng", kpis["n_stores"])
    with col3:
        st.metric("🗓️ Khoảng thời gian", kpis["date_range"])

    st.write("") # Thêm khoảng trắng nhỏ giữa 2 dòng

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("💰 Tổng doanh thu", f"{kpis['total_revenue']:,.0f}")
    with col5:
        st.metric("📊 Tổng units bán", f"{kpis['total_units_sold']:,.0f}")
    with col6:
        st.metric("📈 TB units/giao dịch", f"{kpis['avg_units_sold']:.1f}")

    st.caption(f"Tồn kho TB: **{kpis['avg_inventory']:.1f}** units  |  Giá TB: **{kpis['avg_price']:.2f}**  |  Dữ liệu đã chuẩn hóa: **{len(df)} cặp** (product × store)")

else:
    # Fallback: KPI từ clustering results (có ý nghĩa hơn mean z-score)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Tổng cặp (product×store)", len(df))
    with col2:
        st.metric("🏷️ Số product_id", df["product_id"].nunique())
    with col3:
        st.metric("🏪 Số store_id", df["store_id"].nunique())
    with col4:
        if "Cluster_Name" in df.columns:
            best = df["Cluster_Name"].value_counts().idxmax()
            st.metric("🏆 Nhóm đông nhất", best)

    # Thống kê phân phối theo cụm (có ý nghĩa hơn mean = 0)
    if "Cluster_Name" in df.columns:
        st.caption("Phân bố cụm:")
        cluster_counts = df["Cluster_Name"].value_counts()
        cols = st.columns(len(cluster_counts))
        for col, (name, count) in zip(cols, cluster_counts.items()):
            pct = count / len(df) * 100
            col.metric(name, count, f"{pct:.1f}%")

st.markdown("---")

# ── Phân phối Features ───────────────────────────────────────────────────────
st.subheader("📈 Phân Phối Các Feature Chính")

feat_sel = st.selectbox("Chọn feature để xem phân phối:", FEATURE_COLS, index=0)

col_hist, col_box = st.columns(2)

with col_hist:
    fig_hist = px.histogram(
        df, x=feat_sel, nbins=20,
        color_discrete_sequence=["#2E86C1"],
        opacity=0.85, marginal="rug",
        title=f"Histogram: {feat_sel}"
    )
    fig_hist.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)

with col_box:
    if "Cluster_Name" in df.columns:
        fig_box = px.box(
            df, x="Cluster_Name", y=feat_sel,
            color="Cluster_Name",
            category_orders={"Cluster_Name": ["Bán chạy", "Tồn kho cao", "Bán chậm", "Ổn định"]},
            color_discrete_map={
                "Bán chạy": "#2ecc71", "Tồn kho cao": "#e74c3c",
                "Bán chậm": "#e67e22", "Ổn định": "#3498db"
            },
            title=f"Box plot theo Cụm: {feat_sel}"
        )
        fig_box.update_layout(margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        fig_box = px.box(df, y=feat_sel, title=f"Box plot: {feat_sel}")
        st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# ── Scatter Matrix ───────────────────────────────────────────────────────────
st.subheader("🔗 Mối Liên Hệ Giữa Các Feature")

col_x, col_y = st.columns(2)
with col_x:
    x_axis = st.selectbox("Trục X:", FEATURE_COLS, index=0)
with col_y:
    y_axis = st.selectbox("Trục Y:", FEATURE_COLS, index=5)

color_col = "Cluster_Name" if "Cluster_Name" in df.columns else None
color_map = {"Bán chạy": "#2ecc71", "Tồn kho cao": "#e74c3c",
             "Bán chậm": "#e67e22", "Ổn định": "#3498db"} if color_col else None

fig_scatter = px.scatter(
    df, x=x_axis, y=y_axis,
    color=color_col,
    color_discrete_map=color_map,
    hover_name="product_id",
    hover_data=["store_id"] + ([color_col] if color_col else []),
    opacity=0.75,
    title=f"Scatter: {x_axis} vs {y_axis}"
)
fig_scatter.update_traces(marker=dict(size=8, line=dict(width=0.5, color="white")))
fig_scatter.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    legend_title_text=""
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ── Tìm kiếm sản phẩm ───────────────────────────────────────────────────────
st.subheader("🔍 Tìm Kiếm & Tra Cứu Sản Phẩm")

col_sid, col_pid = st.columns(2)
with col_pid:
    search_pid = st.text_input("Tìm theo Product_ID (vd: P0001):", "").strip()
with col_sid:
    search_sid = st.text_input("Tìm theo Store_ID (vd: S001):", "").strip()

filtered = df.copy()
if search_pid:
    filtered = filtered[filtered["product_id"].str.contains(search_pid, case=False)]
if search_sid:
    filtered = filtered[filtered["store_id"].str.contains(search_sid, case=False)]

if search_pid or search_sid:
    if not filtered.empty:
        st.write(f"Tìm thấy **{len(filtered)}** kết quả:")
        st.dataframe(style_excel(filtered.style.format(precision=4)), hide_index=True, use_container_width=True)
    else:
        st.warning("Không tìm thấy kết quả phù hợp.")
else:
    st.write(f"Top 10 cặp (product × store) có **total_sales** cao nhất:")
    st.dataframe(
        style_excel(df.sort_values("total_sales", ascending=False).head(10).style.format(precision=4)),
        hide_index=True,
        use_container_width=True
    )
