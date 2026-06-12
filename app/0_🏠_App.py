import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(__file__))
from utils import style_excel

# Set page config
st.set_page_config(
    page_title="Phân Tích & Phân Cụm Sản Phẩm Bán Lẻ",
    page_icon="📦",
    layout="wide",
)

# ── Nạp giao diện CSS ───────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if not os.path.exists(css_path):
    css_path = os.path.join(os.path.dirname(__file__), "..", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.title("📦 Phân Tích & Phân Cụm Sản Phẩm Bán Lẻ")
st.write(
    "Hệ thống phân tích doanh số và phân cụm sản phẩm phục vụ tối ưu hóa chuỗi cung ứng và quản lý tồn kho."
)

st.write("Hệ thống sử dụng cấu trúc Streamlit Multi-page với 4 trang phân tích chuyên sâu:")

st.markdown("""
<style>
.feature-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    border-color: var(--primary-color);
}
.feature-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--primary-color);
}
.feature-content {
    font-size: 0.95rem;
    color: var(--text-color);
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 1. Dashboard</div>
        <div class="feature-content">
            Xem các chỉ số KPI, phân phối features và công cụ tìm kiếm sản phẩm.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-title">📉 3. Visualization</div>
        <div class="feature-content">
            Biểu đồ chuyên sâu — xu hướng doanh thu, phân bố theo category/region, cảnh báo sản phẩm cần xem lại.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🎯 2. Clustering</div>
        <div class="feature-content">
            Phân cụm sản phẩm bằng <b>Hierarchical Clustering (Ward)</b> và <b>K-Means (k=4)</b> với nhãn tự động: <i>Bán chạy, Tồn kho cao, Bán chậm, Ổn định</i>.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-title">📈 4. Analytics</div>
        <div class="feature-content">
            Nhận diện chi tiết top sản phẩm đặc biệt (bán chạy, bán chậm, tồn kho cao) và đưa ra các giải pháp/khuyến nghị tối ưu chuỗi cung ứng.
        </div>
    </div>
    """, unsafe_allow_html=True)

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
            st.dataframe(style_excel(df.head(10).style.format(precision=4)), hide_index=True, use_container_width=True)

        with tab2:
            st.dataframe(style_excel(df.describe().round(4).style.format(precision=4)), hide_index=False, use_container_width=True)

        with tab3:
            if os.path.exists(CLST_PATH):
                clst = pd.read_csv(CLST_PATH)
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Phân bố nhãn cụm (Hierarchical):**")
                    st.dataframe(style_excel(clst["Cluster_Name"].value_counts().reset_index()
                                 .rename(columns={"index": "Nhãn", "Cluster_Name": "Số lượng"}).style),
                                 hide_index=True, use_container_width=True)
                with col2:
                    st.write("**Mẫu kết quả clustering:**")
                    st.dataframe(style_excel(clst.head(10).style.format(precision=4)), hide_index=True, use_container_width=True)
            else:
                st.warning("Chưa có file `clustering_results.csv`. Hãy chạy `clustering.ipynb` trước.")

    except Exception as e:
        st.error(f"Có lỗi khi đọc dataset: {e}")
else:
    st.warning(f"Không tìm thấy file dữ liệu tại `{DATA_PATH}`. Hãy chạy `preprocessing.ipynb` trước.")
