import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(page_title="Phân Cụm Sản Phẩm", page_icon="🎯", layout="wide")

st.title("🎯 Phân Cụm K-Means & Nhận Diện Nhóm Sản Phẩm")
st.write("Sử dụng thuật toán học máy K-Means để phân loại các sản phẩm dựa trên các đặc trưng vận hành nâng cao.")

# Loader
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "online_retail_II.csv")

@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        # Fallback simulation data
        np.random.seed(42)
        mock_ids = [str(i) for i in range(10001, 10051)]
        mock_data = {
            'Product_ID': mock_ids,
            'total_sales': np.random.normal(0, 1, 50),
            'sale_frequency': np.random.normal(0, 1, 50),
            'revenue': np.random.normal(0, 1, 50),
            'sales_variance': np.random.normal(-0.04, 0.05, 50),
            'days_since_last_sale': np.random.normal(0.5, 1.1, 50),
            'avg_inventory': np.random.normal(0.1, 1.3, 50),
            'stock_turnover': np.random.normal(-0.1, 1.0, 50)
        }
        return pd.DataFrame(mock_data)

df = load_data().copy()

# Sidebar controls for clustering
st.sidebar.subheader("⚙️ Cấu Hình Thuật Toán")
k_val = st.sidebar.slider("Chọn số lượng cụm (K):", min_value=2, max_value=6, value=3)

clustering_features = st.sidebar.multiselect(
    "Đặc trưng tập trung phân tích:",
    options=["total_sales", "sale_frequency", "revenue", "sales_variance", "days_since_last_sale", "avg_inventory", "stock_turnover"],
    default=["total_sales", "revenue", "stock_turnover"]
)

if len(clustering_features) < 2:
    st.error("⚠️ Hãy chọn ít nhất **2 đặc trưng** để hệ thống có thể thực hiện thuật toán trực quan hóa phân cụm.")
else:
    # K-Means execution with fallback
    X = df[clustering_features].values
    
    # Standardize data in Python manually (robustness)
    X_std = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
    
    kmeans_success = False
    clusters = []
    
    try:
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=k_val, random_state=42, n_init=10)
        clusters = km.fit_predict(X_std)
        kmeans_success = True
    except ImportError:
        # Simple pure Python K-Means fallback
        def fallback_kmeans(data, k_clusters, max_iters=20):
            # Pick random centroids
            np.random.seed(42)
            centroids = data[np.random.choice(data.shape[0], k_clusters, replace=False)]
            for _ in range(max_iters):
                # Calculate distances and assign clusters
                distances = np.linalg.norm(data[:, np.newaxis] - centroids, axis=2)
                labels_pred = np.argmin(distances, axis=1)
                
                # Update centroids
                new_centroids = np.array([data[labels_pred == c].mean(axis=0) if len(data[labels_pred == c]) > 0 else Centroids[c] for c in range(k_clusters)])
                if np.allclose(centroids, new_centroids):
                    break
                centroids = new_centroids
            return labels_pred
            
        clusters = fallback_kmeans(X_std, k_val)
        kmeans_success = True

    df["Cluster"] = [f"Cụm {c}" for c in clusters]
    
    # Layout sections
    st.subheader("📊 Kết Quả Phân Cụm Sản Phẩm")
    
    # Row 1: Charts
    col_chart_left, col_chart_right = st.columns([2, 1])
    
    with col_chart_left:
        st.write("**Biểu đồ phân tán không gian chuẩn hóa (Clustering Scatter Plot)**")
        x_axis = st.selectbox("Tính chất Trục X:", clustering_features, index=0)
        y_axis = st.selectbox("Tính chất Trục Y:", clustering_features, index=min(1, len(clustering_features)-1))
        
        fig_clusters = px.scatter(
            df, 
            x=x_axis, 
            y=y_axis, 
            color="Cluster", 
            hover_name="Product_ID",
            symbol="Cluster",
            color_discrete_sequence=px.colors.qualitative.Safe,
            hover_data=clustering_features
        )
        fig_clusters.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(fig_clusters, use_container_width=True)
        
    with col_chart_right:
        st.write("**Tỷ lệ phân phối số lượng sản phẩm mỗi cụm**")
        cluster_counts = df["Cluster"].value_counts().reset_index()
        cluster_counts.columns = ["Cluster", "Count"]
        
        fig_pie = px.pie(
            cluster_counts, 
            values="Count", 
            names="Cluster", 
            color="Cluster", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    # Row 2: Filtering and table
    st.subheader("🔍 Bộ Lọc & Tra Cứu Danh Sách Sản Phẩm Theo Cụm")
    
    cluster_options = ["Tất cả cụm"] + sorted(df["Cluster"].unique().tolist())
    selected_cluster = st.selectbox("Chọn cụm cần hiển thị chi tiết:", cluster_options)
    
    if selected_cluster == "Tất cả cụm":
        filtered_df = df
    else:
        filtered_df = df[df["Cluster"] == selected_cluster]
        
    st.write(f"Đang hiển thị **{len(filtered_df)}** sản phẩm thỏa mãn điều kiện lọc:")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download helper
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tải xuống danh sách cụm này (CSV)",
        data=csv_data,
        file_name=f"cluster_products_{selected_cluster.replace(' ', '_')}.csv",
        mime="text/csv"
    )
