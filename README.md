# Retail Product Clustering

Đồ án cuối kỳ môn Khai phá dữ liệu.

## Giới thiệu

Dự án xây dựng hệ thống phân cụm sản phẩm bán lẻ dựa trên hành vi bán hàng bằng các thuật toán Data Mining như Hierarchical Clustering và KMeans.

Dataset sử dụng là **Retail Store Inventory Forecasting Dataset** – dữ liệu bán lẻ tổng hợp mô phỏng hoạt động quản lý tồn kho thực tế, bao gồm thông tin giao dịch, sản phẩm, số lượng bán, mức tồn kho thực tế, điểm đặt hàng lại và thời gian giao hàng từ nhà cung cấp.

Mục tiêu của dự án:
- Phân tích hành vi bán hàng của sản phẩm
- Gom cụm các sản phẩm có đặc điểm tương tự
- Hỗ trợ quản lý tồn kho
- Phát hiện sản phẩm bán chậm
- Hỗ trợ tối ưu nhập hàng

---

## Công nghệ sử dụng

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Streamlit
- Jupyter Notebook

---

## Cấu trúc project

```text
project/
│
├── data/
│   ├── raw/
│   │   └── retail_store_inventory.csv
│   └── processed/
│       └── processed_retail_data.csv
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
```

---

## Các bước thực hiện

### 1. Tiền xử lý dữ liệu

* Xử lý missing values
* Xử lý duplicate
* Loại bỏ dữ liệu bất thường (Quantity <= 0, Price <= 0)
* Xử lý outlier bằng phương pháp IQR trên các cột số
* Chuẩn hóa dữ liệu bằng StandardScaler

### 2. Trích xuất đặc trưng hành vi bán hàng

* `total_sales` – Tổng số lượng bán
* `sale_frequency` – Tần suất bán (số giao dịch)
* `revenue` – Doanh thu
* `sales_variance` – Độ biến động doanh số
* `days_since_last_sale` – Số ngày chưa bán
* `avg_inventory` – Tồn kho trung bình thực tế (lấy từ cột `Inventory_Level`)
* `stock_turnover` – Tốc độ quay vòng tồn kho

### 3. Phân cụm sản phẩm

* Hierarchical Clustering (Agglomerative, linkage='ward')
* KMeans
* Dendrogram + Elbow Method để xác định số cụm
* Silhouette Score để đánh giá

### 4. Trực quan hóa dữ liệu

* Scatter Plot
* Heatmap tương quan
* Cluster Visualization
* Dashboard

### 5. Xây dựng ứng dụng web

* Hiển thị dataset
* Hiển thị kết quả phân cụm
* Dashboard thống kê
* Hỗ trợ phân tích sản phẩm

---

## Hướng dẫn cài đặt

### Clone project

```bash
git clone <github-repository>
```

### Tạo môi trường ảo

```bash
python -m venv venv
```

### Kích hoạt môi trường ảo

Windows PowerShell:

```bash
venv\Scripts\activate
```

### Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Hoặc:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn scipy streamlit jupyter
```

---

## Chạy Notebook

Mở thư mục `notebooks/` và chạy theo thứ tự:

1. `preprocessing.ipynb`
2. `clustering.ipynb`
3. `visualization.ipynb`

---

## Chạy ứng dụng Streamlit

```bash
streamlit run app/app.py
```

Sau khi chạy thành công, truy cập:

```
http://localhost:8501
```

---

## Thành viên nhóm

* Nguyễn Thị Minh Thư – 2001230959
* Nguyễn Minh Quân – 2001230718
* Nguyễn Xuân Phương – 2001230703

---

## Ghi chú

Dataset sử dụng:
**Retail Store Inventory Forecasting Dataset**
Nguồn: https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset