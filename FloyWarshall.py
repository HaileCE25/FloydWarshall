import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image, ImageTk, ImageFilter
import copy

INF = np.inf
floyd_tables = []
current_step = 0
next_node = None
df_state = {
    "weight_df": None,
    "cities": [],
    "city_to_idx": {},
    "n": 0
}
original_state = {}
# =====================================================================
# ĐỌC VÀ XỬ LÝ DATASET
# =====================================================================
def load_dataset(filepath):
    global df_state, original_state
    try:
        test_df = pd.read_csv(filepath, sep=None, engine='python', nrows=0)
        
        if 'From' in test_df.columns and 'To' in test_df.columns:
            df = pd.read_csv(filepath, sep=None, engine='python')
            raw_cities = pd.concat([df['From'], df['To']]).unique()
            if all(str(c).startswith('City') for c in raw_cities):
                cities = sorted(raw_cities, key=lambda x: int(str(x).replace('City', '')))
            else:
                cities = sorted(raw_cities)
                
            city_to_idx = {city: i for i, city in enumerate(cities)}
            n = len(cities)
            dist = np.full((n, n), INF)
            np.fill_diagonal(dist, 0)
            
            for row in df.itertuples():
                u, v, w = city_to_idx[row.From], city_to_idx[row.To], row.Distance
                dist[u][v] = dist[v][u] = w 

        else:
            df = pd.read_csv(filepath, sep=';', index_col=0, encoding='utf-8-sig')
            cities = df.index.astype(str).tolist()
            city_to_idx = {city: i for i, city in enumerate(cities)}
            n = len(cities)
            dist = df.to_numpy(dtype=float)
            
            for i in range(n):
                for j in range(n):
                    if i != j and (dist[i, j] == 0 or np.isnan(dist[i, j])):
                        dist[i, j] = INF
                    elif i == j:
                        dist[i, j] = 0

        weight_df = pd.DataFrame(dist, index=cities, columns=cities)
        weight_df.replace(np.inf, "INF").to_csv("Weight_Matrix.csv", encoding='utf-8-sig')
        
        df_state = {"weight_df": weight_df, "cities": cities, "city_to_idx": city_to_idx, "n": n}
        original_state = df_state.copy()
        
        print(f"Đã xử lý xong {n} đỉnh. Ma trận đã được lưu vào Weight_Matrix.csv")

    except Exception as e:
        messagebox.showerror("Lỗi dữ liệu", f"Không thể xử lý file này: {e}")
# =========================================================
# THUẬT TOÁN FLOYD - WARSHALL
# =========================================================
def floyd_warshall(matrix):
    size = len(matrix)
    dist = np.copy(matrix)
    next_node = [[j if (i != j and dist[i][j] < INF) else None 
                  for j in range(size)] for i in range(size)]
    tables = [np.copy(dist)]
    for k in range(size):
        for i in range(size):
            for j in range(size):
                new_dist = dist[i][k] + dist[k][j]
                if new_dist < dist[i][j]:
                    dist[i][j] = new_dist
                    next_node[i][j] = next_node[i][k]
        tables.append(np.copy(dist))
    return dist, next_node, tables
# =========================================================
# ĐƯỜNG ĐI NGẮN NHẤT
# =========================================================
def get_path(u, v):
    if next_node[u][v] is None:
        return []
    path = [u]
    while u != v:
        u = next_node[u][v]
        path.append(u)
    return path

def handle_find_path():
    src, dst = src_entry.get().strip(), dst_entry.get().strip()
    c_idx = df_state["city_to_idx"]
    if src not in c_idx or dst not in c_idx:
        messagebox.showerror("Lỗi", "Thành phố không tồn tại. Vui lòng nhập đúng tên (VD: City1).")
        return
    u, v = c_idx[src], c_idx[dst]
    path = get_path(u, v)
    if not path:
        messagebox.showinfo("Kết quả", "Không có đường đi giữa 2 thành phố này.")
        return
    names = [df_state["cities"][i] for i in path]
    total_dist = floyd_tables[-1][u][v]   
    show_custom_path(names, total_dist, path, u, v)
# =========================================================
# XUẤT ĐỒ THỊ
# =========================================================
def visualize_graph(mode="original", path=None, src=None, dst=None):
    try:
        if mode == "original":
            k_val = int(entry.get())
            data = df_state["weight_df"].iloc[:k_val, :k_val].values
            title = f"Đồ thị gốc ({k_val} đỉnh)"
            size = k_val
        elif mode == "floyd":
            data = floyd_tables[current_step]
            title = f"Đồ thị tại bước k = {current_step}"
            size = len(data)
        else:
            raise ValueError("Mode không hợp lệ")

        G = nx.Graph()
        for i in range(size):
            for j in range(i + 1, size):
                w = data[i][j]
                if not np.isinf(w):
                    G.add_edge(i, j, weight=w)
        pos = nx.spring_layout(G, seed=42)

        def get_node_color(i):
            if src is not None and i == src: return "#4CAF50"
            if dst is not None and i == dst: return "#AB47BC"
            if path and i in path: return "#FF7043"
            if mode == "floyd" and i == current_step - 1: return "#66BB6A"
            return "#4FC3F7"
            
        node_colors = [get_node_color(i) for i in range(size)]
        if path:
            path_edges = set(zip(path[:-1], path[1:])) | set(zip(path[1:], path[:-1]))
            edge_colors = ["red" if e in path_edges else "#BDBDBD" for e in G.edges()]
        else:
            edge_colors = ["#BDBDBD"] * len(G.edges())

        plt.figure(figsize=(10, 7))
        nx.draw(
            G,
            pos,
            labels={i: df_state["cities"][i] for i in range(size)},
            node_color=node_colors,
            node_size=900,
            font_size=9,
            edge_color=edge_colors,
            width=1.5 if path else 1
        )
        
        edge_labels = {
            k: int(v) if not np.isinf(v) else "∞"
            for k, v in nx.get_edge_attributes(G, "weight").items()
        }
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=9
        )
        plt.title(title, fontweight="bold")
        plt.show()
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể vẽ đồ thị: {e}")
# =========================================================
# HIỂN THỊ MA TRẬN/ ĐƯỜNG ĐI NGẮN NHẤT
# =========================================================  
def get_valid_subset():
    try:
        k = int(entry.get())
        if not (1 <= k <= df_state["n"]):
            messagebox.showerror("Lỗi", f'Nhập số từ 1 đến {df_state["n"]}')
            return None, None
        return k, df_state["weight_df"].iloc[:k, :k]
    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ")
        return None, None

def run_floyd():
    global floyd_tables, current_step, next_node
    k, subset = get_valid_subset()
    if subset is None: return 
    
    try:
        dist, next_node, floyd_tables = floyd_warshall(subset.values)        
        current_step = 0
        has_negative_cycle = False
        final_matrix = floyd_tables[-1]
        for i in range(len(final_matrix)):
            if final_matrix[i][i] < 0:
                has_negative_cycle = True
                break
                
        if has_negative_cycle:
            messagebox.showwarning(
                "Cảnh Báo", 
                "Phát hiện chu trình âm trong đồ thị!\n",
                "Vui lòng kiểm tra lại dữ liệu nhập."
            )
            return
        show_floyd_table(current_step)
        frame_nav.pack(pady=5, padx=10, fill="x", before=frame_table)
        frame_path.pack(pady=5, padx=10, fill="x", before=frame_table)
        lbl_max_step.config(text=f"/ {len(floyd_tables)-1}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không chạy được Floyd\n{e}")

def show_matrix():
    k, subset = get_valid_subset()
    if subset is None: return
    frame_nav.pack_forget()
    frame_path.pack_forget()
    subset_display = subset.map(lambda x: "∞" if np.isinf(x) else int(x))
    text.delete("1.0", tk.END)
    text.insert(tk.END, subset_display.to_string())

def export_matrix():
    k, subset = get_valid_subset()
    if subset is None: return
    filename = f"Weight_Matrix_{k}x{k}.csv"
    subset.replace(np.inf, "INF").to_csv(filename)
    messagebox.showinfo("Thành công", f"Đã xuất {filename}")

def show_floyd_table(step):
    text.delete("1.0", tk.END)
    table, prev = floyd_tables[step], floyd_tables[step-1] if step > 0 else None
    size, cities = len(table), df_state["cities"]
    header_w = max([len(str(c)) for c in cities]) + 2 if cities else 10
    col_w = [max(len(str(c)) + 2, 9) for c in cities]

    text.insert(tk.END, f"Ma trận thứ k = {step}\n\n")
    start_idx = text.index(tk.INSERT)
    
    text.insert(tk.END, "".ljust(header_w))
    for j in range(size):
        text.insert(tk.END, str(cities[j]).ljust(col_w[j]))
    text.insert(tk.END, "\n")
    
    if step > 0:
        t = step - 1
        text.tag_add("col_highlight", f"{start_idx}+{header_w + sum(col_w[:t])}c", f"{start_idx}+{header_w + sum(col_w[:t+1])}c")
        
    for i in range(size):
        r_start = text.index(tk.INSERT)
        text.insert(tk.END, str(cities[i]).ljust(header_w))
        if step > 0 and i == step - 1:
            text.tag_add("row_highlight", r_start, text.index(tk.INSERT))
            
        for j in range(size):
            val = table[i][j]
            cell_str = "∞" if np.isinf(val) else str(int(val))
            is_changed = False
            if step > 0 and prev is not None and table[i][j] < prev[i][j]:
                old_val = prev[i][j]
                old_str = "∞" if np.isinf(old_val) else str(int(old_val))
                cell_str = f"{cell_str}/{old_str}"
                is_changed = True
                
            c_start = text.index(tk.INSERT)
            text.insert(tk.END, cell_str.ljust(col_w[j]))
            c_end = text.index(tk.INSERT)
            
            if step > 0:
                t = step - 1
                if i == t and j == t: text.tag_add("overlap", c_start, c_end)
                elif i == t: text.tag_add("row_highlight", c_start, c_end)
                elif j == t: text.tag_add("col_highlight", c_start, c_end)
                elif is_changed: text.tag_add("changed", c_start, c_end)                
        text.insert(tk.END, "\n")      
        
    for tag, color in [("row_highlight", "#FFD54F"), ("col_highlight", "#4FC3F7"), 
                       ("overlap", "#66BB6A"), ("changed", "#FF8A80")]:
        text.tag_config(tag, background=color)


def show_custom_path(path_names, total_dist, path_idx, src, dst):
    popup = tk.Toplevel(root)
    popup.title("Shortest Path Result")
    popup.geometry(f"520x380+{root.winfo_x() + 50}+{root.winfo_y() + 50}")
    popup.configure(bg="#f8f9fa")
    def add_lbl(txt, font=("Arial", 10, "bold"), fg="black", pady=0):
        tk.Label(popup, text=txt, font=font, fg=fg, bg="#f8f9fa").pack(anchor="w" if fg=="black" else "center", padx=20, pady=pady)
    add_lbl("========== ĐƯỜNG ĐI NGẮN NHẤT ==========", ("Consolas", 12, "bold"), "#1565C0", 8)
    add_lbl("Đường đi:")
    r_frame = tk.Frame(popup, bg="#f8f9fa")
    r_frame.pack(fill="x", padx=20, pady=5)
    r_scroll = tk.Scrollbar(r_frame, orient="horizontal")
    r_scroll.pack(side="bottom", fill="x")
    r_box = tk.Text(r_frame, height=1, font=("Consolas", 11), wrap="none", xscrollcommand=r_scroll.set)
    r_box.pack(fill="x")
    r_scroll.config(command=r_box.xview)
    r_box.insert(tk.END, " → ".join(path_names))
    r_box.config(state="disabled")
    add_lbl("Các đoạn:")
    s_box = tk.Text(popup, height=5, font=("Consolas", 10), relief="flat")
    s_box.pack(fill="x", padx=20)
    data, c = df_state["weight_df"].values, df_state['cities']
    segments = [f"{c[path_idx[i]]} → {c[path_idx[i+1]]} ({int(data[path_idx[i]][path_idx[i+1]])})" for i in range(len(path_idx)-1)]
    s_box.insert(tk.END, "\n".join(segments))
    s_box.config(state="disabled")
    stats = f"Số nhánh phải đi: {len(path_idx)-1}\nSố thành phố trung gian: {max(0, len(path_idx)-2)}\nTổng khoảng cách: {int(total_dist)} km"
    add_lbl(stats, ("Consolas", 10), "#2E7D32", 8)
    btn_frame = tk.Frame(popup, bg="#f8f9fa")
    btn_frame.pack(side="bottom", pady=10)
    tk.Button(btn_frame, text="Hiển thị đồ thị", command=lambda: visualize_graph(path=path_idx, src=src, dst=dst), bg="#66BB6A", fg="white", font=("Arial",10,"bold"), padx=15, bd=0).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Đóng", command=popup.destroy, bg="#1976D2", fg="white", font=("Arial",10,"bold"), padx=15, bd=0).pack(side="left", padx=10)

def show_next_popup():
    if next_node is None:
        messagebox.showerror("Lỗi", "Chưa chạy Floyd-Warshall!")
        return

    popup = tk.Toplevel(root)
    popup.title("Ma trận lưu vết")
    popup.geometry("700x450")

    frame = tk.Frame(popup)
    frame.pack(fill="both", expand=True)

    scroll_y = tk.Scrollbar(frame)
    scroll_y.pack(side="right", fill="y")

    scroll_x = tk.Scrollbar(frame, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    text_box = tk.Text(
        frame,
        font=("Consolas",10),
        wrap="none",
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )
    text_box.pack(fill="both", expand=True)

    scroll_y.config(command=text_box.yview)
    scroll_x.config(command=text_box.xview)

    cities = df_state["cities"]
    size = len(next_node)

    # Tính độ rộng dựa trên tên thành phố
    header_w = max([len(str(c)) for c in cities]) + 2 if cities else 10
    col_w = [max(len(str(c)) + 2, 8) for c in cities]

    text_box.insert(tk.END,"Ma trận lưu vết cuối cùng\n\n")

    text_box.insert(tk.END,"".ljust(header_w))
    for j in range(size):
        start = text_box.index(tk.INSERT)
        text_box.insert(tk.END, str(cities[j]).ljust(col_w[j]))
        end = text_box.index(tk.INSERT)
        text_box.tag_add("col_header",start,end)

    text_box.insert(tk.END,"\n")

    for i in range(size):
        start = text_box.index(tk.INSERT)
        text_box.insert(tk.END, str(cities[i]).ljust(header_w))
        end = text_box.index(tk.INSERT)
        text_box.tag_add("row_header",start,end)

        for j in range(size):
            if next_node[i][j] is None:
                val = "-"
            else:
                val = str(cities[next_node[i][j]])

            text_box.insert(tk.END,val.ljust(col_w[j]))

        text_box.insert(tk.END,"\n")

    text_box.tag_config("col_header", foreground="#1565C0", font=("Consolas",10,"bold"))
    text_box.tag_config("row_header", foreground="#2E7D32", font=("Consolas",10,"bold"))
# =========================================================
# LƯU BƯỚC THỨ K
# =========================================================
def go_to_step():
    global current_step
    try:
        step_val = int(step_entry.get())
        if 0 <= step_val < len(floyd_tables):
            current_step = step_val
            show_floyd_table(current_step)
        else:
            messagebox.showerror("Lỗi", f"Bước k phải từ 0 đến {len(floyd_tables)-1}")
    except:
        messagebox.showerror("Lỗi", "Vui lòng nhập số bước hợp lệ")
# =========================================================
# UI DISPLAY
# =========================================================
def next_step():
    global current_step
    if current_step < len(floyd_tables)-1:
        current_step += 1
        show_floyd_table(current_step)

def prev_step():
    global current_step
    if current_step > 0:
        current_step -= 1
        show_floyd_table(current_step)

def auto_play():
    global current_step
    if current_step < len(floyd_tables)-1:
        current_step += 1
        show_floyd_table(current_step)
        root.after(800, auto_play)
# =========================================================
# UI INTRO
# =========================================================
def show_intro():
    intro_frame = tk.Frame(root)
    intro_frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(intro_frame, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    img_original = Image.open("background.jpg")
    def update_ui(event=None):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10: return

        bg_resized = img_original.resize((w, h), Image.LANCZOS)
        bg_tk = ImageTk.PhotoImage(bg_resized)
        canvas.image = bg_tk
        canvas.delete("all")
        canvas.create_image(0, 0, image=bg_tk, anchor="nw")

        p_w, p_h = 650, 420  
        x1, y1 = (w - p_w)//2, (h - p_h)//2
        x2, y2 = x1 + p_w, y1 + p_h

        crop = bg_resized.crop((x1, y1, x2, y2))
        blur = crop.filter(ImageFilter.GaussianBlur(radius=25)) 
        overlay = Image.new('RGBA', blur.size, (255, 255, 255, 40)) 
        glass = Image.alpha_composite(blur.convert('RGBA'), overlay)
        
        glass_tk = ImageTk.PhotoImage(glass)
        canvas.glass_image = glass_tk
        canvas.create_image(x1, y1, image=glass_tk, anchor="nw")
        canvas.create_rectangle(x1, y1, x2, y2, outline="#ffffff", width=1)

        canvas.create_text(w/2, y1 + 60, 
                        text="BÁO CÁO BÀI TẬP LỚN\nMÔN ĐẠI SỐ TUYẾN TÍNH", 
                        font=("Arial", 24, "bold"), fill="#0D47A1", justify="center")
        canvas.create_text(w/2, y1 + 150, 
                        text="ĐỀ TÀI 14:\nThuật toán Floyd–Warshall và ứng dụng\ntrong bài toán mạng thực tế", 
                        font=("Arial", 18, "bold"),fill="#0D3F8A", justify="center", width=550)
        info_text = (
            "Giảng viên hướng dẫn: Nguyễn Hữu Hiệp\n"
            "Nhóm thực hiện: Nhóm 08"
        )
        canvas.create_text(w/2, y1 + 260, 
                        text=info_text, 
                        font=("Arial", 16, "italic"), fill="#1A237E", justify="center")
        btn_start = tk.Button(
            root, text="BẮT ĐẦU", font=("Arial", 13, "bold"),
            bg="#1976D2", fg="white", bd=0, padx=40, pady=10,
            activebackground="#0D47A1", cursor="hand2",
            command=lambda: start_app(intro_frame)
        )
        canvas.create_window(w/2, y1 + 355, window=btn_start)
    canvas.bind("<Configure>", update_ui)

def start_app(intro_frame):
    intro_frame.destroy()
    build_main_ui()
# =========================================================
# ĐIỀU HƯỚNG NHẬP DỮ LIỆU
# =========================================================
def use_dataset():
    global df_state, floyd_tables, current_step
    df_state = copy.deepcopy(original_state)
    floyd_tables.clear() 
    current_step = 0 
    show_dataset_config()

def use_manual():
    show_manual_config()

def show_dataset_config():
    global entry, frame_dataset

    for widget in frame_dataset.winfo_children():
        widget.destroy()
    center_frame = tk.Frame(frame_dataset)
    center_frame.pack(pady=2)
    tk.Label(center_frame, text="Số đỉnh muốn xét:").pack(side="left", padx=5)
    entry = tk.Entry(center_frame, width=5)
    entry.pack(side="left", padx=5)
    tk.Button(center_frame, text="Hiển thị ma trận gốc", command=show_matrix).pack(side="left", padx=10)
    tk.Button(center_frame, text="Xuất ma trận CSV", command=export_matrix, bg="#bbdefb").pack(side="left", padx=10)
    tk.Button(center_frame, text="Thực hiện thuật toán", command=run_floyd, bg="#c8e6c9").pack(side="left", padx=10)

def show_manual_config():
    popup = tk.Toplevel(root)
    popup.title("Nhập ma trận khoảng cách")
    popup.geometry("+%d+%d" % (root.winfo_x() + 100, root.winfo_y() + 100))
    tk.Label(popup, text='Nhập "inf" hoặc để trống nếu không có cạnh', font=("Arial",9,"italic")).pack(pady=5)
    tk.Label(popup, text="Số đỉnh:").pack()
    n_entry = tk.Entry(popup)
    n_entry.pack()
    def create_matrix():
        try:
            n = int(n_entry.get())
        except ValueError:
            return messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên!")
        matrix_frame = tk.Frame(popup)
        matrix_frame.pack(pady=10)
        for j in range(n):
            tk.Label(matrix_frame, text=f"City{j+1}", font=("Arial",9,"bold")).grid(row=0, column=j+1)
        entries = []
        for i in range(n):
            tk.Label(matrix_frame, text=f"City{i+1}", font=("Arial",9,"bold")).grid(row=i+1, column=0)
            row_entries = []
            for j in range(n):
                e = tk.Entry(matrix_frame, width=6)
                e.grid(row=i+1, column=j+1, padx=2, pady=2)
                if i == j: e.insert(0, "0")
                row_entries.append(e)
            entries.append(row_entries)
        def run_manual_floyd():
            global df_state, entry 
            parse_val = lambda x: np.inf if x.lower() in ["inf", "∞", ""] else float(x)
            try:
                matrix = np.array([[parse_val(e.get().strip()) for e in row] for row in entries])
            except ValueError:
                return messagebox.showerror("Lỗi", "Có ô nhập sai định dạng số!")
            cities = [f"City{i+1}" for i in range(n)]
            df_state["cities"] = cities
            df_state["city_to_idx"] = {city: i for i, city in enumerate(cities)}
            df_state["n"] = n
            df_state["weight_df"] = pd.DataFrame(matrix, index=cities, columns=cities)
            entry = tk.Entry(root)
            entry.insert(0, str(n))
            popup.destroy()
            run_floyd()
        tk.Button(popup, text="Chạy thuật toán", command=run_manual_floyd, bg="#c8e6c9").pack(pady=10)
    tk.Button(popup, text="Tạo ma trận", command=create_matrix).pack(pady=5)
# =========================================================
# MAIN UI
# =========================================================
def build_main_ui():
    global entry, text, frame_nav, frame_path, step_entry, lbl_max_step, frame_table, src_entry, dst_entry, frame_dataset
    root.title("Bài Tập Lớn Môn Đại Số Tuyến Tính - Nhóm 08")
    root.geometry("1000x700")
    def add_btn(parent, txt, cmd, bg=None, side="left", px=5, **kwargs):
        tk.Button(parent, text=txt, command=cmd, bg=bg, **kwargs).pack(side=side, padx=px, pady=2)
    def add_lbl(parent, txt, side="left", px=5):
        lbl = tk.Label(parent, text=txt)
        lbl.pack(side=side, padx=px)
        return lbl
    def add_ent(parent, w=5, side="left", px=5):
        ent = tk.Entry(parent, width=w)
        ent.pack(side=side, padx=px)
        return ent
    tk.Label(root, text=f"Đề tài : Thuật toán Floyd – Warshall và ứng dụng trong bài toán mạng thực tế", font=("Arial", 11, "bold")).pack(pady=5)
    frame_config = tk.LabelFrame(root, text=" 1. Chọn dữ liệu đầu vào ")
    frame_config.pack(pady=5, padx=10, fill="x") 
    center_btn = tk.Frame(frame_config)
    center_btn.pack(pady=2)
    add_btn(center_btn, "Dataset có sẵn", use_dataset, bg="#e1f5fe", width=20, px=15)
    add_btn(center_btn, "Nhập thủ công", use_manual, bg="#ffe0b2", width=20, px=15)
    frame_dataset = tk.LabelFrame(root, text=" Cấu hình ")
    frame_dataset.pack(pady=2, padx=10, fill="x")
    frame_nav = tk.LabelFrame(root, text=" 2. Các bước chuyển đổi")
    center_nav = tk.Frame(frame_nav)
    center_nav.pack(pady=2)
    tk.Button(center_nav, text="<< Trang trước", command=prev_step).pack(side="left", padx=5)
    tk.Label(center_nav, text="Đến bước k =").pack(side="left", padx=5)
    step_entry = tk.Entry(center_nav, width=5)
    step_entry.pack(side="left")
    lbl_max_step = tk.Label(center_nav, text="/ 0")
    lbl_max_step.pack(side="left", padx=2)
    tk.Button(center_nav, text="Đi", command=go_to_step, width=5, bg="#fff9c4").pack(side="left", padx=5)
    tk.Button(center_nav, text="Trang sau >>", command=next_step).pack(side="left", padx=5)
    tk.Button(center_nav, text="Tự động", command=auto_play, bg="#d1c4e9").pack(side="left", padx=10)
    tk.Button(center_nav, text="Xem đồ thị", command=lambda: visualize_graph(mode="floyd"), bg="#b2dfdb").pack(side="left", padx=15)
    tk.Button(center_nav, text="Ma trận lưu vết", command=show_next_popup, bg="#c5e1a5").pack(side="left", padx=5)
    frame_path = tk.LabelFrame(root, text=" 3. Tìm đường đi ngắn nhất giữa hai đỉnh")
    center_path = tk.Frame(frame_path)
    center_path.pack(pady=2)
    tk.Label(center_path, text="Từ").pack(side="left", padx=(10, 2))
    src_entry = tk.Entry(center_path, width=8)
    src_entry.pack(side="left", padx=5)
    tk.Label(center_path, text="Đến").pack(side="left", padx=(10, 2))
    dst_entry = tk.Entry(center_path, width=8)
    dst_entry.pack(side="left", padx=5)
    tk.Button(center_path, text="Tìm đường đi", command=handle_find_path, bg="#ffe082").pack(side="left", padx=15)
    frame_table = tk.Frame(root)
    frame_table.pack(fill="both", expand=True, padx=10, pady=5)
    scroll_y = tk.Scrollbar(frame_table)
    scroll_y.pack(side="right", fill="y")  
    scroll_x = tk.Scrollbar(frame_table, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")
    text = tk.Text(frame_table, font=("Consolas", 10), wrap="none", 
                   yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    text.pack(fill="both", expand=True)
    scroll_y.config(command=text.yview)
    scroll_x.config(command=text.xview)
# =========================================================
# MAIN PROGRAM
# =========================================================
root = tk.Tk()
root.title("Bài Tập Lớn Môn Đại Số Tuyến Tính - Nhóm 08")
root.geometry("1000x700")
load_dataset('MST.csv')
show_intro()
root.mainloop()