import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Visualization Chuyên Sâu", page_icon="📉", layout="wide")

st.title("📉 Visualization Chuyên Sâu")
st.write(
    "Biểu đồ phân tích từ `visualization.ipynb`: phân bố theo category/region, "
    "xu hướng doanh thu theo tháng, top sản phẩm mỗi cụm và cảnh báo rủi ro."
)

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
FEAT_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "processed_retail_data.csv")
CLST_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "clustering_results.csv")
RAW_PATH  = os.path.join(BASE_DIR, "..", "..", "data", "raw", "retail_store_inventory.csv")
PNAME_PATH = os.path.join(BASE_DIR, "..", "..", "data", "processed", "product_names.json")

FEATURE_COLS = [
    "total_sales", "sale_frequency", "revenue",
    "sales_variance", "avg_inventory", "stock_turnover", "fill_rate",
]
CLUSTER_ORDER = ["Bán chạy", "Tồn kho cao", "Bán chậm", "Ổn định"]
COLORS = {
    "Bán chạy":    "#2ecc71",
    "Tồn kho cao": "#e74c3c",
    "Bán chậm":    "#e67e22",
    "Ổn định":     "#3498db",
}

for path, name in [(FEAT_PATH, "processed_retail_data.csv"), (CLST_PATH, "clustering_results.csv")]:
    if not os.path.exists(path):
        st.error(f"Không tìm thấy `{name}`. Hãy chạy notebook tương ứng trước.")
        st.stop()

@st.cache_data
def load_all():
    features = pd.read_csv(FEAT_PATH)
    results  = pd.read_csv(CLST_PATH)

    # Gộp nhãn vào features
    df = features.merge(
        results[["product_id", "store_id", "Cluster_HC", "Cluster_Name"]],
        on=["product_id", "store_id"], how="left"
    )

    # Product names từ visualization.ipynb
    product_names = {}
    if os.path.exists(PNAME_PATH):
        with open(PNAME_PATH, encoding="utf-8") as f:
            product_names = json.load(f)
    results["product_name"] = results["product_id"].map(product_names)

    # Raw data (nếu có) — cần cho revenue trend, category, region
    raw = None
    if os.path.exists(RAW_PATH):
        raw = pd.read_csv(RAW_PATH)
        raw.columns = (raw.columns.str.strip().str.lower()
                       .str.replace(" ", "_").str.replace("/", "_"))
        raw["date"] = pd.to_datetime(raw["date"])
        raw["revenue_raw"] = raw["units_sold"] * raw["price"]
        raw = raw.merge(
            results[["product_id", "store_id", "Cluster_Name"]],
            on=["product_id", "store_id"], how="left"
        )
        raw["product_name"] = raw["product_id"].map(product_names)

    return df, results, raw, product_names

df, results, raw, product_names = load_all()

# ── Tab layout ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗂️ Theo Category",
    "🌏 Theo Region",
    "📅 Xu hướng Doanh thu",
    "🏆 Top Sản phẩm",
    "🚨 Cảnh báo Rủi ro",
])

# ── Tab 1: Phân bố theo Category ─────────────────────────────────────────────
with tab1:
    st.subheader("Phân bố Cụm theo Danh mục Sản phẩm (Category)")
    if raw is not None:
        cat_map = raw.groupby(["product_id", "store_id"])["category"].first().reset_index()
        df_cat  = results.merge(cat_map, on=["product_id", "store_id"], how="left")

        ct = pd.crosstab(df_cat["category"], df_cat["Cluster_Name"])
        ct = ct.reindex(columns=CLUSTER_ORDER, fill_value=0)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                ct.reset_index().melt(id_vars="category"),
                x="category", y="value", color="Cluster_Name",
                color_discrete_map=COLORS,
                category_orders={"Cluster_Name": CLUSTER_ORDER},
                barmode="stack",
                title="Số lượng tuyệt đối",
                labels={"value": "Số điểm", "variable": "Cụm"}
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            ct_pct = ct.div(ct.sum(axis=1), axis=0).mul(100)
            fig2 = px.bar(
                ct_pct.reset_index().melt(id_vars="category"),
                x="category", y="value", color="Cluster_Name",
                color_discrete_map=COLORS,
                category_orders={"Cluster_Name": CLUSTER_ORDER},
                barmode="stack",
                title="Tỷ lệ phần trăm (%)",
                labels={"value": "%", "variable": "Cụm"}
            )
            fig2.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Cần file `retail_store_inventory.csv` trong `data/raw/` để hiển thị biểu đồ này.")

# ── Tab 2: Phân bố theo Region ───────────────────────────────────────────────
with tab2:
    st.subheader("Phân bố Cụm theo Khu vực (Region)")
    if raw is not None:
        reg_map = raw.groupby(["product_id", "store_id"])["region"].first().reset_index()
        df_reg  = results.merge(reg_map, on=["product_id", "store_id"], how="left")

        ct_reg = pd.crosstab(df_reg["region"], df_reg["Cluster_Name"])
        ct_reg = ct_reg.reindex(columns=CLUSTER_ORDER, fill_value=0)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                ct_reg.reset_index().melt(id_vars="region"),
                x="region", y="value", color="Cluster_Name",
                color_discrete_map=COLORS,
                category_orders={"Cluster_Name": CLUSTER_ORDER},
                barmode="stack",
                title="Số lượng tuyệt đối",
                labels={"value": "Số điểm", "variable": "Cụm"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            ct_reg_pct = ct_reg.div(ct_reg.sum(axis=1), axis=0).mul(100)
            fig2 = px.bar(
                ct_reg_pct.reset_index().melt(id_vars="region"),
                x="region", y="value", color="Cluster_Name",
                color_discrete_map=COLORS,
                category_orders={"Cluster_Name": CLUSTER_ORDER},
                barmode="stack",
                title="Tỷ lệ phần trăm (%)",
                labels={"value": "%", "variable": "Cụm"}
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Heatmap Product × Store
        st.subheader("Heatmap: Nhãn cụm Product × Store")
        pivot = results.pivot(index="product_id", columns="store_id", values="Cluster_Name")
        name_to_num = {"Bán chạy": 0, "Tồn kho cao": 1, "Bán chậm": 2, "Ổn định": 3}
        pivot_num = pivot.replace(name_to_num).fillna(-1).astype(float)

        colorscale = [[0, "#2ecc71"], [0.33, "#e74c3c"], [0.67, "#e67e22"], [1.0, "#3498db"]]
        fig_hm = go.Figure(go.Heatmap(
            z=pivot_num.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale=colorscale,
            zmin=0, zmax=3,
            text=[[str(v) if pd.notna(v) else "" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont={"size": 9},
            showscale=False,
        ))
        fig_hm.update_layout(
            title="Nhãn cụm theo Product × Store",
            xaxis_title="Store ID", yaxis_title="Product ID",
            height=600
        )
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        st.info("Cần file `retail_store_inventory.csv` trong `data/raw/` để hiển thị biểu đồ này.")

# ── Tab 3: Xu hướng Doanh thu ────────────────────────────────────────────────
with tab3:
    st.subheader("Xu hướng Doanh thu theo Tháng — Phân theo Cụm")
    if raw is not None:
        raw["month"] = raw["date"].dt.to_period("M")
        monthly = (
            raw.groupby(["month", "Cluster_Name"])["revenue_raw"]
            .sum().reset_index()
        )
        monthly["month_dt"] = monthly["month"].dt.to_timestamp()

        # Bỏ tháng cuối (dữ liệu không đầy đủ)
        last_month = monthly["month"].max()
        monthly = monthly[monthly["month"] < last_month]

        fig = go.Figure()
        for name in CLUSTER_ORDER:
            data = monthly[monthly["Cluster_Name"] == name].sort_values("month_dt")
            fig.add_trace(go.Scatter(
                x=data["month_dt"], y=data["revenue_raw"],
                name=name, line=dict(color=COLORS[name], width=2.5),
                mode="lines+markers", marker=dict(size=6)
            ))
        fig.update_layout(
            title="Xu hướng doanh thu theo tháng theo cụm",
            xaxis_title="Tháng", yaxis_title="Doanh thu (tổng)",
            legend_title="Cụm", hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần file `retail_store_inventory.csv` trong `data/raw/` để hiển thị biểu đồ này.")

# ── Tab 4: Top sản phẩm ──────────────────────────────────────────────────────
with tab4:
    st.subheader("Top 5 Sản phẩm Doanh thu Cao nhất trong Từng Cụm")

    if raw is not None:
        revenue_real = (
            raw.groupby(["product_id", "store_id"])["revenue_raw"]
            .sum().reset_index()
        )
        df_top = results.merge(revenue_real, on=["product_id", "store_id"])
        df_top["label"] = df_top["product_id"].apply(
            lambda x: product_names.get(x, x)
        ) + " (" + df_top["store_id"] + ")"

        for name in CLUSTER_ORDER:
            st.write(f"**Cụm: {name}**")
            top5 = df_top[df_top["Cluster_Name"] == name].nlargest(5, "revenue_raw")
            if top5.empty:
                st.caption("Không có sản phẩm nào trong cụm này.")
                continue
            fig = px.bar(
                top5, x="revenue_raw", y="label",
                orientation="h",
                color_discrete_sequence=[COLORS[name]],
                text=top5["revenue_raw"].apply(lambda v: f"{v:,.0f}"),
                title=f"Top 5 — {name}"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=280,
                               margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback: dùng total_sales từ features
        st.caption("Hiển thị theo **total_sales** (z-score) vì không có raw data.")
        for name in CLUSTER_ORDER:
            sub = df[df["Cluster_Name"] == name].nlargest(5, "total_sales")
            if sub.empty:
                continue
            sub["label"] = sub["product_id"] + " (" + sub["store_id"] + ")"
            fig = px.bar(
                sub, x="total_sales", y="label",
                orientation="h",
                color_discrete_sequence=[COLORS[name]],
                title=f"Top 5 — {name} (total_sales z-score)"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=280,
                               margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ── Tab 5: Cảnh báo Rủi ro ───────────────────────────────────────────────────
with tab5:
    st.subheader("🚨 Cảnh Báo Sản Phẩm Cần Xem Lại")
    st.write(
        "Các cặp (product × store) thuộc cụm **Bán chậm** hoặc **Tồn kho cao** "
        "với **fill_rate** và **stock_turnover** thấp nhất — rủi ro tồn đọng vốn cao."
    )

    alert_clusters = ["Bán chậm", "Tồn kho cao"]
    alert = df[df["Cluster_Name"].isin(alert_clusters)].copy()
    alert["label"] = alert["product_id"] + " - " + alert["store_id"]

    col1, col2 = st.columns(2)

    with col1:
        st.write("**15 sản phẩm có fill_rate thấp nhất**")
        top_fill = alert.sort_values("fill_rate").head(15)
        fig1 = px.bar(
            top_fill, x="fill_rate", y="label",
            color="Cluster_Name", color_discrete_map=COLORS,
            orientation="h",
            title="Fill rate thấp nhất (nhu cầu không được đáp ứng)",
            labels={"fill_rate": "Fill rate (z-score)", "label": ""}
        )
        fig1.add_vline(x=0, line_dash="dash", line_color="black", line_width=1)
        fig1.update_layout(yaxis=dict(autorange="reversed"), legend_title="Cụm",
                           height=450, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.write("**15 sản phẩm có stock_turnover thấp nhất**")
        top_turn = alert.sort_values("stock_turnover").head(15)
        fig2 = px.bar(
            top_turn, x="stock_turnover", y="label",
            color="Cluster_Name", color_discrete_map=COLORS,
            orientation="h",
            title="Stock turnover thấp nhất (hàng luân chuyển chậm)",
            labels={"stock_turnover": "Stock turnover (z-score)", "label": ""}
        )
        fig2.add_vline(x=0, line_dash="dash", line_color="black", line_width=1)
        fig2.update_layout(yaxis=dict(autorange="reversed"), legend_title="Cụm",
                           height=450, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Boxplot features theo cụm (giống visualization.ipynb cell cuối)
    st.subheader("📦 Phân Phối Feature theo Từng Cụm (Box Plot)")
    feat_choice = st.selectbox("Chọn feature:", FEATURE_COLS)

    fig_box = px.box(
        df, x="Cluster_Name", y=feat_choice,
        color="Cluster_Name",
        color_discrete_map=COLORS,
        category_orders={"Cluster_Name": CLUSTER_ORDER},
        points="outliers",
        title=f"Phân phối {feat_choice} theo cụm"
    )
    fig_box.add_hline(y=0, line_dash="dash", line_color="gray", line_width=0.8)
    fig_box.update_layout(showlegend=False, xaxis_title="Cụm", yaxis_title="z-score")
    st.plotly_chart(fig_box, use_container_width=True)
