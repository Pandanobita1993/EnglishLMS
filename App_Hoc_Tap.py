# ==============================================================================
# ỨNG DỤNG HỌC TẬP CAMBRIDGE KIDS (ALL-IN-ONE)
# Yêu cầu cài đặt: pip install streamlit streamlit-sortables pandas streamlit-option-menu streamlit-lottie requests openpyxl supabase
# ==============================================================================

import streamlit as st
from streamlit_sortables import sort_items
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from streamlit_cropper import st_cropper
from PIL import Image
import streamlit.components.v1 as components
import pandas as pd
import datetime
import base64
import os
import random
import io
import requests
import supabase
from supabase import create_client, Client

# Khởi tạo kết nối (Cache_resource giúp kết nối chạy 1 lần duy nhất)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# ================= 1. SYSTEM & UI CONFIGURATION =================
st.set_page_config(page_title="Smart English Class", page_icon="🏫", layout="centered")

@st.cache_data 
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data 
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()

lottie_hello = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_M9p23l.json")
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_a2chheio.json")

# ================= 2. SESSION STATE & ROUTING =================
if 'role' not in st.session_state: st.session_state['role'] = None  
if 'is_teacher_logged_in' not in st.session_state: st.session_state['is_teacher_logged_in'] = False
if 'current_teacher' not in st.session_state: st.session_state['current_teacher'] = None
if 'current_teacher_username' not in st.session_state: st.session_state['current_teacher_username'] = None
if 'do_scroll' not in st.session_state: st.session_state['do_scroll'] = False

# HÀM CSS RESPONSIVE & ANTI-DARK MODE
def set_responsive_background(image_path, current_role):
    try:
        bin_str = get_base64_of_bin_file(image_path)
        ext = image_path.split('.')[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        bg_css = f'background-image: url("data:{mime};base64,{bin_str}");'
    except Exception as e: 
        st.error(f"⚠️ Không tìm thấy ảnh nền. Bồ kiểm tra lại tên file nhé: {e}")
        bg_css = 'background-color: #f5f6fa;'
    
    # Độ trong suốt: 
    bg_opacity = "rgba(255, 255, 255, 0.05)" if current_role is None else "rgba(255, 255, 255, 0.45)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');
        
        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* GỌI TẤT CẢ CÁC TÊN CỦA KHUNG CHỨA */
        .block-container, 
        [data-testid="stAppViewBlockContainer"], 
        [data-testid="stMainBlockContainer"] {{
            background: {bg_opacity} !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-radius: 20px;
            padding: 2rem !important;
            margin-top: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: background 0.3s ease-in-out;
        }}

        /* Ép chữ đậm chống Dark Mode */
        .block-container p, .block-container span, .block-container label, div[data-baseweb="select"] {{
            color: #2d3436 !important; 
            font-family: 'Nunito', sans-serif !important; 
            font-weight: 700;
        }}
        
        h1, h2, h3, h4, h5 {{ 
            color: transparent !important; background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
            -webkit-background-clip: text; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            font-weight: 900 !important; font-family: 'Nunito', sans-serif !important;
        }}
        
        /* 🔥 XÓA PHÔNG ĐEN CỦA ẢNH ĐỘNG & MENU TRONG DARK MODE 🔥 */
        iframe {{
            background-color: transparent !important;
        }}
        [data-testid="stFrame"] {{
            background-color: transparent !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# Bật ảnh nền (Đã chốt cứng chuẩn 100% tên file của bồ)
set_responsive_background("Background_1.jpg", st.session_state['role'])

# Tiêu đề App
st.markdown("<h1 style='text-align: center;'>🌟 CAMBRIDGE KIDS LMS 🌟</h1>", unsafe_allow_html=True)

# ================= 3. THANH ĐIỀU HƯỚNG RESPONSIVE (OPTION MENU) =================
nav_options = ["Home", "Student", "Teacher", "Admin"]
idx_map = {None: 0, 'student': 1, 'teacher': 2, 'admin': 3}

selected_nav = option_menu(
    menu_title=None, options=nav_options,
    icons=["house-fill", "backpack-fill", "person-workspace", "shield-lock-fill"],
    menu_icon="cast", default_index=idx_map[st.session_state['role']], orientation="horizontal",
    styles={
        "container": {"padding": "5px!important", "background-color": "rgba(255,255,255,0.9)", "border-radius": "15px"},
        "icon": {"color": "#ff6b6b", "font-size": "18px"}, 
        "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "color": "#2d3436", "font-weight": "bold"},
        "nav-link-selected": {"background-color": "#0984e3", "color": "white"},
    }
)

if selected_nav == "Home" and st.session_state['role'] is not None:
    st.session_state['role'] = None
    st.rerun()
elif selected_nav != "Home" and st.session_state['role'] != selected_nav.lower():
    st.session_state['role'] = selected_nav.lower()
    st.session_state['do_scroll'] = True
    st.rerun()

# Logic tự cuộn trang
st.markdown("<div id='portal_content'></div>", unsafe_allow_html=True)
if st.session_state['do_scroll']:
    components.html("""
        <script>
            const target = window.parent.document.getElementById('portal_content');
            if (target) { target.scrollIntoView({behavior: 'smooth', block: 'start'}); }
        </script>
    """, height=0)
    st.session_state['do_scroll'] = False

# ================= 4. TRANG CHỦ (HOME) =================
if st.session_state['role'] is None:
    st.markdown("<h3 style='text-align: center; color: #0984e3 !important;'>Welcome to the Interactive Learning Platform!</h3>", unsafe_allow_html=True)
    if lottie_hello:
        st_lottie(lottie_hello, height=300, key="home_dog")
    st.info("👆 Please select your portal from the menu above to continue.")

# =========================================================================
# 5. GÓC HỌC VIÊN (STUDENT PORTAL) - PHIÊN BẢN ĐẤU NỐI DỮ LIỆU ĐỘNG
# =========================================================================
st.markdown(f"<h1 style='text-align: center; font-size: 45px;'>🚀 WELCOME TO CAMBRIDGE KIDS</h1>", unsafe_allow_html=True)

# --- KHUNG HIỂN THỊ AVATAR VÀ BONG BÓNG CHAT ---
# Khai báo tên mặc định nếu học sinh chưa đăng nhập
selected_name = st.session_state.get('student_name', 'Xu')

avatar_src = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png" 
st.markdown(f"""
    <div class="chat-container" style="display: flex; align-items: center; gap: 20px; margin-bottom: 25px;">
        <img src="{avatar_src}" style="width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 4px solid #0984e3; box-shadow: 0 4px 10px rgba(0,0,0,0.15); flex-shrink: 0;">
        <div class="chat-bubble" style="background-color: rgba(0, 184, 148, 0.15); border-left: 6px solid #00b894; padding: 18px 20px; border-radius: 12px; flex-grow: 1; color: #2d3436; font-size: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            🎉 Hello <strong style="color: #00b894; font-size: 22px;">{selected_name}</strong>! Are you ready for today's adventure?
        </div>
    </div>
""", unsafe_allow_html=True)

# --- KHU VỰC CHỌN NHIỆM VỤ ---
st.markdown("### 🎯 CHOOSE YOUR MISSION")

col_b, col_u, col_t = st.columns(3)
with col_b:
    sel_book = st.selectbox("📚 Book:", ["Kid's Box 1", "Kid's Box 2", "Kid's Box 3"])
with col_u:
    sel_unit = st.selectbox("📖 Unit:", ["Unit 1", "Unit 2", "Unit 3", "Unit 4"])
with col_t:
    sel_topic = st.selectbox("🌟 Topic:", ["Animals", "Colors", "Greetings", "Family"])

# Biến toàn cục lưu trạng thái bài học
if 'playlist' not in st.session_state:
    st.session_state['playlist'] = []
    st.session_state['current_q'] = 0
    st.session_state['all_questions'] = []

# NÚT BẤM BẮT ĐẦU VÀ LOGIC BỐC THĂM
if st.button("🚀 START MISSION", type="primary", use_container_width=True):
    with st.spinner("Đang xào bài và chuẩn bị thử thách..."):
        try:
            # Kéo dữ liệu từ Supabase (Lọc 3 lớp)
            res = supabase.table("questions").select("*") \
                    .eq("book", sel_book).eq("unit", sel_unit).eq("topic", sel_topic).execute()
            
            all_qs = res.data
            
            if not all_qs:
                st.warning("📭 Ôi! Chưa có bài tập nào trong kho cho phần này. Bé chọn chủ đề khác nhé!")
            else:
                st.session_state['all_questions'] = all_qs # Lưu lại toàn bộ câu hỏi của chủ đề này
                
                # Phân loại câu hỏi nhanh (Ex1, Ex2) và Boss (Ex4)
                # Riêng Ex3 sẽ được xử lý riêng vì nó cần gom tất cả các dòng Ex3 lại thành 1 bài Matching
                quick_qs = [q for q in all_qs if q['ex_type'] in ['Ex1', 'Ex2']]
                boss_qs = [q for q in all_qs if q['ex_type'] == 'Ex4']
                has_ex3 = any(q['ex_type'] == 'Ex3' for q in all_qs)
                
                # Rút thăm: Tối đa 8 câu Ex1, Ex2
                num_quick = min(8, len(quick_qs))
                selected_playlist = random.sample(quick_qs, num_quick)
                
                # Nếu có Ex3 trong ngân hàng, nhét 1 đại diện Ex3 vào Playlist
                if has_ex3:
                    selected_playlist.append({'ex_type': 'Ex3'}) 
                
                # Xào lên cho ngẫu nhiên
                random.shuffle(selected_playlist)
                
                # Nhét Boss (Ex4) vào CỐ ĐỊNH cuối cùng
                if boss_qs:
                    selected_playlist.append({'ex_type': 'Ex4'})
                
                st.session_state['playlist'] = selected_playlist
                st.session_state['current_q'] = 0
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ Lỗi kết nối lấy đề bài: {e}")

st.markdown("---")

# =====================================================================
# HỆ THỐNG CÁC HÀM FRAGMENT BÀI TẬP (NHẬN DỮ LIỆU ĐỘNG)
# =====================================================================
import random, string, json

@st.fragment
def run_ex1_dynamic(q_data, idx):
    st.markdown("### 🧩 EXERCISE 1: WORD PUZZLE")
    st.markdown("👉 **How to play:** Tap the letters below to spell the correct word!")
    st.info(f"💡 **Hint:** {q_data['question']}")

    correct_word = str(q_data['answer']).upper().strip().replace(" ", "")
    pool_key = f"ex1_pool_{idx}"
    ans_key = f"ex1_ans_{idx}"
    
    if pool_key not in st.session_state:
        chars = list(correct_word)
        random.shuffle(chars)
        st.session_state[pool_key] = [{'id': i, 'char': c, 'used': False} for i, c in enumerate(chars)]
        st.session_state[ans_key] = []

    pool = st.session_state[pool_key]
    answer = st.session_state[ans_key]

    # Vẽ ô đứt nét
    html_boxes = "<div style='display: flex; gap: 8px; justify-content: center; margin: 10px 0 20px 0; flex-wrap: wrap;'>"
    for i in range(len(correct_word)):
        if i < len(answer):
            char = answer[i]['char']
            html_boxes += f"<div style='width: 45px; height: 50px; border: 2px solid #0984e3; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 900; background-color: #e3f2fd; color: #2d3436; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>{char}</div>"
        else:
            html_boxes += "<div style='width: 45px; height: 50px; border: 2px dashed #b2bec3; border-radius: 8px; background-color: rgba(255,255,255,0.5);'></div>"
    html_boxes += "</div>"
    st.markdown(html_boxes, unsafe_allow_html=True)

    # Nút Delete / Reset
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1, 2, 2, 1])
    with ctrl_col2:
        if st.button("⌫ Delete", key=f"del_{idx}", use_container_width=True, disabled=len(answer) == 0):
            last_item = answer.pop()
            for p in pool:
                if p['id'] == last_item['id']: p['used'] = False
            st.rerun()
    with ctrl_col3:
        if st.button("↻ Reset", key=f"res_{idx}", use_container_width=True, disabled=len(answer) == 0):
            for p in pool: p['used'] = False
            answer.clear()
            st.rerun()

    # Bàn phím chữ cái
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(len(correct_word))
    for i, item in enumerate(pool):
        with cols[i]:
            if not item['used']:
                if st.button(item['char'], key=f"btn_{idx}_{item['id']}", use_container_width=True, type="primary"):
                    if len(answer) < len(correct_word):
                        item['used'] = True
                        answer.append(item)
                        st.rerun()
            else:
                st.button(item['char'], key=f"btndis_{idx}_{item['id']}", disabled=True, use_container_width=True)

    # Chấm điểm
    st.markdown("---")
    if len(answer) == len(correct_word):
        if "".join([item['char'] for item in answer]) == correct_word:
            st.success(f"🎉 Awesome! You spelled **{correct_word}** correctly!")
            st.balloons()
        else:
            st.error("❌ Not quite! Tap 'Delete' or 'Reset' to try again!")

@st.fragment
def run_ex2_dynamic(q_data, idx):
    st.markdown("### 📝 EXERCISE 2: FILL IN THE BLANK")
    st.info("Tap the correct word below to fill in the blank!")
    
    base_q = str(q_data['question'])
    correct_ans = str(q_data['answer']).strip()
    # Xử lý các lựa chọn
    raw_opts = str(q_data['options']).split(',')
    opts = [o.strip() for o in raw_opts if o.strip()]
    if correct_ans not in opts: opts.append(correct_ans) # Đề phòng cô giáo quên nhập đáp án vào ô options
    
    sel_key = f"ex2_sel_{idx}"
    if sel_key not in st.session_state:
        random.shuffle(opts)
        st.session_state[f"ex2_opts_{idx}"] = opts
        st.session_state[sel_key] = None
        st.session_state[f"ex2_done_{idx}"] = False

    current_word = st.session_state[sel_key] if st.session_state[sel_key] else "..."
    blank_color = "#0984e3" if st.session_state[sel_key] else "#b2bec3"
    
    display_q = base_q.replace('___________', f'<span style="color:{blank_color}; border:2px dashed {blank_color}; background:#fff; padding:2px 12px; border-radius:8px;">{current_word}</span>')
    st.markdown(f"<div style='font-size:18px; background:rgba(255,255,255,0.7); padding:18px; border-radius:12px; text-align:center; margin-bottom:20px;'>{display_q}</div>", unsafe_allow_html=True)

    if not st.session_state[f"ex2_done_{idx}"]:
        cols = st.columns(len(st.session_state[f"ex2_opts_{idx}"]))
        for i, opt in enumerate(st.session_state[f"ex2_opts_{idx}"]):
            with cols[i]:
                is_chosen = (st.session_state[sel_key] == opt)
                if st.button(f"✨ [{opt}]" if is_chosen else f"📦 {opt}", key=f"e2b_{idx}_{i}", use_container_width=True):
                    st.session_state[sel_key] = opt
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 SUBMIT ANSWER", key=f"e2s_{idx}", use_container_width=True, type="primary"):
            if not st.session_state[sel_key]:
                st.warning("⚠️ Please select a word first!")
            else:
                if st.session_state[sel_key] == correct_ans:
                    st.session_state[f"ex2_done_{idx}"] = True
                    st.rerun()
                else:
                    st.error(f"❌ Oops, '{st.session_state[sel_key]}' is incorrect.")
    else:
        st.success(f"✅ Perfect! The correct answer is: **{correct_ans}**")
        st.balloons()

@st.fragment
def run_ex3_dynamic(all_qs, idx):
    st.markdown("### 🔗 EXERCISE 3: MATCHING")
    st.info("Tap an item in COLUMN A, then tap its match in COLUMN B.")

    # Tự động gom TẤT CẢ câu Ex3 trong chủ đề này lại
    ex3_qs = [q for q in all_qs if q['ex_type'] == 'Ex3']
    if not ex3_qs:
        st.error("Không đủ dữ liệu tạo bài nối.")
        return
        
    matching_pairs = {q['question']: q['answer'] for q in ex3_qs}
    
    if f'ex3_lefts_{idx}' not in st.session_state:
        lefts = list(matching_pairs.keys())
        rights = list(matching_pairs.values())
        random.shuffle(lefts)
        random.shuffle(rights)
        st.session_state[f'ex3_lefts_{idx}'] = lefts
        st.session_state[f'ex3_rights_{idx}'] = rights
        st.session_state[f'ex3_sl_{idx}'] = None
        st.session_state[f'ex3_sr_{idx}'] = None
        st.session_state[f'ex3_done_{idx}'] = []

    # Logic check nối
    if st.session_state[f'ex3_sl_{idx}'] and st.session_state[f'ex3_sr_{idx}']:
        l_val = st.session_state[f'ex3_sl_{idx}']
        r_val = st.session_state[f'ex3_sr_{idx}']
        if matching_pairs[l_val] == r_val:
            st.session_state[f'ex3_done_{idx}'].append(l_val)
            st.toast("🎉 Correct Match!", icon="✅")
        else:
            st.toast("❌ Incorrect Match!", icon="🚨")
        st.session_state[f'ex3_sl_{idx}'] = None
        st.session_state[f'ex3_sr_{idx}'] = None
        st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<h5 style='text-align: center; color: #d63031;'>🔹 COLUMN A</h5>", unsafe_allow_html=True)
        for item in st.session_state[f'ex3_lefts_{idx}']:
            is_done = item in st.session_state[f'ex3_done_{idx}']
            is_sel = item == st.session_state[f'ex3_sl_{idx}']
            if is_done:
                st.button(f"✅ {item}", key=f"LA_{idx}_{item}", disabled=True, use_container_width=True)
            elif is_sel:
                if st.button(f"🟡 {item}", key=f"LA_{idx}_{item}", type="primary", use_container_width=True):
                    st.session_state[f'ex3_sl_{idx}'] = None; st.rerun()
            else:
                if st.button(f"🟦 {item}", key=f"LA_{idx}_{item}", use_container_width=True):
                    st.session_state[f'ex3_sl_{idx}'] = item; st.rerun()
    with col_b:
        st.markdown("<h5 style='text-align: center; color: #0984e3;'>🔸 COLUMN B</h5>", unsafe_allow_html=True)
        for item in st.session_state[f'ex3_rights_{idx}']:
            parent_key = [k for k, v in matching_pairs.items() if v == item][0]
            is_done = parent_key in st.session_state[f'ex3_done_{idx}']
            is_sel = item == st.session_state[f'ex3_sr_{idx}']
            if is_done:
                st.button(f"✅ {item}", key=f"LB_{idx}_{item}", disabled=True, use_container_width=True)
            elif is_sel:
                if st.button(f"🟡 {item}", key=f"LB_{idx}_{item}", type="primary", use_container_width=True):
                    st.session_state[f'ex3_sr_{idx}'] = None; st.rerun()
            else:
                if st.button(f"🟧 {item}", key=f"LB_{idx}_{item}", use_container_width=True):
                    st.session_state[f'ex3_sr_{idx}'] = item; st.rerun()

    if len(st.session_state[f'ex3_done_{idx}']) == len(matching_pairs):
        st.success("🎉 Awesome! You matched everything perfectly!")
        st.balloons()

@st.fragment
def run_ex4_dynamic(all_qs, idx):
    st.markdown("### 🕵️‍♀️ EXERCISE 4: THE BIG BOSS WORD SEARCH")
    st.info("Swipe through the letters in the grid to find the hidden words. Drag and drop them into the correct pictures!")

    ex4_qs = [q for q in all_qs if q['ex_type'] == 'Ex4']
    # Giới hạn 8 câu cho lưới 12x12
    if len(ex4_qs) > 8: ex4_qs = random.sample(ex4_qs, 8)
    
    target_words = [q['answer'].upper().replace(" ", "") for q in ex4_qs]
    pic_mapping = {q['question']: q['answer'].upper().replace(" ", "") for q in ex4_qs}

    # THUẬT TOÁN TẠO LƯỚI MA TRẬN TỰ ĐỘNG BẰNG PYTHON (Đỉnh cao đây nè bồ)
    def generate_grid(words, size=12):
        grid = [['' for _ in range(size)] for _ in range(size)]
        for word in words:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction = random.choice([(0,1), (1,0)]) # Ngang hoặc Dọc
                r = random.randint(0, size-1) if direction == (0,1) else random.randint(0, size-len(word))
                c = random.randint(0, size-len(word)) if direction == (0,1) else random.randint(0, size-1)
                fit = True
                for i, char in enumerate(word):
                    if grid[r + direction[0]*i][c + direction[1]*i] not in ('', char): fit = False; break
                if fit:
                    for i, char in enumerate(word): grid[r + direction[0]*i][c + direction[1]*i] = char
                    placed = True
                attempts += 1
        for r in range(size):
            for c in range(size):
                if grid[r][c] == '': grid[r][c] = random.choice(string.ascii_uppercase)
        return grid

    grid_data = generate_grid(target_words)
    
    # Đóng gói dữ liệu Python vứt sang Javascript
    js_grid = json.dumps(grid_data)
    js_targets = json.dumps(target_words)
    js_mapping = json.dumps(pic_mapping)

    # HTML & Javascript (Dùng dữ liệu được bơm từ Python)
    html_game_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8">
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; user-select: none; background: transparent; padding-bottom: 30px;}}
        .grid {{ display: grid; grid-template-columns: repeat(12, 28px); gap: 4px; justify-content: center; margin: 15px auto; touch-action: none;}}
        .cell {{ width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; background: #fff; border: 2px solid #dfe6e9; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: crosshair; transition: transform 0.1s; }}
        .cell.selecting {{ background: #ffeaa7; transform: scale(1.1); box-shadow: 0 0 10px #fdcb6e; border-color: #fdcb6e;}}
        .cell.found {{ background: #55efc4; color: white; border-color: #00b894; opacity: 0.8;}}
        .bank {{ min-height: 50px; padding: 10px; border: 2px dashed #b2bec3; border-radius: 15px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin: 15px 0; background: rgba(255,255,255,0.7);}}
        .pill {{ padding: 6px 15px; background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white; border-radius: 20px; font-weight: bold; font-size: 14px; cursor: grab; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .pictures {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin: auto; }}
        .pic-box {{ width: 75px; background: white; border-radius: 12px; padding: 8px; display: flex; flex-direction: column; align-items: center; border: 3px solid transparent;}}
        .pic {{ font-size: 35px; margin-bottom: 5px; }}
        .drop-zone {{ width: 100%; height: 30px; background: #f1f2f6; border: 2px dashed #ced6e0; border-radius: 6px; display: flex; align-items: center; justify-content: center;}}
        .drop-zone.drag-over {{ background: #dfe6e9; border-color: #0984e3; transform: scale(1.05);}}
        .btn-check {{ margin-top: 25px; padding: 12px 30px; background: linear-gradient(90deg, #ff6b6b, #feca57); color: white; border: none; border-radius: 25px; font-size: 18px; font-weight: bold; cursor: pointer; }}
        #message {{ margin-top: 15px; font-weight: bold; font-size: 18px; }}
    </style>
    </head>
    <body>
    <div class="grid" id="grid"></div>
    <h4 style="color:#6c5ce7; margin-bottom: 5px;">Drag words to pictures:</h4>
    <div class="bank" id="bank"></div>
    <div class="pictures" id="pictures"></div>
    <button class="btn-check" onclick="checkAnswers()">🚀 CHECK MY ANSWERS</button>
    <div id="message"></div>

    <script>
        const gridData = {js_grid};
        const targetWords = {js_targets};
        const picMapping = {js_mapping};
        let foundWords = [];

        const gridEl = document.getElementById('grid');
        gridData.forEach(row => {{
            row.forEach(letter => {{
                let cell = document.createElement('div');
                cell.className = 'cell'; cell.innerText = letter;
                gridEl.appendChild(cell);
            }});
        }});

        let isSelecting = false; let currentSelection = []; let selectedCells = [];
        function startSelect(target) {{
            if(target.classList.contains('cell') && !target.classList.contains('found')) {{
                isSelecting = true; target.classList.add('selecting');
                currentSelection.push(target.innerText); selectedCells.push(target);
            }}
        }}
        function moveSelect(target) {{
            if(isSelecting && target.classList.contains('cell') && !target.classList.contains('found') && !selectedCells.includes(target)) {{
                target.classList.add('selecting'); currentSelection.push(target.innerText); selectedCells.push(target);
            }}
        }}
        function endSelect() {{
            if(isSelecting) {{
                isSelecting = false;
                let wordStr = currentSelection.join('');
                let wordStrRev = currentSelection.slice().reverse().join(''); 
                let matchedWord = null;
                if(targetWords.includes(wordStr) && !foundWords.includes(wordStr)) matchedWord = wordStr;
                else if (targetWords.includes(wordStrRev) && !foundWords.includes(wordStrRev)) matchedWord = wordStrRev;

                if (matchedWord) {{
                    selectedCells.forEach(c => {{ c.classList.remove('selecting'); c.classList.add('found'); }});
                    foundWords.push(matchedWord); createPill(matchedWord); 
                }} else {{
                    selectedCells.forEach(c => c.classList.remove('selecting'));
                }}
                currentSelection = []; selectedCells = [];
            }}
        }}
        gridEl.addEventListener('mousedown', (e) => startSelect(e.target));
        gridEl.addEventListener('mouseover', (e) => moveSelect(e.target));
        window.addEventListener('mouseup', endSelect);
        gridEl.addEventListener('touchstart', (e) => {{ let t = document.elementFromPoint(e.touches[0].clientX, e.touches[0].clientY); if(t) startSelect(t); e.preventDefault(); }}, {{passive: false}});
        gridEl.addEventListener('touchmove', (e) => {{ let t = document.elementFromPoint(e.touches[0].clientX, e.touches[0].clientY); if(t) moveSelect(t); e.preventDefault(); }}, {{passive: false}});
        window.addEventListener('touchend', endSelect);

        const picsEl = document.getElementById('pictures');
        Object.keys(picMapping).forEach(emoji => {{
            let box = document.createElement('div'); box.className = 'pic-box';
            let pic = document.createElement('div'); pic.className = 'pic'; pic.innerText = emoji;
            let dropZone = document.createElement('div'); dropZone.className = 'drop-zone'; dropZone.dataset.target = picMapping[emoji];
            dropZone.addEventListener('dragover', (e) => {{ e.preventDefault(); dropZone.classList.add('drag-over'); }});
            dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
            dropZone.addEventListener('drop', (e) => {{
                e.preventDefault(); dropZone.classList.remove('drag-over');
                let pill = document.getElementById(e.dataTransfer.getData('text'));
                if (pill) {{ dropZone.innerHTML = ''; dropZone.appendChild(pill); dropZone.style.border = 'none'; dropZone.style.background = 'transparent';}}
            }});
            box.appendChild(pic); box.appendChild(dropZone); picsEl.appendChild(box);
        }});

        const bankEl = document.getElementById('bank');
        bankEl.addEventListener('dragover', (e) => e.preventDefault());
        bankEl.addEventListener('drop', (e) => {{ e.preventDefault(); let pill = document.getElementById(e.dataTransfer.getData('text')); if(pill) bankEl.appendChild(pill); }});

        function createPill(word) {{
            let pill = document.createElement('div'); pill.className = 'pill'; pill.innerText = word; pill.id = 'pill_' + word; pill.draggable = true;
            pill.addEventListener('dragstart', (e) => e.dataTransfer.setData('text', e.target.id));
            bankEl.appendChild(pill);
        }}

        function checkAnswers() {{
            let allCorrect = true; let filledCount = 0;
            document.querySelectorAll('.drop-zone').forEach(zone => {{
                let pill = zone.querySelector('.pill');
                if(pill) {{
                    filledCount++;
                    if(pill.innerText !== zone.dataset.target) {{ allCorrect = false; zone.parentElement.style.borderColor = "#ff7675"; }} 
                    else {{ zone.parentElement.style.borderColor = "#55efc4"; }}
                }} else {{ allCorrect = false; }}
            }});
            let msg = document.getElementById('message');
            if(filledCount < Object.keys(picMapping).length) msg.innerHTML = "<span style='color:#fdcb6e;'>⚠️ Nu says: You haven't found all words yet!</span>";
            else if (!allCorrect) msg.innerHTML = "<span style='color:#ff7675;'>❌ Oops, some matches are incorrect. Try again!</span>";
            else msg.innerHTML = "<span style='color:#00b894;'>🎉 EXCELLENT! You found and matched everything perfectly! 🏆</span>";
        }}
    </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_game_code, height=1050)


# --- KHU VỰC ĐIỀU HƯỚNG VÀ RENDER BÀI TẬP ---
if len(st.session_state['playlist']) > 0:
    total_q = len(st.session_state['playlist'])
    curr_idx = st.session_state['current_q']
    current_q_data = st.session_state['playlist'][curr_idx]
    
    st.progress((curr_idx + 1) / total_q)
    st.caption(f"🚩 Tiến độ: Thử thách số {curr_idx + 1} / {total_q}")
    
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav2:
        # Nút chuyển câu - chỉ xuất hiện sau khi nhấn Start
        btn_label = "FINISH MISSION 🌟" if curr_idx == total_q - 1 else "NEXT MISSION ➔"
        if st.button(btn_label, use_container_width=True, type="secondary"):
            if curr_idx < total_q - 1:
                st.session_state['current_q'] += 1
                st.rerun()
            else:
                st.balloons()
                st.success("🎉 XUẤT SẮC! BÉ ĐÃ ĐÁNH BẠI TOÀN BỘ THỬ THÁCH HÔM NAY!")
                st.session_state['playlist'] = [] # Xóa playlist để kết thúc
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🔥 ĐẤU NỐI LOGIC: CÂU HỎI LOẠI NÀO THÌ GỌI FRAGMENT LOẠI ĐÓ 🔥
    ex_type = current_q_data.get('ex_type', '')
    
    if ex_type == 'Ex1':
        run_ex1_dynamic(current_q_data, curr_idx)
    elif ex_type == 'Ex2':
        run_ex2_dynamic(current_q_data, curr_idx)
    elif ex_type == 'Ex3':
        # Ex3 xài dữ liệu tổng hợp của toàn bộ Unit/Topic hiện tại
        run_ex3_dynamic(st.session_state['all_questions'], curr_idx)
    elif ex_type == 'Ex4':
        # Ex4 đánh boss xài dữ liệu tổng hợp để tạo lưới 12x12 tự động
        run_ex4_dynamic(st.session_state['all_questions'], curr_idx)
    else:
        st.error("⚠️ Hệ thống không nhận diện được loại bài tập này.")
                
# ================= 6. GÓC GIÁO VIÊN (TEACHER PORTAL) =================
elif st.session_state['role'] == 'teacher':
    if not st.session_state['is_teacher_logged_in']:
        st.markdown("### 👨‍🏫 Teacher Login")
        u_tch = st.text_input("Username:")
        p_tch = st.text_input("Password:", type="password")
        if st.button("🔓 Login", type="primary"):
            res = supabase.table("teachers").select("*").eq("username", u_tch).eq("password", p_tch).execute()
            if res.data:
                st.session_state['is_teacher_logged_in'] = True
                st.session_state['current_teacher'] = res.data[0]['full_name']
                st.session_state['current_teacher_username'] = res.data[0]['username'] # Lưu lại ID để lọc danh sách
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please contact Admin.")
    else:
        c_title, c_btn = st.columns([4, 1])
        with c_title:
            st.success(f"✨ Welcome back, Teacher **{st.session_state['current_teacher']}**!")
        with c_btn:
            if st.button("🔒 Logout"):
                st.session_state['is_teacher_logged_in'] = False
                st.rerun()
            
        st.markdown("---")
        
        # TEACHER DASHBOARD
        tab_assign, tab_bank, tab_student = st.tabs(["🛠️ Assign Homework", "🏦 Question Bank", "👧🏻 Manage Students"])
        
        # --------- TAB 1: ASSIGN HOMEWORK ---------
        with tab_assign:
            st.markdown("#### Create New Session")
            col1, col2 = st.columns(2)
            with col1:
                sach = st.selectbox("📚 Select Book:", ["Kid's Box 1", "Kid's Box 2", "Kid's Box 3"])
                ky_nang = st.selectbox("🎯 Target Skill:", ["Listening", "Reading & Writing", "Speaking"])
            with col2:
                units = st.multiselect("🏷️ Select Units:", ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"])
                thoi_gian = st.number_input("⏳ Duration (Hours):", min_value=1, value=48)
            
            if st.button("🚀 PUBLISH ASSIGNMENT", type="primary", use_container_width=True):
                if not units:
                    st.error("⚠️ Please select at least one Unit!")
                else:
                    st.session_state['active_session'] = {
                        'book': sach, 'units': units, 'skill': ky_nang, 
                        'deadline': datetime.datetime.now() + datetime.timedelta(hours=thoi_gian)
                    }
                    st.success(f"Successfully published assignment for {sach} ({', '.join(units)})!")

        # --------- TAB 2: QUESTION BANK ---------
        with tab_bank:
            st.markdown("#### 🏦 Import Questions from Excel")
            st.info("💡 **Hướng dẫn:** File Excel tải lên cần có dòng tiêu đề: **Book, Unit, Topic, Type, Question, Answer, Options**")
            
            # 1. KHU VỰC TẢI FILE
            uploaded_file = st.file_uploader("📥 Tải file Excel (.xlsx) lên đây", type=["xlsx"])
            
            if uploaded_file:
                try:
                    import pandas as pd
                    # Đọc file Excel
                    df = pd.read_excel(uploaded_file)
                    df = df.dropna(how='all') # Bỏ các dòng trống
                    
                    st.write("👀 **Bản xem trước dữ liệu:**")
                    st.dataframe(df.head(5), use_container_width=True) # Chỉ hiện 5 dòng đầu cho lẹ
                    
                    if st.button("🚀 UPLOAD TO DATABASE", type="primary", use_container_width=True):
                        with st.spinner("Đang đẩy dữ liệu lên kho Supabase..."):
                            success_count = 0
                            # Vòng lặp chuyển từng dòng Excel lên Cloud
                            for index, row in df.iterrows():
                                try:
                                    data_insert = {
                                        "book": str(row.get('Book', '')).strip(),
                                        "unit": str(row.get('Unit', '')).strip(),
                                        "topic": str(row.get('Topic', '')).strip(),
                                        "ex_type": str(row.get('Type', '')).strip(),
                                        "question": str(row.get('Question', '')).strip(),
                                        "answer": str(row.get('Answer', '')).strip(),
                                        "options": str(row.get('Options', '')).strip() if pd.notna(row.get('Options')) else ""
                                    }
                                    # Lệnh bóp cò bắn dữ liệu
                                    supabase.table("questions").insert(data_insert).execute()
                                    success_count += 1
                                except Exception as err:
                                    st.error(f"⚠️ Lỗi ở dòng {index + 2}: {err}")
                            
                            st.success(f"🎉 Xuất sắc! Đã nạp thành công {success_count} câu hỏi vào kho!")
                            st.balloons()
                except Exception as e:
                    st.error(f"❌ File Excel không hợp lệ. Lỗi: {e}")
                    
            st.markdown("---")
            
            # 2. KHU VỰC QUẢN LÝ KHO DỮ LIỆU CHÍNH THỨC
            st.markdown("#### 📋 Question Library (Kho câu hỏi hiện tại trên Cloud)")
            
            # Bộ lọc để giáo viên tìm kiếm (Bây giờ có thêm lọc theo Topic)
            col_loc1, col_loc2 = st.columns(2)
            with col_loc1:
                filter_book = st.selectbox("📚 Lọc theo Sách:", ["All", "Kid's Box 1", "Kid's Box 2", "Kid's Box 3"])
            with col_loc2:
                # Nút Refresh siêu tốc
                if st.button("🔄 Làm mới danh sách", use_container_width=True):
                    st.rerun()
            
            try:
                # Đọc dữ liệu từ Supabase về
                if filter_book == "All":
                    res_q = supabase.table("questions").select("*").execute()
                else:
                    res_q = supabase.table("questions").select("*").eq("book", filter_book).execute()
                    
                db_questions = res_q.data
                
                if db_questions:
                    # Đưa vào Pandas để hiển thị bảng thật đẹp
                    df_view = pd.DataFrame(db_questions)
                    # Sắp xếp lại cột cho dễ nhìn
                    df_view = df_view[['id', 'book', 'unit', 'topic', 'ex_type', 'question', 'answer', 'options']]
                    
                    st.dataframe(df_view, use_container_width=True, hide_index=True)
                    st.caption(f"📊 Tổng cộng: **{len(db_questions)}** câu hỏi trong kho.")
                else:
                    st.warning("📭 Kho dữ liệu đang trống. Hãy tải file Excel lên nhé!")
            except Exception as e:
                st.error("⚠️ Lỗi kết nối Supabase! Bồ kiểm tra lại xem đã tạo bảng 'questions' chưa nhé.")

       # --------- TAB 3: MANAGE STUDENTS ---------
        with tab_student:
            st.markdown("**Add Student to Class**")
            res_classes = supabase.table("classes").select("*").eq("teacher_username", st.session_state['current_teacher_username']).execute()
            db_classes = res_classes.data
            
            if not db_classes:
                st.warning("⚠️ No classes found. Please ask Admin to create a class first!")
            else:
                class_options = [f"{c['class_code']} - {c['class_name']}" for c in db_classes]
                selected_class_full = st.selectbox("Assign to Class:", class_options)
                selected_code = selected_class_full.split(" - ")[0]
                
                s_name = st.text_input("Student Name (e.g., Harry Potter):").strip()
                s_avatar = st.file_uploader("Upload Student Avatar (Optional)", type=["png", "jpg", "jpeg"])
                
                avatar_b64 = None
                
                # --- GIAO DIỆN CẮT ẢNH TƯƠNG TÁC ---
                if s_avatar:
                    st.info("✂️ Drag and resize the blue box to frame the face. (The square will automatically become a circle later!)")
                    # Mở ảnh bằng thư viện PIL
                    img = Image.open(s_avatar)
                    
                    # Gọi công cụ cắt ảnh (Ép tỉ lệ 1:1 hình vuông để CSS tự bo thành hình tròn chuẩn)
                    cropped_img = st_cropper(img, aspect_ratio=(1, 1), box_color='#0984e3', return_type='image')
                    
                    # Biến ảnh đã cắt thành Base64 để lưu vào Database
                    buffered = io.BytesIO()
                    cropped_img.save(buffered, format="PNG")
                    avatar_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                # Nút Submit (Đã đưa ra ngoài form)
                if st.button("➕ ADD STUDENT", type="primary"):
                    if s_name:
                        try:
                            supabase.table("students").insert({
                                "class_code": selected_code, "student_name": s_name, "avatar": avatar_b64
                            }).execute()
                            st.success(f"✅ Added {s_name} to class {selected_code} successfully!")
                            st.rerun() # Tự động load lại trang để cập nhật danh sách ngay lập tức
                        except Exception as e:
                            st.error(f"❌ Error adding student: {e}")
                    else:
                        st.error("⚠️ Please enter the student's name.")
                            
            # Xem danh sách học sinh
            st.markdown("---")
            if db_classes:
                view_class = st.selectbox("View Students in Class:", options=[c['class_code'] for c in db_classes], format_func=lambda x: next(c['class_name'] for c in db_classes if c['class_code'] == x))
                if view_class:
                    res_students = supabase.table("students").select("*").eq("class_code", view_class).execute()
                    if res_students.data:
                        st.write(f"**Total: {len(res_students.data)} students**")
                        cols = st.columns(4)
                        for i, student in enumerate(res_students.data):
                            with cols[i % 4]:
                                avt_src = f"data:image/jpeg;base64,{student['avatar']}" if student['avatar'] else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                                st.markdown(f"""
                                    <div style="text-align: center; background: rgba(255,255,255,0.8); padding: 15px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 2px solid transparent;">
                                        <img src="{avt_src}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #6c5ce7; padding: 2px;">
                                        <p style="font-weight: bold; margin-top: 10px; margin-bottom: 0; color: #2d3436; font-size: 16px;">{student['student_name']}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No students in this class yet.")

# ================= 7. GÓC QUẢN TRỊ VIÊN (ADMIN PORTAL) =================
elif st.session_state['role'] == 'admin':
    if 'is_admin_logged_in' not in st.session_state:
        st.session_state['is_admin_logged_in'] = False
        
    if not st.session_state['is_admin_logged_in']:
        st.markdown("### 🛡️ System Administrator")
        u_admin = st.text_input("Admin ID:")
        p_admin = st.text_input("Password:", type="password")
        if st.button("🔓 Login", type="primary"):
            if u_admin == "admin" and p_admin == "123456": 
                st.session_state['is_admin_logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Access Denied!")
    else:
        c_title, c_btn = st.columns([4, 1])
        with c_title:
            st.success("✨ Welcome to Central Management!")
        with c_btn:
            if st.button("🔒 Logout"):
                st.session_state['is_admin_logged_in'] = False
                st.rerun()
            
        tab_tch, tab_cls = st.tabs(["👨‍🏫 Manage Teachers", "🏫 Manage Classes"])
        
        # QUẢN LÝ GIÁO VIÊN
        with tab_tch:
            st.markdown("**Create Teacher Accounts**")
            with st.form("add_teacher", clear_on_submit=True):
                t_name = st.text_input("Teacher's Full Name:")
                t_user = st.text_input("Username (Login ID):").strip()
                t_pass = st.text_input("Password:", type="password")
                if st.form_submit_button("➕ CREATE ACCOUNT", type="primary"):
                    if t_user and t_pass:
                        try:
                            supabase.table("teachers").insert({"username": t_user, "password": t_pass, "full_name": t_name}).execute()
                            st.success(f"✅ Account '{t_user}' created for {t_name}!")
                        except Exception as e:
                            st.error(f"❌ Error (Username may already exist): {e}")
                    else:
                        st.warning("Please fill all fields.")
                            
        # QUẢN LÝ MÃ LỚP TRUNG TÂM
        with tab_cls:
            st.markdown("**Create Official Classes & Assign Teachers**")
            
            # Kéo danh sách giáo viên về trước
            res_tch = supabase.table("teachers").select("*").execute()
            db_teachers = res_tch.data
            
            if not db_teachers:
                st.warning("⚠️ Please create at least one Teacher account first!")
            else:
                with st.form("add_class_admin", clear_on_submit=True):
                    c_code = st.text_input("Class Code (e.g., ENG101):").strip().upper()
                    c_name = st.text_input("Class Name (e.g., Movers 1):").strip()
                    
                    # Danh sách chọn giáo viên
                    teacher_options = [f"{t['username']} - {t['full_name']}" for t in db_teachers]
                    selected_teacher_full = st.selectbox("Assign Teacher:", teacher_options)
                    selected_t_username = selected_teacher_full.split(" - ")[0]
                    
                    if st.form_submit_button("➕ ADD CLASS", type="primary"):
                        if c_code and c_name:
                            try:
                                supabase.table("classes").insert({
                                    "class_code": c_code, 
                                    "class_name": c_name,
                                    "teacher_username": selected_t_username
                                }).execute()
                                st.success(f"✅ Class {c_name} assigned to teacher '{selected_t_username}' successfully!")
                            except Exception as e:
                                st.error(f"❌ Error adding class: {e}")
                        else:
                            st.error("⚠️ Please enter both Code and Name.")
