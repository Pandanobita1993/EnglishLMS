# ==============================================================================
# CAMBRIDGE KIDS LEARNING APP (ALL-IN-ONE)
# Requirements: pip install streamlit streamlit-sortables pandas streamlit-option-menu streamlit-lottie requests openpyxl supabase
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

# -----------------------------------------------------------------------------
# 🔥 HỆ THỐNG TỐI ƯU TỐC ĐỘ (CACHE) - TRÁNH LAG KHI RERUN 🔥
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def get_class_info(class_code):
    return supabase.table("classes").select("*").eq("class_code", class_code).execute().data

@st.cache_data(ttl=300)
def get_students_in_class(class_code):
    return supabase.table("students").select("*").eq("class_code", class_code).execute().data

@st.cache_data(ttl=300)
def get_curriculum_structure():
    try:
        # Kéo thêm cột level để phục vụ lộ trình luyện thi
        res = supabase.table("curriculum").select("book, unit, topic, level").execute()
        if res.data:
            return pd.DataFrame(res.data).drop_duplicates()
        return pd.DataFrame()
    except Exception as e:
        print(f"Lỗi đọc khung chương trình: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_questions(mode, skill, book=None, unit=None, level=None, topic=None):
    # Bộ lọc thông minh tự động uốn nắn theo lựa chọn của học viên
    query = supabase.table("questions").select("*")
    
    # Lọc Kỹ năng (Nếu khác "All")
    if skill != "All":
        query = query.eq("skill", skill)
        
    # Lọc theo Lộ trình
    if mode == "book":
        query = query.eq("book", book).eq("unit", unit)
    elif mode == "topic":
        query = query.eq("level", level).eq("topic", topic)
        
    return query.execute().data
    
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
        st.error(f"⚠️ Background image not found: {e}")
        bg_css = 'background-color: #f5f6fa;'
    
    bg_opacity = "rgba(255, 255, 255, 0.05)" if current_role is None else "rgba(255, 255, 255, 0.45)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

        /* Nút Primary (Bắt đầu, Nộp bài) - Màu gradient rực rỡ */
        div[data-testid="stButton"] button[kind="primary"] {{
            background: linear-gradient(90deg, #ff6b6b, #feca57) !important;
            color: white !important;
            border: none !important;
            font-weight: 900 !important;
            border-radius: 25px !important;
            box-shadow: 0 5px 15px rgba(255,107,107,0.4) !important;
            transition: all 0.2s ease-in-out;
        }}
        div[data-testid="stButton"] button[kind="primary"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255,107,107,0.6) !important;
        }}
        
        /* Nút Secondary (Next Mission) - Nền tối chữ vàng siêu ngầu & dễ đọc */
        div[data-testid="stButton"] button[kind="secondary"] {{
            background: #2d3436 !important;
            color: #ffeaa7 !important;
            border: 2px solid #ffeaa7 !important;
            font-weight: 900 !important;
            border-radius: 25px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }}
        div[data-testid="stButton"] button[kind="secondary"]:hover {{
            background: #1e272e !important;
            color: #f1c40f !important;
            border-color: #f1c40f !important;
        }}
        
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
        
        iframe, [data-testid="stFrame"] {{
            background-color: transparent !important;
        }}
        </style>
    """, unsafe_allow_html=True)

set_responsive_background("Background_1.jpg", st.session_state['role'])

st.markdown("<h1 style='text-align: center;'>🌟 CAMBRIDGE KIDS LMS 🌟</h1>", unsafe_allow_html=True)

# ================= 3. NAVIGATION (OPTION MENU) =================
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

st.markdown("<div id='portal_content'></div>", unsafe_allow_html=True)
if st.session_state['do_scroll']:
    components.html("""
        <script>
            const target = window.parent.document.getElementById('portal_content');
            if (target) { target.scrollIntoView({behavior: 'smooth', block: 'start'}); }
        </script>
    """, height=0)
    st.session_state['do_scroll'] = False

# ================= 4. HOME PORTAL =================
if st.session_state['role'] is None:
    st.markdown("<h3 style='text-align: center; color: #0984e3 !important;'>Welcome to the Interactive Learning Platform!</h3>", unsafe_allow_html=True)
    if lottie_hello:
        st_lottie(lottie_hello, height=300, key="home_dog")
    st.info("👆 Please select your portal from the menu above to continue.")

# =========================================================================
# 5. STUDENT PORTAL
# =========================================================================
elif st.session_state['role'] == 'student':
    import random, string, json
    
    # Kéo các hàm bài tập siêu mượt từ file hệ thống sang
    from Exercise_Components import run_ex1_dynamic, run_ex2_dynamic, run_ex3_dynamic, run_ex4_dynamic, run_ex5_dynamic, run_ex6_dynamic

    # ---------------------------------------------------------------------
    # GIAO DIỆN ĐĂNG NHẬP & LUỒNG HỌC TẬP CHÍNH
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='text-align: center; color: #0984e3;'>🎒 Student Login</h3>", unsafe_allow_html=True)
    
    class_code_input = st.text_input("🔑 Enter your Class Code:").strip().upper()
    
    if class_code_input:
        class_data = get_class_info(class_code_input)
        
        if not class_data:
            st.error("❌ Class Code not found!")
        else:
            class_name = class_data[0]['class_name']
            st.success(f"🏫 Found class: **{class_name}**")
            
            students_in_class = get_students_in_class(class_code_input)
            
            if len(students_in_class) == 0:
                st.warning("⚠️ No students added to this class yet!")
            else:
                student_options = ["👇 Click here..."] + [s['student_name'] for s in students_in_class]
                selected_name = st.selectbox("Who are you?", options=student_options)
                
                # BƯỚC 3: KIỂM TRA ĐĂNG NHẬP THÀNH CÔNG -> HIỂN THỊ AVATAR NỔI VÀ BÀI TẬP
                if selected_name != "👇 Click here...":
                    
                    # 1. Khởi tạo các biến lưu trạng thái nếu chưa có
                    if 'playlist' not in st.session_state:
                        st.session_state['playlist'] = []
                        st.session_state['current_q'] = 0
                        st.session_state['all_questions'] = []
                    if 'mission_completed' not in st.session_state:
                        st.session_state['mission_completed'] = False

                    # 2. Xử lý Avatar và tính toán % Vòng tròn tiến độ
                    student_info = next(item for item in students_in_class if item["student_name"] == selected_name)
                    avatar_src = f"data:image/jpeg;base64,{student_info['avatar']}" if student_info['avatar'] else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    
                    if st.session_state['mission_completed']:
                        bg_css = "background: conic-gradient(red, orange, yellow, green, blue, indigo, violet, red); animation: spin 3s linear infinite;"
                        progress_text = "Well Done!"
                        chat_msg = f"🌈 Excellent job, {selected_name}! You are a star!"
                    else:
                        if len(st.session_state['playlist']) > 0:
                            total_q = len(st.session_state['playlist'])
                            curr_idx = st.session_state['current_q']
                            
                            gradient_stops = []
                            deg_per_q = 360 / total_q
                            for i in range(total_q):
                                start_deg = i * deg_per_q
                                end_deg = (i + 1) * deg_per_q - 4 # Tạo độ hở cho các đốt
                                gap_end = (i + 1) * deg_per_q
                                
                                if i < curr_idx: color = "#00b894" # Xanh lá (Đã qua)
                                elif i == curr_idx: color = "#feca57" # Vàng (Đang làm)
                                else: color = "#dfe6e9" # Xám (Chưa tới)
                                
                                gradient_stops.append(f"{color} {start_deg}deg {end_deg}deg")
                                gradient_stops.append(f"transparent {end_deg}deg {gap_end}deg")
                            
                            bg_css = f"background: conic-gradient({', '.join(gradient_stops)});"
                            progress_text = f"{curr_idx + 1}/{total_q}"
                            chat_msg = f"🚀 Keep going, {selected_name}!"
                        else:
                            bg_css = "background: #dfe6e9;"
                            progress_text = "Ready"
                            chat_msg = f"🎉 Hello {selected_name}!"

                    # Giao diện Floating Widget
                    floating_html = f"""
                    <style>
                        .floating-widget {{
                            position: fixed; top: 50%; left: 3%; transform: translateY(-50%);
                            z-index: 99999; display: flex; align-items: center; gap: 15px; pointer-events: none;
                        }}
                        .circular-progress-container {{
                            position: relative; width: 140px; height: 140px; border-radius: 50%;
                            display: flex; align-items: center; justify-content: center;
                            box-shadow: 0 8px 25px rgba(0,0,0,0.15); pointer-events: auto; overflow: hidden;
                        }}
                        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
                        .circular-progress-bg {{
                            position: absolute; width: 100%; height: 100%; border-radius: 50%; {bg_css}
                        }}
                        .circular-progress-container::after {{
                            content: ""; position: absolute; width: 120px; height: 120px;
                            background-color: white; border-radius: 50%; z-index: 1;
                        }}
                        .avatar-img-float {{
                            width: 110px; height: 110px; border-radius: 50%; object-fit: cover;
                            z-index: 2; border: 2px solid #f1f2f6;
                        }}
                        .progress-badge {{
                            position: absolute; bottom: 0px; left: 50%; transform: translateX(-50%);
                            background: #ff7675; color: white; padding: 5px 15px; border-radius: 20px;
                            font-weight: 900; font-size: 14px; border: 3px solid white; z-index: 3;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                        }}
                        .mini-chat {{
                            background: white; padding: 12px 20px; border-radius: 15px;
                            border-left: 5px solid #00b894; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                            font-size: 16px; font-weight: bold; color: #2d3436; position: relative;
                            animation: floatUpDown 3s ease-in-out infinite; pointer-events: auto; white-space: nowrap;
                        }}
                        .mini-chat::before {{
                            content: ''; position: absolute; left: -10px; top: 50%; transform: translateY(-50%);
                            border-top: 10px solid transparent; border-bottom: 10px solid transparent; border-right: 10px solid white;
                        }}
                        @keyframes floatUpDown {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
                        @media (max-width: 1024px) {{
                            .floating-widget {{ top: auto; bottom: 20px; left: 20px; transform: none; }}
                            .circular-progress-container {{ width: 100px; height: 100px; }}
                            .circular-progress-container::after {{ width: 84px; height: 84px; }}
                            .avatar-img-float {{ width: 76px; height: 76px; }}
                            .mini-chat {{ display: none; }} 
                        }}
                    </style>
                    <div class="floating-widget">
                        <div class="circular-progress-container">
                            <div class="circular-progress-bg"></div>
                            <img src="{avatar_src}" class="avatar-img-float">
                            <div class="progress-badge">{progress_text}</div>
                        </div>
                        <div class="mini-chat">{chat_msg}</div>
                    </div>
                    """
                    st.markdown(floating_html, unsafe_allow_html=True)
                    st.markdown("---")

                    # 3. ĐIỀU HƯỚNG 3 TRẠNG THÁI: HOÀN THÀNH / CHỌN BÀI / ĐANG CHƠI
                    if st.session_state['mission_completed']:
                        st.balloons()
                        st.markdown("<h2 style='text-align: center; color: #00b894;'>🎉 RAINBOW UNLOCKED! 🎉</h2>", unsafe_allow_html=True)
                        st.info("You have successfully completed all challenges in this mission!")
                        if st.button("🚀 CHOOSE ANOTHER MISSION", type="primary", use_container_width=True):
                            st.session_state['mission_completed'] = False
                            st.rerun()

                    elif len(st.session_state['playlist']) == 0:
                        st.markdown("### 🎯 CHOOSE YOUR MISSION")
                        
                        df_curriculum = get_curriculum_structure()
                        
                        if df_curriculum.empty:
                            st.warning("📭 Chưa có chương trình học nào được thiết lập. Đợi thầy cô cập nhật nhé!")
                        else:
                            # Bộ lọc Skill nắm trùm toàn bộ
                            sel_skill = st.selectbox("⚡ Choose Skill:", ["All", "Listening", "Reading & Writing", "Vocabulary", "Speaking"])
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Tách lộ trình bằng Tabs trực quan
                            tab_book, tab_topic = st.tabs(["📚 Lộ trình Sách giáo khoa", "🏆 Lộ trình Luyện thi (Topic)"])
                            
                            with tab_book:
                                col_b, col_u = st.columns(2)
                                with col_b:
                                    books = sorted(df_curriculum['book'].dropna().unique().tolist())
                                    sel_book = st.selectbox("📖 Select Book:", books) if books else st.selectbox("📖 Select Book:", ["N/A"])
                                with col_u:
                                    if books:
                                        units = sorted(df_curriculum[df_curriculum['book'] == sel_book]['unit'].dropna().unique().tolist())
                                        sel_unit = st.selectbox("🏷️ Select Unit:", units) if units else st.selectbox("🏷️ Select Unit:", ["N/A"])
                                    else:
                                        sel_unit = "N/A"
                                        
                                btn_start_book = st.button("🚀 START BOOK MISSION", type="primary", use_container_width=True, key="btn_book")

                            with tab_topic:
                                col_l, col_t = st.columns(2)
                                with col_l:
                                    levels = ["Starter", "Mover", "Flyer"] 
                                    sel_level = st.selectbox("🎓 Select Level:", levels)
                                with col_t:
                                    topics = sorted(df_curriculum[df_curriculum['level'] == sel_level]['topic'].dropna().unique().tolist())
                                    sel_topic = st.selectbox("🌟 Select Topic:", topics) if topics else st.selectbox("🌟 Select Topic:", ["N/A"])
                                    
                                btn_start_topic = st.button("🚀 START TOPIC MISSION", type="primary", use_container_width=True, key="btn_topic")

                            # Xử lý Logic bấm nút (Bấm tab nào thì lấy mode tab đó)
                            if btn_start_book or btn_start_topic:
                                mode = "book" if btn_start_book else "topic"
                                with st.spinner("Shuffling questions and preparing missions..."):
                                    try:
                                        all_qs = get_questions(
                                            mode=mode, skill=sel_skill, 
                                            book=sel_book if mode=="book" else None, 
                                            unit=sel_unit if mode=="book" else None,
                                            level=sel_level if mode=="topic" else None,
                                            topic=sel_topic if mode=="topic" else None
                                        )
                                        
                                        if not all_qs:
                                            st.warning("📭 Oops! No missions found for this selection. Please try another!")
                                        else:
                                            st.session_state['all_questions'] = all_qs
                                            
                                            # Bốc các dạng bài tập tương tác (Ex1, 2, 5, 6)
                                            quick_qs = [q for q in all_qs if q['ex_type'] in ['Ex1', 'Ex2', 'Ex5', 'Ex6']]
                                            
                                            if not quick_qs:
                                                st.warning("⚠️ Oop! Không có bài tập nào cho mục này. Bé Xu đang đi tìm thêm!")
                                            else:
                                                # --- BẮT ĐẦU LOGIC PHÂN LOẠI CÂU CHUYỆN VÀ CÂU LẺ ---
                                                bundles = {}
                                                standalones = []
                                                for q in quick_qs:
                                                    bid = q.get('bundle_id')
                                                    if bid and str(bid).strip() and str(bid).strip().lower() not in ['nan', 'none', '']:
                                                        if bid not in bundles: bundles[bid] = []
                                                        bundles[bid].append(q)
                                                    else:
                                                        standalones.append(q)
                                                        
                                                selected_playlist = []
                                                
                                                if bundles:
                                                    # TRƯỜNG HỢP 1: CÓ BỘ CÂU HỎI -> TỔNG 6 CÂU
                                                    chosen_bid = random.choice(list(bundles.keys()))
                                                    story_qs = sorted(bundles[chosen_bid], key=lambda x: x.get('id', 0)) 
                                                    selected_playlist.extend(story_qs)
                                                    
                                                    slots_left = 6 - len(selected_playlist)
                                                    if slots_left > 0 and standalones:
                                                        fillers = random.sample(standalones, min(slots_left, len(standalones)))
                                                        selected_playlist.extend(fillers)
                                                else:
                                                    # TRƯỜNG HỢP 2: KHÔNG CÓ BỘ (Toàn câu lẻ) -> TỔNG 5 CÂU
                                                    if standalones:
                                                        fillers = random.sample(standalones, min(5, len(standalones)))
                                                        selected_playlist.extend(fillers)
                                                        random.shuffle(selected_playlist)
                                                # ---------------------------------------------------
                                                
                                                # Bắt đầu đưa vào playlist cho học sinh chơi
                                                st.session_state['playlist'] = selected_playlist
                                                st.session_state['current_q'] = 0
                                                st.rerun()
                                    except Exception as e:
                                        st.error(f"⚠️ Error fetching missions: {e}")

                    else:
                        # TRẠNG THÁI HIỂN THỊ BÀI TẬP 
                        total_q = len(st.session_state['playlist'])
                        curr_idx = st.session_state['current_q']
                        current_q_data = st.session_state['playlist'][curr_idx]
                        
                        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
                        with col_nav2:
                            btn_label = "FINISH MISSION 🌟" if curr_idx == total_q - 1 else "NEXT MISSION ➔"
                            if st.button(btn_label, use_container_width=True, type="secondary"):
                                if curr_idx < total_q - 1:
                                    st.session_state['current_q'] += 1
                                    st.rerun()
                                else:
                                    st.session_state['mission_completed'] = True
                                    st.session_state['playlist'] = []
                                    st.rerun()
                                    
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        ex_type = current_q_data.get('ex_type', '')
                        if ex_type == 'Ex1': run_ex1_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex2': run_ex2_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex3': run_ex3_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex4': run_ex4_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex5': run_ex5_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex6': run_ex6_dynamic(current_q_data, curr_idx)
                        else: st.error("⚠️ System cannot recognize this mission type.")
                
# ================= 6. TEACHER PORTAL =================
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
                st.session_state['current_teacher_username'] = res.data[0]['username']
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
        
        tab_assign, tab_bank, tab_student = st.tabs(["🛠️ Assign Homework", "🏦 Question Bank", "👧🏻 Manage Students"])
        book_list = ["Kid's Box 1", "Kid's Box 2", "Kid's Box 3", "Kid's Box 4", "Kid's Box 5", "Kid's Box 6"]
        
        with tab_assign:
            st.markdown("#### Create New Session")
            col1, col2 = st.columns(2)
            with col1:
                sach = st.selectbox("📚 Select Book:", book_list)
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

        with tab_bank:
            st.markdown("#### 🏦 Import Questions from Excel")
            st.info("💡 **Instruction:** The uploaded Excel file must have exact headers: Book, Unit, Topic, Level, Skill, Bundle, Type, Question, Answer, Options")
            
            uploaded_file = st.file_uploader("📥 Upload Excel file (.xlsx) here", type=["xlsx"])
            
            if uploaded_file:
                try:
                    import pandas as pd
                    df = pd.read_excel(uploaded_file)
                    df = df.dropna(how='all')
                    
                    st.write("👀 **Data Preview:**")
                    st.dataframe(df.head(5), use_container_width=True)
                    
                    if st.button("🚀 UPLOAD TO DATABASE", type="primary", use_container_width=True):
                        with st.spinner("Đang đẩy dữ liệu lên Supabase..."):
                            import time
                            current_bundle_id = None # Biến theo dõi bộ câu hỏi
                            rows_to_insert = []
                            
                            try:
                                for index, row in df.iterrows():
                                    # LOGIC TỰ ĐỘNG GOM BỘ (BUNDLE) THÔNG MINH CỦA BỒ
                                    bundle_val = str(row.get('Bundle', '')).strip().lower()
                                    if bundle_val in ['yes', 'y', 'có', 'co', '1']:
                                        if current_bundle_id is None:
                                            # Tự sinh mã duy nhất khi bắt đầu một bộ mới
                                            current_bundle_id = f"bundle_{int(time.time())}_{index}"
                                        assigned_bundle_id = current_bundle_id
                                    else:
                                        # Hết bộ thì reset lại
                                        current_bundle_id = None
                                        assigned_bundle_id = ""

                                    rows_to_insert.append({
                                        "book": str(row.get('Book', '')).strip(),
                                        "unit": str(row.get('Unit', '')).strip(),
                                        "topic": str(row.get('Topic', '')).strip(),
                                        "level": str(row.get('Level', '')).strip(), 
                                        "skill": str(row.get('Skill', 'All')).strip() or "All", 
                                        "bundle_id": assigned_bundle_id,
                                        "ex_type": str(row.get('Type', '')).strip(),
                                        "question": str(row.get('Question', '')).strip(),
                                        "answer": str(row.get('Answer', '')).strip(),
                                        "options": str(row.get('Options', '')).strip() if pd.notna(row.get('Options')) else ""
                                    })
                                
                                # Đẩy lên Supabase theo lô (mỗi lần 200 câu) để chống nghẽn
                                for i in range(0, len(rows_to_insert), 200):
                                    supabase.table("questions").insert(rows_to_insert[i:i+200]).execute()
                                
                                # XÓA CACHE ĐỂ GIAO DIỆN HỌC SINH CẬP NHẬT NGAY LẬP TỨC
                                get_questions.clear()
                                get_curriculum_structure.clear()
                                
                                st.success(f"🎉 Xuất sắc! Đã tải lên thành công {len(rows_to_insert)} câu hỏi!")
                                st.balloons()
                            except Exception as err:
                                st.error(f"⚠️ Lỗi hệ thống khi tải dữ liệu: {err}")
                    
            st.markdown("---")
            
            st.markdown("#### 📋 Question Library (Cloud Database)")
            
            col_loc1, col_loc2 = st.columns(2)
            with col_loc1:
                filter_book = st.selectbox("📚 Filter by Book:", ["All"] + book_list)
            with col_loc2:
                if st.button("🔄 Refresh List", use_container_width=True):
                    st.rerun()
            
            try:
                if filter_book == "All":
                    res_q = supabase.table("questions").select("*").execute()
                else:
                    res_q = supabase.table("questions").select("*").eq("book", filter_book).execute()
                    
                db_questions = res_q.data
                
                if db_questions:
                    df_view = pd.DataFrame(db_questions)
                    df_view = df_view[['id', 'book', 'unit', 'topic', 'ex_type', 'question', 'answer', 'options']]
                    
                    st.dataframe(df_view, use_container_width=True, hide_index=True)
                    st.caption(f"📊 Total: **{len(db_questions)}** questions in database.")
                else:
                    st.warning("📭 Database is empty. Please upload an Excel file!")
            except Exception as e:
                st.error("⚠️ Supabase connection error! Please check your table structure.")

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
                
                if s_avatar:
                    st.info("✂️ Drag and resize the blue box to frame the face. (The square will automatically become a circle later!)")
                    img = Image.open(s_avatar)
                    cropped_img = st_cropper(img, aspect_ratio=(1, 1), box_color='#0984e3', return_type='image')
                    
                    buffered = io.BytesIO()
                    cropped_img.save(buffered, format="PNG")
                    avatar_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                if st.button("➕ ADD STUDENT", type="primary"):
                    if s_name:
                        try:
                            supabase.table("students").insert({
                                "class_code": selected_code, "student_name": s_name, "avatar": avatar_b64
                            }).execute()
                            get_students_in_class.clear()
                            st.success(f"✅ Added {s_name} to class {selected_code} successfully!")
                            st.rerun() 
                        except Exception as e:
                            st.error(f"❌ Error adding student: {e}")
                    else:
                        st.error("⚠️ Please enter the student's name.")
                            
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

# ================= 7. ADMIN PORTAL =================
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
                            
        with tab_cls:
            st.markdown("**Create Official Classes & Assign Teachers**")
            
            res_tch = supabase.table("teachers").select("*").execute()
            db_teachers = res_tch.data
            
            if not db_teachers:
                st.warning("⚠️ Please create at least one Teacher account first!")
            else:
                with st.form("add_class_admin", clear_on_submit=True):
                    c_code = st.text_input("Class Code (e.g., ENG101):").strip().upper()
                    c_name = st.text_input("Class Name (e.g., Movers 1):").strip()
                    
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
                                get_class_info.clear() 
                                st.success(f"✅ Class {c_name} assigned to teacher '{selected_t_username}' successfully!")
                            except Exception as e:
                                st.error(f"❌ Error adding class: {e}")
                        else:
                            st.error("⚠️ Please enter both Code and Name.")
