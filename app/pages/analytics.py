import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Nhận Diện & Khuyến Nghị Sản Phẩm", page_icon="📈", layout="wide")

st.title("📈 Phân Tích Chuyên Sâu & Giải Pháp Hỗ Trợ Tồn Kho")
st.write("Khám phá các sản phẩm nổi bật, nhận diện các vấn đề về bán hàng và xem đề xuất tự động tối ưu hóa tồn kho.")

# Loader helper
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
            'total_sales': np.random.normal(0.2, 1.2, 40),
            'sale_frequency': np.random.normal(0.1, 0.9, 40),
            'revenue': np.random.normal(0.3, 1.1, 40),
            'sales_variance': np.random.normal(-0.04, 0.05, 40),
            'days_since_last_sale': np.random.normal(0.5, 1.1, 40),
            'avg_inventory': np.random.normal(0.1, 1.3, 40),
            'stock_turnover': np.random.normal(-0.1, 0.9, 40)
        }
        return pd.DataFrame(mock_data)

df = load_data()

# Categorizations tabs
st.subheader("🔍 Phân Loại Nhận Diện Sản Phẩm Đặc Biệt")
tab_best, tab_slow, tab_high_inv = st.tabs([
    "🔥 Sản phẩm Bán chạy (Bestsellers)", 
    "💤 Sản phẩm Bán chậm (Slow Movers)", 
    "📦 Sản phẩm Tồn kho cao (High Inventory)"
])

with tab_best:
    st.write("Top sản phẩm có doanh số bán ra (`total_sales`) cao nhất hệ thống:")
    best_df = df.sort_values(by="total_sales", ascending=False).head(5)
    st.dataframe(best_df, use_container_width=True)
    
    # Chart
    fig_best = px.bar(
        best_df, 
        x="Product_ID", 
        y="total_sales", 
        color="revenue", 
        title="Top 5 Sản phẩm Bán chạy nhất",
        color_continuous_scale=px.colors.sequential.Darkmint
    )
    st.plotly_chart(fig_best, use_container_width=True)

with tab_slow:
    st.write("Top sản phẩm có doanh số bán ra (`total_sales`) thấp nhất hệ thống:")
    slow_df = df.sort_values(by="total_sales", ascending=True).head(5)
    st.dataframe(slow_df, use_container_width=True)
    
    # Chart
    fig_slow = px.bar(
        slow_df, 
        x="Product_ID", 
        y="total_sales", 
        color="days_since_last_sale", 
        title="Top 5 Sản phẩm Bán chậm nhất",
        color_continuous_scale=px.colors.sequential.Oranges
    )
    st.plotly_chart(fig_slow, use_container_width=True)

with tab_high_inv:
    st.write("Top sản phẩm có mức tồn kho trung bình (`avg_inventory`) cao nhất:")
    high_inv_df = df.sort_values(by="avg_inventory", ascending=False).head(5)
    st.dataframe(high_inv_df, use_container_width=True)
    
    # Chart
    fig_high = px.bar(
        high_inv_df, 
        x="Product_ID", 
        y="avg_inventory", 
        color="stock_turnover", 
        title="Top 5 Sản phẩm có Tồn kho cao nhất",
        color_continuous_scale=px.colors.sequential.Reds
    )
    st.plotly_chart(fig_high, use_container_width=True)

# Recommendations Section
st.markdown("---")
st.subheader("💡 Đề Xuất Tự Động Định Hướng Quản Lý Tồn Kho")
st.write("Hệ thống tự động rà soát chỉ số vận hành và phân loại rủi ro chuỗi cung ứng dựa trên dữ liệu sản phẩm:")

# Rule-based calculation helper for table
recommendations = []

# Tự động tính các mốc Thấp (25%) và Cao (75%) từ dữ liệu thực tế
q_sales_high = df['total_sales'].quantile(0.75)
q_sales_low = df['total_sales'].quantile(0.25)

q_inv_high = df['avg_inventory'].quantile(0.75)
q_inv_low = df['avg_inventory'].quantile(0.25)

q_turnover_high = df['stock_turnover'].quantile(0.75)
q_turnover_low = df['stock_turnover'].quantile(0.25)

for idx, row in df.iterrows():
    p_id = row['Product_ID']
    sales = row['total_sales']
    inv = row['avg_inventory']
    turnover = row['stock_turnover']
    rec = "Chưa có đề xuất đặc biệt"
    status = "Bình thường"
    color_label = "gray"
    
    # Rule engine
    if sales > q_sales_high and inv < q_inv_low:
        rec = "⚠️ Doanh số cao nhưng mức tồn kho rất thấp. Bổ sung hàng hóa gấp để tránh hụt kho (Out-of-stock)!"
        status = "Bổ sung khẩn cấp"
        color_label = "red"
    elif sales < q_sales_low and inv > q_inv_high:
        rec = "💸 Bán rất chậm nhưng tồn kho đang quá cao. Cần thực hiện khuyến mãi, giảm giá sốc hoặc gộp combo thanh lý giải phóng mặt bằng kho."
        status = "Khuyến mãi thanh lý"
        color_label = "amber"
    elif turnover < q_turnover_low and inv > q_inv_high:
        rec = "🚨 Vòng quay hàng tồn kho cực kì thấp, rủi ro đọng vốn cao. Ngừng đặt mua thêm mã hàng này khẩn cấp, đánh giá lại nhu cầu thị trường."
        status = "Ngừng mua mới"
        color_label = "red"
    elif turnover > q_turnover_high and inv < q_inv_low:
        rec = "✅ Vòng quay kho rất tốt, sản phẩm lưu chuyển nhanh. Duy trì lịch trình cung ứng ổn định hiện tại."
        status = "Duy trì cung ứng"
        color_label = "green"
        
    recommendations.append({
        "Product_ID": p_id,
        "Total Sales": f"{sales:.2f}",
        "Avg Inventory": f"{inv:.2f}",
        "Turnover Rate": f"{turnover:.2f}",
        "Phân nhóm vận hành": status,
        "Khuyến nghị chuỗi cung ứng": rec
    })

rec_df = pd.DataFrame(recommendations)

# Interactive filters for recommendations
action_filter = st.selectbox(
    "Lọc sản phẩm theo Khuyến nghị hành động:",
    ["Tất cả", "Bổ sung khẩn cấp", "Khuyến mãi thanh lý", "Ngừng mua mới", "Duy trì cung ứng"]
)

if action_filter != "Tất cả":
    show_rec_df = rec_df[rec_df["Phân nhóm vận hành"] == action_filter]
else:
    show_rec_df = rec_df

st.write(f"Đang hiển thị **{len(show_rec_df)}** sản phẩm cần lưu ý:")
st.dataframe(show_rec_df, use_container_width=True)

# Custom metrics charts
# Custom metrics charts
st.markdown("---")
st.subheader("🛠️ Công cụ Phân tích Ma trận Vòng quay vs Doanh số")

# Fix lỗi số âm: Tạo cột giá trị tuyệt đối cho kích thước bong bóng
df["inventory_size"] = df["avg_inventory"].abs()

fig_matrix = px.scatter(
    df,
    x="total_sales",
    y="stock_turnover",
    size="inventory_size",  # <-- Đổi từ "avg_inventory" sang cột vừa tạo
    color="days_since_last_sale",
    hover_name="Product_ID",
    text="Product_ID",
    labels={
        "total_sales": "Doanh số (Doanh thu bán ra)",
        "stock_turnover": "Vòng quay kho (Stock Turnover)"
    },
    title="Ma trận Vận hành sản phẩm (Nhấn kéo để xem vùng chi tiết)"
)
fig_matrix.update_traces(textposition='top center')
st.plotly_chart(fig_matrix, use_container_width=True)