````markdown
# Retail Product Clustering

Đồ án cuối kỳ môn Khai phá dữ liệu.

## Giới thiệu

Dự án xây dựng hệ thống phân cụm sản phẩm bán lẻ dựa trên hành vi bán hàng bằng các thuật toán Data Mining như Hierarchical Clustering và KMeans.

Dataset sử dụng là Online Retail II Dataset – dữ liệu bán lẻ thực tế từ UK, bao gồm thông tin giao dịch, sản phẩm, số lượng bán, giá bán và thời gian giao dịch.

Mục tiêu của dự án:
- Phân tích hành vi bán hàng của sản phẩm
- Gom cụm các sản phẩm có đặc điểm tương tự
- Hỗ trợ quản lý tồn kho
- Phát hiện sản phẩm bán chậm
- Hỗ trợ tối ưu nhập hàng

---

# Công nghệ sử dụng

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Streamlit
- Jupyter Notebook

---

# Cấu trúc project

```text
project/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── preprocessing.ipynb
│   ├── clustering.ipynb
│   └── visualization.ipynb
│
├── app/
│   ├── app.py
│   ├── pages/
│   └── assets/
│
├── models/
│
├── reports/
│
└── requirements.txt
````

---

# Các bước thực hiện

## 1. Tiền xử lý dữ liệu

* Xử lý missing values
* Xử lý duplicate
* Loại bỏ dữ liệu bất thường
* Clean StockCode không hợp lệ
* Chuẩn hóa dữ liệu bằng StandardScaler

## 2. Trích xuất đặc trưng hành vi bán hàng

* total_sales
* sale_frequency
* revenue
* sales_variance
* days_since_last_sale
* avg_inventory
* stock_turnover

## 3. Phân cụm sản phẩm

* Hierarchical Clustering
* Agglomerative Clustering
* KMeans
* Dendrogram
* Silhouette Score

## 4. Trực quan hóa dữ liệu

* Scatter Plot
* Heatmap
* Cluster Visualization
* Dashboard

## 5. Xây dựng ứng dụng web

* Hiển thị dataset
* Hiển thị kết quả phân cụm
* Dashboard thống kê
* Hỗ trợ phân tích sản phẩm

---

# Hướng dẫn cài đặt

## Clone project

```bash
git clone <github-repository>
```

## Tạo môi trường ảo

```bash
python -m venv venv
```

## Kích hoạt môi trường ảo

Windows PowerShell:

```bash
venv\Scripts\activate
```

## Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Hoặc:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn scipy streamlit jupyter
```

---

# Chạy Notebook

Mở thư mục notebooks/ và chạy:

* preprocessing.ipynb
* clustering.ipynb
* visualization.ipynb

---

# Chạy ứng dụng Streamlit

```bash
streamlit run app/app.py
```

Sau khi chạy thành công, truy cập:

```text
http://localhost:8501
```

---

# Thành viên nhóm

* Nguyễn Thị Minh Thư
* Nguyễn Minh Quân
* Nguyễn Xuân Phương
---

# Ghi chú

Dataset sử dụng:
Online Retail II Dataset (UK Retail Transactions)

```
```
