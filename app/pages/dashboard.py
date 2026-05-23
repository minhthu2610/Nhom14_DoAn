import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Dashboard Tổng Quan", page_icon="📊", layout="wide")

st.title("📊 Dashboard Phân Tích Tổng Quan")
st.write("Màn hình hiển thị các chỉ số hiệu suất bán hàng tổng quan và phân bổ chỉ số vận hành sản phẩm.")

# Load data helper
# Thay file đã chuẩn hóa thành file số liệu gốc
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "online_retail_II.csv")

@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        # Fallback simulation
        import numpy as np
        np.random.seed(42)
        mock_ids = [str(i) for i in range(10001, 10041)]
        mock_data = {
            'Product_ID': mock_ids,
            'total_sales': np.random.uniform(10, 1000, 40),
            'sale_frequency': np.random.uniform(1, 50, 40),
            'revenue': np.random.uniform(100, 5000, 40),
            'sales_variance': np.random.normal(0, 0.05, 40),
            'days_since_last_sale': np.random.uniform(1, 30, 40),
            'avg_inventory': np.random.uniform(10, 500, 40), 
            'stock_turnover': np.random.uniform(0.5, 5.0, 40)
        }
        return pd.DataFrame(mock_data)

df = load_data()

if "avg_inventory" in df.columns:
    df["inventory_size"] = df["avg_inventory"].abs()
else:
    df["inventory_size"] = 10

# KPI Metric Cards
st.subheader("💡 Chỉ Số Vận Hành Thiết Yếu (Normalized Metrics)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Tổng số sản phẩm", value=len(df), delta=None)
with col2:
    st.metric(label="Doanh số trung bình (sales)", value=f"{df['total_sales'].mean():.3f}", delta=None)
with col3:
    st.metric(label="Vòng quay kho trung bình (turnover)", value=f"{df['stock_turnover'].mean():.3f}", delta=None)
with col4:
    st.metric(label="Days Since Last Sale (Mean)", value=f"{df['days_since_last_sale'].mean():.3f}", delta=None)

st.markdown("---")

# Row 1: Charts
st.subheader("📈 Phân Tích Mối Liên Hệ Đa Biến")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("**Biểu đồ phân phối doanh số (Total Sales Distribution)**")
    fig_sales = px.histogram(
        df, 
        x="total_sales", 
        nbins=15, 
        color_discrete_sequence=["#2E86C1"],
        opacity=0.8,
        marginal="rug"
    )
    fig_sales.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_sales, use_container_width=True)

with chart_col2:
    st.write("**Doanh thu vs. Tần suất bán hàng (Revenue vs. Sale Frequency)**")
    df["inventory_size"] = df["avg_inventory"].abs()
    fig_scatter = px.scatter(
        df, 
        x="sale_frequency", 
        y="revenue", 
        size="inventory_size", 
        hover_name="Product_ID",
        color="total_sales",
        color_continuous_scale=px.colors.sequential.Bluered,
    )
    fig_scatter.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# Row 2: Detailed Search & Stats
st.markdown("---")
st.subheader("🔍 Tìm Kiếm & So Sánh Sản Phẩm")
search_id = st.text_input("Nhập mã Product_ID cần tra cứu nhanh:", "").strip()

if search_id:
    matched = df[df["Product_ID"].astype(str).str.contains(search_id)]
    if not matched.empty:
        st.write(f"Tìm thấy **{len(matched)}** sản phẩm khớp:")
        st.dataframe(matched, use_container_width=True)
    else:
        st.warning("Không tìm thấy mã sản phẩm phù hợp. Thử lại với mã khác nhé!")
else:
    st.write("Sử dụng bảng dưới đây để xem nhanh top 10 sản phẩm có doanh số bán hàng (total_sales) lớn nhất:")
    df_sorted = df.sort_values(by="total_sales", ascending=False)
    st.dataframe(df_sorted.head(10), use_container_width=True)
