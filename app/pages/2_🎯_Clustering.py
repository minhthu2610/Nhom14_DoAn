import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import style_excel

st.set_page_config(page_title="Phân Cụm Sản Phẩm", page_icon="🎯", layout="wide")

# ── Nạp giao diện CSS & Plotly Dark Theme ──────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if not os.path.exists(css_path):
    css_path = os.path.join(os.path.dirname(__file__), "..", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.title("🎯 Phân Cụm Sản Phẩm — Hierarchical & K-Means")
st.write(
    "Kết quả phân cụm từ `clustering.ipynb` sử dụng **Hierarchical Clustering (Ward, k=4)** làm chính "
    "và **K-Means (k=4)** để so sánh. Nhãn cụm được đặt tự động dựa trên profile đặc trưng."
)

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "processed_retail_data.csv")
CLST_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "clustering_results.csv")

FEATURE_COLS = [
    "total_sales", "sale_frequency", "revenue",
    "sales_variance", "avg_inventory", "stock_turnover", "fill_rate",
]

COLORS = {
    "Bán chạy":    "#2ecc71",
    "Tồn kho cao": "#e74c3c",
    "Bán chậm":    "#e67e22",
    "Ổn định":     "#3498db",
}
CLUSTER_ORDER = ["Bán chạy", "Tồn kho cao", "Bán chậm", "Ổn định"]

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None, None
    features = pd.read_csv(DATA_PATH)
    clustering = pd.read_csv(CLST_PATH) if os.path.exists(CLST_PATH) else None
    if clustering is not None:
        df = features.merge(
            clustering[["product_id", "store_id", "Cluster_HC", "Cluster_KM", "Cluster_Name"]],
            on=["product_id", "store_id"], how="left"
        )
    else:
        df = features
    return df, clustering

if not os.path.exists(DATA_PATH):
    st.error("Không tìm thấy `processed_retail_data.csv`. Hãy chạy `preprocessing.ipynb` trước.")
    st.stop()

if not os.path.exists(CLST_PATH):
    st.warning(
        "Chưa có `clustering_results.csv`. "
        "Hãy chạy `clustering.ipynb` để tạo kết quả phân cụm. "
        "Trang này sẽ chạy lại K-Means trực tiếp để tạm thời hiển thị."
    )

df, clustering = load_data()

# ── Nếu chưa có clustering_results, chạy KMeans tạm ─────────────────────────
if "Cluster_Name" not in df.columns:
    st.info("Đang chạy K-Means tạm thời (k=4) để hiển thị...")
    from sklearn.cluster import KMeans, AgglomerativeClustering

    X = df[FEATURE_COLS].values
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    df["Cluster_KM"] = km.fit_predict(X)

    hc = AgglomerativeClustering(n_clusters=4, linkage="ward")
    df["Cluster_HC"] = hc.fit_predict(X)

    # Đặt tên cụm tự động theo profile (giống clustering.ipynb)
    profile = df.groupby("Cluster_HC")[FEATURE_COLS].mean()
    rank_sales = profile["total_sales"].rank(ascending=False)
    rank_inv   = profile["avg_inventory"].rank(ascending=False)
    rank_fill  = profile["fill_rate"].rank(ascending=True)

    assigned, used = {}, set()
    for label, rank_series in [("Bán chạy", rank_sales), ("Tồn kho cao", rank_inv), ("Bán chậm", rank_fill)]:
        for cid in rank_series.sort_values().index:
            if cid not in used:
                assigned[cid] = label
                used.add(cid)
                break
    for cid in profile.index:
        if cid not in assigned:
            assigned[cid] = "Ổn định"

    df["Cluster_Name"] = df["Cluster_HC"].map(assigned)

if "Cluster_KM" in df.columns:
    profile_km = df.groupby("Cluster_KM")[FEATURE_COLS].mean()
    rank_sales_km = profile_km["total_sales"].rank(ascending=False)
    rank_inv_km   = profile_km["avg_inventory"].rank(ascending=False)
    rank_fill_km  = profile_km["fill_rate"].rank(ascending=True)

    km_to_name = {}
    used_km = set()
    for label, rank_series in [("Bán chạy", rank_sales_km), ("Tồn kho cao", rank_inv_km), ("Bán chậm", rank_fill_km)]:
        for cid in rank_series.sort_values().index:
            if cid not in used_km:
                km_to_name[cid] = label
                used_km.add(cid)
                break
    for cid in profile_km.index:
        if cid not in km_to_name:
            km_to_name[cid] = "Ổn định"

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.subheader("⚙️ Tuỳ chỉnh hiển thị")
algo_choice = st.sidebar.radio(
    "Chọn thuật toán hiển thị:",
    ["**Hierarchical** (Cluster_Name)", "**K-Means** (Cluster_KM)"],
    index=0
)
use_hc = algo_choice.startswith("**Hierarchical")

# ── Section 1: Tổng quan phân bố ────────────────────────────────────────────
st.subheader("📊 Phân Bố Cụm Sản Phẩm")

col_pie, col_bar = st.columns(2)

cluster_col = "Cluster_Name" if use_hc else "Cluster_KM"

if use_hc:
    counts = df["Cluster_HC"].value_counts().sort_index()
    name_map = df.drop_duplicates("Cluster_HC").set_index("Cluster_HC")["Cluster_Name"].to_dict()
    labels = [f"Cụm {i} ({name_map.get(i, '')})" for i in counts.index]
    pie_colors = [COLORS[name_map.get(i, "Ổn định")] for i in counts.index]
    bar_colors = pie_colors
else:
    counts = df["Cluster_KM"].value_counts().sort_index()
    labels = [f"Cụm {i} ({km_to_name[i]})" for i in counts.index]
    pie_colors = [COLORS[km_to_name[i]] for i in counts.index]
    bar_colors = pie_colors

with col_pie:
    color_map = {label: color for label, color in zip(labels, pie_colors)}
    fig_pie = px.pie(
        values=counts.values, names=labels,
        color=labels,
        color_discrete_map=color_map,
        hole=0.4,
        title="Tỷ lệ phần trăm mỗi cụm"
    )
    fig_pie.update_layout(legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.1,
        xanchor="center",
        x=0.5
    ))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    fig_bar = px.bar(
        x=labels, y=counts.values,
        color=labels, color_discrete_map=color_map,
        text=counts.values,
        title="Số lượng cặp (product × store) mỗi cụm",
        labels={"x": "Cụm", "y": "Số điểm"}
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── Section 2: Scatter Plot ──────────────────────────────────────────────────
st.subheader("🔵 Scatter Plot Phân Cụm")

col_x, col_y = st.columns(2)
with col_x:
    x_axis = st.selectbox("Trục X:", FEATURE_COLS, index=0)
with col_y:
    y_axis = st.selectbox("Trục Y:", FEATURE_COLS, index=5)

if use_hc:
    fig_scatter = px.scatter(
        df, x=x_axis, y=y_axis,
        color="Cluster_Name",
        color_discrete_map=COLORS,
        category_orders={"Cluster_Name": CLUSTER_ORDER},
        symbol="Cluster_Name",
        hover_name="product_id",
        hover_data=["store_id", "Cluster_Name"],
        title=f"Hierarchical Clustering — {x_axis} vs {y_axis}"
    )
else:
    df["_cluster_str"] = df["Cluster_KM"].apply(lambda x: f"Cụm {x} ({km_to_name[x]})")
    seq_map = {f"Cụm {i} ({km_to_name[i]})": COLORS[km_to_name[i]] for i in km_to_name.keys()}
    fig_scatter = px.scatter(
        df, x=x_axis, y=y_axis,
        color="_cluster_str",
        color_discrete_map=seq_map,
        category_orders={"_cluster_str": [f"Cụm {i} ({km_to_name[i]})" for i in sorted(df["Cluster_KM"].unique())]},
        symbol="_cluster_str",
        hover_name="product_id",
        hover_data=["store_id"],
        title=f"KMeans — {x_axis} vs {y_axis}"
    )

fig_scatter.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=0.8, color="white")))
fig_scatter.update_layout(
    margin=dict(b=60),
    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0),
    legend_title_text=""
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ── Section 3: Cluster Profile Heatmap ──────────────────────────────────────
st.subheader("🌡️ Profile Trung Bình Từng Cụm (Heatmap)")

if use_hc:
    # Gom nhóm theo cụm số (0, 1, 2, 3) để giữ nguyên thứ tự gốc của thuật toán
    profile = df.groupby("Cluster_HC")[FEATURE_COLS].mean().sort_index()
    name_map = df.drop_duplicates("Cluster_HC").set_index("Cluster_HC")["Cluster_Name"].to_dict()
    y_labels = [f"Cụm {i} ({name_map.get(i, '')})" for i in profile.index]
else:
    profile = df.groupby("Cluster_KM")[FEATURE_COLS].mean().sort_index()
    y_labels = [f"Cụm {i} ({km_to_name[i]})" for i in profile.index]

fig_heat = go.Figure(data=go.Heatmap(
    z=profile.values.round(3),
    x=FEATURE_COLS,
    y=y_labels,
    colorscale="RdYlGn",
    zmid=0,
    text=profile.values.round(2),
    texttemplate="%{text}",
    textfont={"size": 11},
))
fig_heat.update_layout(
    title="Giá trị trung bình (z-score) từng feature theo cụm",
    xaxis_tickangle=-20,
    yaxis=dict(autorange="reversed"),
    height=320,
    margin=dict(l=10, r=10, t=50, b=10)
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ── Section 4: Bộ lọc & danh sách ───────────────────────────────────────────
st.subheader("🔍 Bộ Lọc & Tra Cứu Sản Phẩm Theo Cụm")

if use_hc:
    cluster_options = ["Tất cả cụm"] + CLUSTER_ORDER
    selected = st.selectbox("Chọn cụm:", cluster_options)
    filtered_df = df if selected == "Tất cả cụm" else df[df["Cluster_Name"] == selected]
else:
    km_options = ["Tất cả cụm"] + [f"Cụm {i}" for i in sorted(df["Cluster_KM"].unique())]
    selected = st.selectbox("Chọn cụm:", km_options)
    if selected == "Tất cả cụm":
        filtered_df = df
    else:
        cid = int(selected.split(" ")[1])
        filtered_df = df[df["Cluster_KM"] == cid]

display_cols = ["product_id", "store_id"] + FEATURE_COLS
if "Cluster_Name" in filtered_df.columns:
    display_cols += ["Cluster_Name", "Cluster_HC", "Cluster_KM"]

st.write(f"Hiển thị **{len(filtered_df)}** cặp (product × store):")
st.dataframe(style_excel(filtered_df[display_cols].style.format(precision=4)), hide_index=True, use_container_width=True)

csv_data = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Tải xuống danh sách này (CSV)",
    data=csv_data,
    file_name=f"cluster_{selected.replace(' ', '_')}.csv",
    mime="text/csv"
)

# ── Section 5: So sánh HC vs KMeans (Silhouette) ────────────────────────────
if "Cluster_HC" in df.columns and "Cluster_KM" in df.columns:
    st.markdown("---")
    st.subheader("⚖️ So Sánh Hierarchical vs K-Means")

    try:
        from sklearn.metrics import silhouette_score
        X = df[FEATURE_COLS].values
        sil_hc = silhouette_score(X, df["Cluster_HC"].values)
        sil_km = silhouette_score(X, df["Cluster_KM"].values)

        c1, c2, c3 = st.columns(3)
        c1.metric("Silhouette — Hierarchical", f"{sil_hc:.4f}")
        c2.metric("Silhouette — KMeans", f"{sil_km:.4f}")
        winner = "Hierarchical" if sil_hc >= sil_km else "KMeans"
        c3.metric("Thuật toán tốt hơn", winner)
    except Exception:
        st.info("Cài sklearn để xem Silhouette Score.")
