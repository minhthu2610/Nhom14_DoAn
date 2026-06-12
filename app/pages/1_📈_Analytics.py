import streamlit as st
import pandas as pd
import os
import plotly.express as px
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import style_excel

st.set_page_config(page_title="Nhận Diện & Khuyến Nghị Sản Phẩm", page_icon="📈", layout="wide")

# ── Nạp giao diện CSS & Plotly Dark Theme ──────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if not os.path.exists(css_path):
    css_path = os.path.join(os.path.dirname(__file__), "..", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.title("📈 Phân Tích Chuyên Sâu & Giải Pháp Hỗ Trợ Tồn Kho")
st.write("Nhận diện sản phẩm bán chạy, bán chậm, tồn kho cao và đưa ra đề xuất tối ưu hóa chuỗi cung ứng.")

st.markdown("### 🎯 Đề Xuất Quản Lý Tồn Kho Theo Phân Cụm")

st.markdown("""
<style>
.strat-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.strat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    border-color: var(--primary-color);
}
.strat-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 8px;
}
.strat-content {
    font-size: 0.95rem;
    color: var(--text-color);
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="strat-card">
        <div class="strat-title" style="color: #2ecc71;">🟢 Cụm Bán chạy</div>
        <div class="strat-content">
            <b>Đặc điểm:</b> 📈 Doanh số cao, quay vòng nhanh<br/>
            <b>Chiến lược:</b> Tăng mức tồn kho an toàn, ưu tiên cung ứng đầy đủ
        </div>
    </div>
    <div class="strat-card">
        <div class="strat-title" style="color: #e67e22;">🟠 Cụm Bán chậm</div>
        <div class="strat-content">
            <b>Đặc điểm:</b> 📉 Doanh số thấp, tiêu thụ chậm<br/>
            <b>Chiến lược:</b> Giảm lượng nhập hàng, theo dõi và đánh giá lại
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="strat-card">
        <div class="strat-title" style="color: #3498db;">🔵 Cụm Ổn định</div>
        <div class="strat-content">
            <b>Đặc điểm:</b> 〰️ Nhu cầu ổn định, tồn kho hợp lý<br/>
            <b>Chiến lược:</b> Duy trì kế hoạch nhập hàng hiện tại
        </div>
    </div>
    <div class="strat-card">
        <div class="strat-title" style="color: #e74c3c;">🔴 Cụm Tồn kho cao</div>
        <div class="strat-content">
            <b>Đặc điểm:</b> 📦 Tồn kho rất cao, nguy cơ ứ đọng<br/>
            <b>Chiến lược:</b> Thực hiện khuyến mãi, xả hàng, tối ưu tồn kho
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="strat-card" style="border-left: 4px solid var(--primary-color);">
    <div class="strat-content">
        <b>💡 Ý nghĩa:</b> Khung chiến lược này giúp doanh nghiệp phân bổ nguồn lực và xây dựng kế hoạch tồn kho phù hợp cho từng nhóm sản phẩm tại từng chi nhánh một cách tổng quan nhất.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

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

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH)
    if os.path.exists(CLST_PATH):
        clst = pd.read_csv(CLST_PATH)[["product_id", "store_id", "Cluster_Name"]]
        df = df.merge(clst, on=["product_id", "store_id"], how="left")
    return df

if not os.path.exists(DATA_PATH):
    st.error("Không tìm thấy `processed_retail_data.csv`. Hãy chạy `preprocessing.ipynb` trước.")
    st.stop()

df = load_data()

# ── Section 1: Top sản phẩm theo nhóm ───────────────────────────────────────
st.subheader("🔍 Nhận Diện Sản Phẩm Đặc Biệt")

tab_best, tab_slow, tab_high_inv, tab_fill = st.tabs([
    "🔥 Bán chạy (Bestsellers)",
    "💤 Bán chậm (Slow Movers)",
    "📦 Tồn kho cao (High Inventory)",
    "⚠️ Fill Rate thấp"
])

with tab_best:
    st.write("Top 10 cặp (product × store) **thuộc cụm Bán chạy** có **total_sales** cao nhất:")
    best_df = df[df["Cluster_Name"] == "Bán chạy"].sort_values("total_sales", ascending=False).head(10)
    st.dataframe(style_excel(best_df.style.format(precision=4)), hide_index=True, use_container_width=True)
    fig = px.bar(
        best_df, x="product_id", y="total_sales",
        color="revenue", color_continuous_scale="Mint",
        hover_data=["store_id", "sale_frequency"],
        title="Top 10 — Doanh số cao nhất (Cụm Bán chạy)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_slow:
    st.write("Top 10 cặp (product × store) **thuộc cụm Bán chậm** có **total_sales** thấp nhất:")
    slow_df = df[df["Cluster_Name"] == "Bán chậm"].sort_values("total_sales", ascending=True).head(10)
    st.dataframe(style_excel(slow_df.style.format(precision=4)), hide_index=True, use_container_width=True)
    fig = px.bar(
        slow_df, x="product_id", y="total_sales",
        color="days_since_last_sale" if "days_since_last_sale" in df.columns else "fill_rate",
        color_continuous_scale="Oranges",
        hover_data=["store_id"],
        title="Top 10 — Doanh số thấp nhất (Cụm Bán chậm)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_high_inv:
    st.write("Top 10 cặp (product × store) **thuộc cụm Tồn kho cao** có **avg_inventory** cao nhất:")
    high_inv = df[df["Cluster_Name"] == "Tồn kho cao"].sort_values("avg_inventory", ascending=False).head(10)
    st.dataframe(style_excel(high_inv.style.format(precision=4)), hide_index=True, use_container_width=True)
    fig = px.bar(
        high_inv, x="product_id", y="avg_inventory",
        color="stock_turnover", color_continuous_scale="Reds",
        hover_data=["store_id", "total_sales"],
        title="Top 10 — Tồn kho cao nhất (Cụm Tồn kho cao)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_fill:
    st.write("Top 10 cặp (product × store) có **fill_rate** thấp nhất (không đáp ứng đủ nhu cầu):")
    low_fill = df.sort_values("fill_rate", ascending=True).head(10)
    st.dataframe(style_excel(low_fill.style.format(precision=4)), hide_index=True, use_container_width=True)
    fig = px.bar(
        low_fill, x="product_id", y="fill_rate",
        color="Cluster_Name" if "Cluster_Name" in df.columns else "total_sales",
        color_discrete_map=COLORS if "Cluster_Name" in df.columns else None,
        hover_data=["store_id", "stock_turnover"],
        title="Top 10 — Fill rate thấp nhất"
    )
    fig.update_layout(
        margin=dict(b=60),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0),
        legend_title_text=""
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Section 2: Đề xuất tồn kho ──────────────────────────────────────────────
st.subheader("💡 Đề Xuất Tự Động Tối Ưu Hóa Tồn Kho (thông số cụ thể)")
st.write(
    "Hệ thống tự động phân loại rủi ro dựa trên **total_sales**, **avg_inventory**, "
    "**stock_turnover**, và **fill_rate** (tứ phân vị 25%/75%):"
)

# Tứ phân vị từ dữ liệu thực
q = {col: {"low": df[col].quantile(0.25), "high": df[col].quantile(0.75)} for col in
     ["total_sales", "avg_inventory", "stock_turnover", "fill_rate"]}

recommendations = []
for _, row in df.iterrows():
    sales     = row["total_sales"]
    inv       = row["avg_inventory"]
    turnover  = row["stock_turnover"]
    fill      = row["fill_rate"]
    rec, status = "Chưa có đề xuất đặc biệt", "Bình thường"

    if sales > q["total_sales"]["high"] and inv < q["avg_inventory"]["low"]:
        rec    = "⚠️ Doanh số cao nhưng tồn kho rất thấp — bổ sung hàng gấp để tránh hụt kho!"
        status = "Bổ sung khẩn cấp"
    elif sales < q["total_sales"]["low"] and inv > q["avg_inventory"]["high"]:
        rec    = "💸 Bán rất chậm, tồn kho quá cao — khuyến mãi, combo thanh lý giải phóng kho."
        status = "Khuyến mãi thanh lý"
    elif turnover < q["stock_turnover"]["low"] and inv > q["avg_inventory"]["high"]:
        rec    = "🚨 Vòng quay kho cực thấp, rủi ro đọng vốn cao — ngừng đặt mua thêm, đánh giá lại nhu cầu."
        status = "Ngừng mua mới"
    elif fill < q["fill_rate"]["low"] and sales > q["total_sales"]["high"]:
        rec    = "📉 Nhu cầu cao nhưng tỷ lệ đáp ứng thấp (fill_rate âm) — kiểm tra lại dự báo và lịch nhập hàng."
        status = "Cải thiện dự báo"
    elif turnover > q["stock_turnover"]["high"] and inv < q["avg_inventory"]["low"]:
        rec    = "✅ Vòng quay kho tốt, hàng lưu chuyển nhanh — duy trì lịch cung ứng hiện tại."
        status = "Duy trì cung ứng"

    recommendations.append({
        "Product_ID":  row["product_id"],
        "Store_ID":    row["store_id"],
        "Cluster":     row.get("Cluster_Name", "N/A"),
        "Total Sales": f"{row['total_sales']:.3f}",
        "Avg Inventory": f"{inv:.3f}",
        "Turnover Rate": f"{turnover:.3f}",
        "Fill Rate":   f"{fill:.3f}",
        "Phân nhóm":   status,
        "Khuyến nghị": rec,
    })

rec_df = pd.DataFrame(recommendations)

all_statuses = ["Tất cả", "Bổ sung khẩn cấp", "Khuyến mãi thanh lý",
                "Ngừng mua mới", "Cải thiện dự báo", "Duy trì cung ứng", "Bình thường"]
action_filter = st.selectbox("Lọc theo Phân nhóm:", all_statuses)

show_df = rec_df if action_filter == "Tất cả" else rec_df[rec_df["Phân nhóm"] == action_filter]
st.write(f"Hiển thị **{len(show_df)}** sản phẩm:")
st.dataframe(style_excel(show_df.style.format(precision=4)), hide_index=True, use_container_width=True)

st.markdown("---")

# ── Section 3: Ma trận Vòng quay vs Doanh số ────────────────────────────────
st.subheader("🛠️ Ma Trận Vận Hành: Stock Turnover × Total Sales")

df["_inv_abs"] = df["avg_inventory"].abs()
color_matrix = "Cluster_Name" if "Cluster_Name" in df.columns else "fill_rate"
color_map_matrix = COLORS if color_matrix == "Cluster_Name" else None

fig_matrix = px.scatter(
    df, x="total_sales", y="stock_turnover",
    size="_inv_abs",
    color=color_matrix,
    color_discrete_map=color_map_matrix,
    hover_name="product_id",
    hover_data=["store_id", "avg_inventory", "fill_rate"],
    labels={
        "total_sales": "Doanh số (z-score)",
        "stock_turnover": "Vòng quay kho (z-score)"
    },
    title="Ma trận Vận hành sản phẩm — kéo để zoom vùng chi tiết",
    opacity=0.8
)
fig_matrix.update_traces(marker=dict(line=dict(width=0.5, color="white")))
fig_matrix.update_layout(legend_title_text="Cụm" if color_matrix == "Cluster_Name" else "Fill Rate")
st.plotly_chart(fig_matrix, use_container_width=True)
