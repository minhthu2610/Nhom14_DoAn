import streamlit as st
import pandas as pd
import os

# Set page config
st.set_page_config(
    page_title="Phân Tích & Phân Cụm Sản Phẩm Bán Lẻ",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Phân Tích & Phân Cụm Sản Phẩm Bán Lẻ")
st.write(
    "Hệ thống phân tích doanh số và phân cụm sản phẩm phục vụ tối ưu hóa chuỗi cung ứng và quản lý tồn kho."
)

st.markdown("""
Hệ thống sử dụng cấu trúc Streamlit Multi-page với 3 trang phân tích chuyên sâu:
1. **📊 Dashboard**: Xem các chỉ số KPI, phân phối features và công cụ tìm kiếm sản phẩm.
2. **🎯 Clustering**: Phân cụm sản phẩm bằng **Hierarchical Clustering (Ward)** và **K-Means (k=4)** với nhãn tự động: *Bán chạy*, *Tồn kho cao*, *Bán chậm*, *Ổn định*.
3. **📈 Visualization**: Biểu đồ chuyên sâu — xu hướng doanh thu, phân bố theo category/region, cảnh báo sản phẩm cần xem lại.
""")

# Path setup — file xử lý từ preprocessing.ipynb
BASE_DIR  = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "processed_retail_data.csv")
CLST_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "clustering_results.csv")

st.subheader("📁 Khám phá tập dữ liệu (Features sau chuẩn hóa)")

if os.path.exists(DATA_PATH):
    try:
        df = pd.read_csv(DATA_PATH)
        st.success(f"Đã tải thành công: **{len(df)}** cặp (product × store), **{len(df.columns)}** cột")

        tab1, tab2, tab3 = st.tabs(["📊 Xem Dataset", "📈 Thống kê mô tả", "🏷️ Kết quả Clustering"])

        with tab1:
            st.caption("Features đã được chuẩn hóa (StandardScaler) từ `preprocessing.ipynb`")
            st.dataframe(df.head(10), use_container_width=True)

        with tab2:
            st.dataframe(df.describe().round(4), use_container_width=True)

        with tab3:
            if os.path.exists(CLST_PATH):
                clst = pd.read_csv(CLST_PATH)
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Phân bố nhãn cụm (Hierarchical):**")
                    st.dataframe(clst["Cluster_Name"].value_counts().reset_index()
                                 .rename(columns={"index": "Nhãn", "Cluster_Name": "Số lượng"}),
                                 use_container_width=True)
                with col2:
                    st.write("**Mẫu kết quả clustering:**")
                    st.dataframe(clst.head(10), use_container_width=True)
            else:
                st.warning("Chưa có file `clustering_results.csv`. Hãy chạy `clustering.ipynb` trước.")

    except Exception as e:
        st.error(f"Có lỗi khi đọc dataset: {e}")
else:
    st.warning(f"Không tìm thấy file dữ liệu tại `{DATA_PATH}`. Hãy chạy `preprocessing.ipynb` trước.")
