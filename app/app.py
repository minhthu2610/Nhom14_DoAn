import streamlit as st
import pandas as pd
import os

# Set page config
st.set_page_config(
    page_title="Product Analytics & Clustering Workspace",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Product Analytics & Clustering Workspace")
st.write(
    "Chào mừng bạn đến với hệ thống phân tích doanh số và phân cụm sản phẩm phục vụ tối ưu hóa chuỗi cung ứng và tồn kho."
)

st.markdown("""
Hệ thống này sử dụng cấu trúc Streamlit Multi-page để tổ chức các trang phân tích chuyên sâu:
1. **📊 Dashboard**: Xem các chỉ số KPI, hiệu suất bán hàng tổng quan và phân bổ của tất cả sản phẩm.
2. **🎯 Clustering**: Thực hiện phân cụm sản phẩm dựa trên thuật toán **K-Means** với bộ chỉ số vận hành nâng cao.
3. **📈 Analytics**: Hỗ trợ nhận diện sản phẩm bán chạy, bán chậm, tồn kho cao và đưa ra giải pháp quản lý.
""")

# Path setup
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "processed_retail_data.csv")

st.subheader("📁 Khám phá tập dữ liệu mẫu (Sample Dataset)")

if os.path.exists(DATA_PATH):
    try:
        df = pd.read_csv(DATA_PATH)
        st.success(f"Đã tải thành công tập dữ liệu: {len(df)} dòng và {len(df.columns)} cột")
        
        tab1, tab2 = st.tabs(["📊 Xem Dataset", "📈 Thống kê mô tả"])
        with tab1:
            st.dataframe(df.head(10), use_container_width=True)
        with tab2:
            st.dataframe(df.describe(), use_container_width=True)
    except Exception as e:
        st.error(f"Có lỗi khi đọc file dataset: {e}")
