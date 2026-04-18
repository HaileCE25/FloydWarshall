# 🚀 Floyd–Warshall Visualization Tool

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Status](https://img.shields.io/badge/Status-Completed-success)
![Algorithm](https://img.shields.io/badge/Algorithm-Floyd--Warshall-orange)
![UI](https://img.shields.io/badge/UI-Tkinter-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

Ứng dụng trực quan hóa thuật toán **Floyd–Warshall** để giải bài toán **All-Pairs Shortest Path** trên đồ thị có trọng số.

---

## 📸 Demo

### 🔹 Giao diện chính
![Main UI](docs/images/main_ui.png)

### 🔹 Ma trận qua từng bước k
![Step Visualization](docs/images/floyd_steps.png)

### 🔹 Trực quan đồ thị
![Graph](docs/images/graph.png)

---

## 🎥 Demo GIF
![Demo GIF](docs/gif/demo.gif)

---

## ✨ Features
- 📂 Đọc dữ liệu từ CSV (Edge list / Adjacency matrix)  
- 🧮 Tạo ma trận trọng số tự động  
- 🔁 Minh họa từng bước thuật toán Floyd–Warshall  
- 📊 Hiển thị:
  - Ma trận khoảng cách  
  - Ma trận lưu vết (Next matrix)  
- 🔍 Tìm đường đi ngắn nhất giữa hai đỉnh  
- 🌐 Trực quan hóa đồ thị  
- 💾 Xuất file CSV  

---

## 🛠️ Tech Stack
- Python  
- NumPy, Pandas  
- Tkinter  
- NetworkX, Matplotlib  
- Pillow (PIL)  

---

## 📂 Project Structure

FloydWarshall/
│── FloyWarshall.py
│── MST.csv
│── Weight_Matrix.csv
│
├── docs/
│ ├── images/
│ │ ├── main_ui.png
│ │ ├── floyd_steps.png
│ │ └── graph.png
│ └── gif/
│ └── demo.gif
│
└── README.md


---

## 📥 Input Format

### 1. Edge List
```csv
From,To,Distance
City1,City2,10
City2,City3,5
2. Adjacency Matrix
CSV dạng ma trận vuông
0, rỗng hoặc NaN → ∞
▶️ Usage
python FloyWarshall.py
Quy trình:
Chọn dữ liệu đầu vào
Nhập số đỉnh
Chạy thuật toán
Duyệt từng bước k
Tìm đường đi ngắn nhất
📤 Output
Ma trận khoảng cách cuối
Đường đi ngắn nhất
File:
Weight_Matrix.csv
Weight_Matrix_kxk.csv
⚠️ Notes
Có kiểm tra chu trình âm
Nên dùng format City1, City2, ...
Dữ liệu sai sẽ báo lỗi
🔮 Future Work
Thêm Dijkstra, Bellman-Ford
Cải thiện UI/UX
Tối ưu hiệu năng
📄 License

MIT License


---

Nếu bạn muốn “xịn hơn nữa”, mình có thể làm thêm:
- :contentReference[oaicite:0]{index=0}
- Hoặc :contentReference[oaicite:1]{index=1} 👍
