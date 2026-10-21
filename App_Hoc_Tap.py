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
import hashlib
import hmac
import secrets as pysecrets
from supabase import create_client, Client
import mascot_config

# Khởi tạo kết nối (Cache_resource giúp kết nối chạy 1 lần duy nhất)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# -----------------------------------------------------------------------------
# 🔐 BĂM MẬT KHẨU (PBKDF2-SHA256, định dạng: pbkdf2$<salt_hex>$<hash_hex>)
# -----------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = pysecrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200_000)
    return f"pbkdf2${salt}${dk.hex()}"

def verify_password(password: str, stored) -> bool:
    stored = str(stored or "")
    if stored.startswith("pbkdf2$"):
        try:
            _, salt, hash_hex = stored.split("$")
            dk = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200_000)
            return hmac.compare_digest(dk.hex(), hash_hex)
        except Exception:
            return False
    # Tương thích mật khẩu cũ lưu dạng plaintext
    return bool(stored) and hmac.compare_digest(password.encode(), stored.encode())

# -----------------------------------------------------------------------------
# 🔥 HỆ THỐNG TỐI ƯU TỐC ĐỘ (CACHE) - TRÁNH LAG KHI RERUN 🔥
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def get_class_info(class_code):
    try:
        return supabase.table("classes").select("*").eq("class_code", class_code).execute().data
    except Exception as e:
        print(f"Lỗi đọc thông tin lớp: {e}")
        return None

@st.cache_data(ttl=300)
def get_students_in_class(class_code):
    try:
        return supabase.table("students").select("*").eq("class_code", class_code).execute().data
    except Exception as e:
        print(f"Lỗi đọc học sinh trong lớp: {e}")
        return []

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
    try:
        query = supabase.table("questions").select("*")
        if skill != "All":
            query = query.eq("skill", skill)
        if mode == "book":
            if book:
                query = query.eq("book", book)
            if unit:
                if isinstance(unit, list):
                    query = query.in_("unit", unit)
                else:
                    query = query.eq("unit", unit)
        elif mode == "topic":
            if level:
                query = query.eq("level", level)
            if topic:
                query = query.eq("topic", topic)
        return query.execute().data
    except Exception as e:
        print(f"Lỗi lấy câu hỏi: {e}")
        return []

@st.cache_data(ttl=60)
def get_active_assignments(class_code=None, teacher_username=None):
    try:
        now_str = datetime.datetime.now().isoformat()
        res = supabase.table("assignments").select("*").gte("deadline", now_str).order("deadline", desc=False).execute()
        raw = res.data or []
        filtered = []
        for a in raw:
            c_code = a.get("class_code")
            if not class_code or not c_code or c_code == "ALL" or c_code == class_code:
                if not teacher_username or a.get("teacher_username") == teacher_username:
                    filtered.append(a)
        return filtered
    except Exception as e:
        print(f"Lỗi đọc bài tập về nhà: {e}")
        return []

def save_study_log(log_data):
    try:
        supabase.table("study_logs").insert(log_data).execute()
        get_class_study_logs.clear()
        return True
    except Exception as e:
        print(f"Lỗi lưu kết quả học tập (bảng study_logs): {e}")
        return False

@st.cache_data(ttl=30)
def get_class_study_logs(class_code):
    try:
        res = supabase.table("study_logs").select("*").eq("class_code", class_code).order("completed_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        print(f"Lỗi đọc lịch sử học tập lớp {class_code}: {e}")
        return []

@st.cache_data(ttl=60)
def get_teacher_assignments(teacher_username):
    try:
        res = supabase.table("assignments").select("*").eq("teacher_username", teacher_username).order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        print(f"Lỗi đọc bài tập giáo viên: {e}")
        return []

def build_mission_playlist(all_qs, max_q=20):
    quick_qs = [q for q in all_qs if q.get('ex_type') in ['Ex1', 'Ex2', 'Ex3', 'Ex4', 'Ex5', 'Ex6', 'Ex7', 'Ex8']]
    if not quick_qs:
        return []
    
    SET_TYPES = ['Ex3', 'Ex4', 'Ex5', 'Ex7', 'Ex8']
    set_reps = {}
    bundles = {}
    standalones = []
    for q in quick_qs:
        bid = q.get('bundle_id')
        if q.get('ex_type') in SET_TYPES:
            set_reps.setdefault(q['ex_type'], q)
        elif bid and str(bid).strip() and str(bid).strip().lower() not in ['nan', 'none', '']:
            if bid not in bundles: bundles[bid] = []
            bundles[bid].append(q)
        else:
            standalones.append(q)
    standalones.extend(set_reps.values())
    
    selected_playlist = []
    if bundles:
        chosen_bid = random.choice(list(bundles.keys()))
        story_qs = sorted(bundles[chosen_bid], key=lambda x: x.get('id', 0))
        selected_playlist.extend(story_qs)
        
        slots_left = max_q - len(selected_playlist)
        if slots_left > 0 and standalones:
            fillers = random.sample(standalones, min(slots_left, len(standalones)))
            selected_playlist.extend(fillers)
    else:
        if standalones:
            fillers = random.sample(standalones, min(max_q, len(standalones)))
            selected_playlist.extend(fillers)
            random.shuffle(selected_playlist)
    return selected_playlist
    
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
        bg_css = f'background-image: url("data:{mime};base64,{bin_str}") !important;'
    except Exception as e: 
        st.error(f"⚠️ Background image not found: {e}")
        bg_css = 'background-color: #f5f6fa !important;'
    
    bg_opacity = "rgba(255, 255, 255, 0.05)" if current_role is None else "rgba(255, 255, 255, 0.45)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

        /* 1. Dán hình nền thẳng vào lớp đáy cùng của Streamlit */
        .stApp {{
            {bg_css}
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        /* 2. Biến các lớp che phủ bên trên thành kính trong suốt */
        [data-testid="stAppViewContainer"], 
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        /* Căn giữa và giới hạn độ rộng thông minh trên màn hình vi tính */
        .block-container {{
            max-width: 1200px !important;
        }}

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
        
        /* Nút Secondary (Next Mission) - Nền tối chữ vàng siêu ngầu */
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
        
        [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] {{
            background: {bg_opacity} !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-radius: 20px;
            padding: 2rem !important;
            margin-top: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
    
    from Exercise_Components import run_ex1_dynamic, run_ex2_dynamic, run_ex3_dynamic, run_ex4_dynamic, run_ex5_dynamic, run_ex6_dynamic, run_ex7_dynamic, run_ex8_dynamic

    # ---------------------------------------------------------------------
    # GIAO DIỆN ĐĂNG NHẬP & LUỒNG HỌC TẬP CHÍNH
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='text-align: center; color: #0984e3;'>🎒 Student Login</h3>", unsafe_allow_html=True)
    
    class_code_input = st.text_input("🔑 Enter your Class Code:").strip().upper()
    
    if class_code_input:
        class_data = get_class_info(class_code_input)
        
        if class_data is None:
            st.error("⚠️ Không thể kết nối tới cơ sở dữ liệu Supabase! Nếu dự án không hoạt động hơn 7 ngày, Supabase có thể đã tự động Tạm dừng (Paused). Vui lòng vào https://supabase.com/dashboard bấm 'Restore project' rồi thử lại nhé.")
        elif not class_data:
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
                    
                    # 1. State initialization
                    if 'playlist' not in st.session_state:
                        st.session_state['playlist'] = []
                        st.session_state['current_q'] = 0
                        st.session_state['all_questions'] = []
                    if 'mission_completed' not in st.session_state:
                        st.session_state['mission_completed'] = False
                    if 'active_mission_info' not in st.session_state:
                        st.session_state['active_mission_info'] = None
                    if 'last_completed_info' not in st.session_state:
                        st.session_state['last_completed_info'] = None

                    # 2. Companion Mascot Resolution
                    student_info = next(item for item in students_in_class if item["student_name"] == selected_name)
                    is_mascot, mascot_obj, avatar_src = mascot_config.parse_student_avatar(student_info.get('avatar'))
                    current_mascot_id = mascot_obj['id'] if (is_mascot and mascot_obj) else mascot_config.DEFAULT_MASCOT_ID
                    active_mascot = mascot_config.get_mascot(current_mascot_id)
                    mascot_js_data = mascot_config.get_mascot_js_payload(current_mascot_id)

                    # 3. Companion Header & Interactive Switcher (100% English)
                    col_comp1, col_comp2 = st.columns([3, 1])
                    with col_comp1:
                        st.markdown(f"🐾 **Study Companion:** {active_mascot['badge']} **{active_mascot['name']}** — *{active_mascot['personality']}*")
                    with col_comp2:
                        toggle_companion = st.toggle("🎨 Change", key=f"tgl_mascot_{selected_name}")

                    if toggle_companion:
                        st.markdown("##### 🌟 Choose Your Study Companion")
                        st.caption("Pick a mascot companion to cheer you on and react to your answers!")
                        all_mascots = mascot_config.get_all_mascots()
                        m_cols = st.columns(len(all_mascots))
                        for i, m_item in enumerate(all_mascots):
                            with m_cols[i]:
                                is_curr = (m_item['id'] == active_mascot['id'])
                                border_style = "2px solid #00b894; background: #e6fffa;" if is_curr else "1px solid #dfe6e9; background: white;"
                                st.markdown(f"""
                                <div style="text-align: center; padding: 10px 6px; border-radius: 12px; border: {border_style}; margin-bottom: 8px;">
                                    <img src="{m_item['expressions']['idle']}" style="width: 55px; height: 55px; border-radius: 50%; object-fit: cover; margin-bottom: 6px;">
                                    <div style="font-weight: 800; font-size: 13px; color: #2d3436;">{m_item['badge']} {m_item['name']}</div>
                                    <div style="font-size: 11px; color: #6c5ce7; font-weight: bold; margin: 3px 0;">{m_item['personality']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                if not is_curr:
                                    if st.button(f"Pick {m_item['badge']}", key=f"btn_pick_{m_item['id']}", use_container_width=True):
                                        try:
                                            supabase.table("students").update({"avatar": f"mascot:{m_item['id']}"}).eq("class_code", class_code_input).eq("student_name", selected_name).execute()
                                            get_students_in_class.clear()
                                            st.success(f"🎉 {m_item['name']} is now your companion!")
                                            st.rerun()
                                        except Exception as err:
                                            st.error(f"Could not update companion: {err}")
                                else:
                                    st.caption("✅ Selected")
                        st.markdown("---")

                    # 4. Circular Progress & Reactive Mascot Widget
                    if st.session_state['mission_completed']:
                        bg_css = "background: conic-gradient(red, orange, yellow, green, blue, indigo, violet, red); animation: spin 3s linear infinite;"
                        progress_text = "Well Done!"
                        chat_msg = f"🏆 {active_mascot['quotes']['celebrate'][0]}"
                        widget_img_src = active_mascot['expressions']['celebrate']
                    else:
                        if len(st.session_state['playlist']) > 0:
                            total_q = len(st.session_state['playlist'])
                            curr_idx = st.session_state['current_q']
                            
                            gradient_stops = []
                            deg_per_q = 360 / total_q
                            for i in range(total_q):
                                start_deg = i * deg_per_q
                                end_deg = (i + 1) * deg_per_q - 4
                                gap_end = (i + 1) * deg_per_q
                                
                                if i < curr_idx: color = "#00b894"
                                elif i == curr_idx: color = "#feca57"
                                else: color = "#dfe6e9"
                                
                                gradient_stops.append(f"{color} {start_deg}deg {end_deg}deg")
                                gradient_stops.append(f"transparent {end_deg}deg {gap_end}deg")
                            
                            bg_css = f"background: conic-gradient({', '.join(gradient_stops)});"
                            progress_text = f"{curr_idx + 1}/{total_q}"
                            chat_msg = f"🚀 Keep going, {selected_name}!"
                            widget_img_src = avatar_src
                        else:
                            bg_css = "background: #dfe6e9;"
                            progress_text = "Ready"
                            chat_msg = active_mascot['quotes']['welcome'][0]
                            widget_img_src = avatar_src

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
                            transition: transform 0.3s ease;
                        }}
                        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
                        @keyframes mascotBounce {{
                            0%, 100% {{ transform: scale(1); }}
                            30% {{ transform: scale(1.18) translateY(-10px); }}
                            60% {{ transform: scale(0.95); }}
                        }}
                        @keyframes mascotWobble {{
                            0%, 100% {{ transform: translateX(0); }}
                            20% {{ transform: translateX(-8px) rotate(-6deg); }}
                            40% {{ transform: translateX(8px) rotate(6deg); }}
                            60% {{ transform: translateX(-5px) rotate(-3deg); }}
                            80% {{ transform: translateX(5px) rotate(3deg); }}
                        }}
                        .mascot-bounce {{
                            animation: mascotBounce 0.65s ease-in-out !important;
                            box-shadow: 0 0 25px #55efc4 !important;
                        }}
                        .mascot-wobble {{
                            animation: mascotWobble 0.65s ease-in-out !important;
                            box-shadow: 0 0 25px #ff7675 !important;
                        }}
                        .circular-progress-bg {{
                            position: absolute; width: 100%; height: 100%; border-radius: 50%; {bg_css}
                        }}
                        .circular-progress-container::after {{
                            content: ""; position: absolute; width: 120px; height: 120px;
                            background-color: white; border-radius: 50%; z-index: 1;
                        }}
                        .avatar-img-float {{
                            width: 110px; height: 110px; border-radius: 50%; object-fit: cover;
                            z-index: 2; border: 2px solid #f1f2f6; transition: all 0.25s ease;
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
                            font-size: 15px; font-weight: bold; color: #2d3436; position: relative;
                            animation: floatUpDown 3s ease-in-out infinite; pointer-events: auto; white-space: nowrap;
                            max-width: 320px; text-overflow: ellipsis; overflow: hidden;
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
                        <div class="circular-progress-container" id="mascot_circle">
                            <div class="circular-progress-bg"></div>
                            <img id="mascot_avatar_img" src="{widget_img_src}" class="avatar-img-float">
                            <div class="progress-badge">{progress_text}</div>
                        </div>
                        <div class="mini-chat" id="mascot_chat_msg">{chat_msg}</div>
                    </div>

                    <script>
                        (function() {{
                            const mascotData = {mascot_js_data};
                            const defaultIdleImg = "{widget_img_src}";
                            const defaultIdleMsg = "{chat_msg}";
                            let resetTimer = null;

                            window.addEventListener('message', function(event) {{
                                if (!event.data || event.data.type !== 'MASCOT_REACTION') return;
                                const status = event.data.status;
                                const imgEl = document.getElementById('mascot_avatar_img');
                                const chatEl = document.getElementById('mascot_chat_msg');
                                const circleEl = document.getElementById('mascot_circle');

                                if (resetTimer) clearTimeout(resetTimer);

                                if (status === 'correct') {{
                                    if (imgEl && mascotData.expressions && mascotData.expressions.correct) {{
                                        imgEl.src = mascotData.expressions.correct;
                                    }}
                                    if (chatEl && mascotData.quotes && mascotData.quotes.correct) {{
                                        const quotes = mascotData.quotes.correct;
                                        chatEl.innerText = quotes[Math.floor(Math.random() * quotes.length)];
                                    }}
                                    if (circleEl) {{
                                        circleEl.classList.remove('mascot-bounce', 'mascot-wobble');
                                        void circleEl.offsetWidth;
                                        circleEl.classList.add('mascot-bounce');
                                    }}
                                }} else if (status === 'wrong') {{
                                    if (imgEl && mascotData.expressions && mascotData.expressions.encourage) {{
                                        imgEl.src = mascotData.expressions.encourage;
                                    }}
                                    if (chatEl && mascotData.quotes && mascotData.quotes.wrong) {{
                                        const quotes = mascotData.quotes.wrong;
                                        chatEl.innerText = quotes[Math.floor(Math.random() * quotes.length)];
                                    }}
                                    if (circleEl) {{
                                        circleEl.classList.remove('mascot-bounce', 'mascot-wobble');
                                        void circleEl.offsetWidth;
                                        circleEl.classList.add('mascot-wobble');
                                    }}
                                }}

                                resetTimer = setTimeout(function() {{
                                    if (imgEl) imgEl.src = defaultIdleImg;
                                    if (chatEl) chatEl.innerText = defaultIdleMsg;
                                    if (circleEl) circleEl.classList.remove('mascot-bounce', 'mascot-wobble');
                                }}, 3600);
                            }});
                        }})();
                    </script>
                    """
                    st.markdown(floating_html, unsafe_allow_html=True)
                    st.markdown("---")

                    # 5. NAVIGATION & THREE MAIN STATES (100% English)
                    if st.session_state['mission_completed']:
                        st.balloons()
                        if lottie_success:
                            st_lottie(lottie_success, height=200, key="success_anim")
                        
                        last_info = st.session_state.get('last_completed_info') or {}
                        m_title = last_info.get('title', 'Learning Mission')
                        stars_count = last_info.get('stars', 20)
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); padding: 30px; border-radius: 20px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0, 184, 148, 0.3); margin-bottom: 25px;">
                            <h1 style="color: #ffeaa7; margin-bottom: 10px; font-size: 32px;">🌟 RAINBOW UNLOCKED! 🌟</h1>
                            <h3 style="color: white; margin-top: 0;">Congratulations <b>{selected_name}</b> and <b>{active_mascot['name']}</b>!</h3>
                            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 12px; display: inline-block; margin: 12px 0;">
                                <span style="font-size: 17px; font-weight: bold;">🎯 {m_title}</span>
                            </div>
                            <div style="font-size: 26px; font-weight: 900; color: #feca57; margin: 10px 0;">
                                {'⭐' * min(stars_count, 10)} +{stars_count} STARS!
                            </div>
                            <p style="margin-top: 10px; font-size: 14px; opacity: 0.95;">
                                ✅ Your stars and achievements have been submitted to your class leaderboard!
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🚀 CHOOSE ANOTHER MISSION", type="primary", use_container_width=True):
                            st.session_state['mission_completed'] = False
                            st.session_state['last_completed_info'] = None
                            st.session_state['active_mission_info'] = None
                            st.session_state['playlist'] = []
                            st.rerun()

                    elif len(st.session_state['playlist']) == 0:
                        # SECTION A: ACTIVE HOMEWORK (100% English)
                        active_hw_list = get_active_assignments(class_code_input)
                        if active_hw_list:
                            st.markdown("### 📌 CLASS HOMEWORK ASSIGNMENTS")
                            for hw in active_hw_list:
                                hw_id = hw.get('id')
                                hw_book = hw.get('book', 'Kid\'s Box')
                                hw_units = hw.get('units', [])
                                hw_skill = hw.get('skill', 'All')
                                hw_deadline = hw.get('deadline', '')
                                
                                if isinstance(hw_units, list):
                                    units_txt = ", ".join(hw_units)
                                else:
                                    units_txt = str(hw_units)
                                
                                dl_display = hw_deadline[:16].replace('T', ' ') if hw_deadline else 'No deadline'
                                
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); padding: 18px 22px; border-radius: 18px; color: white; margin-bottom: 12px; box-shadow: 0 8px 25px rgba(108, 92, 231, 0.25);">
                                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                                        <span style="font-size: 13px; font-weight: bold; background: rgba(255,255,255,0.25); padding: 5px 12px; border-radius: 12px;">⏰ Due Date: {dl_display}</span>
                                        <span style="font-size: 13px; font-weight: bold; background: #ffeaa7; color: #2d3436; padding: 5px 12px; border-radius: 12px;">🎯 {hw_skill}</span>
                                    </div>
                                    <h3 style="margin: 10px 0 5px 0; color: white !important;">📖 {hw_book} - {units_txt}</h3>
                                    <p style="margin: 0; font-size: 14px; opacity: 0.95;">Official homework mission for class {class_code_input} — Complete to earn Stars!</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button(f"🎯 START HOMEWORK MISSION ({hw_book})", key=f"btn_hw_{hw_id}", type="primary", use_container_width=True):
                                    with st.spinner("Preparing your homework mission..."):
                                        all_qs = get_questions(
                                            mode="book",
                                            skill=hw_skill if hw_skill else "All",
                                            book=hw_book,
                                            unit=hw_units
                                        )
                                        if not all_qs:
                                            st.warning("⚠️ Questions for this assignment are coming soon!")
                                        else:
                                            st.session_state['all_questions'] = all_qs
                                            mission_qs = build_mission_playlist(all_qs, max_q=20)
                                            if not mission_qs:
                                                st.warning("⚠️ No interactive exercises available for this unit yet.")
                                            else:
                                                st.session_state['playlist'] = mission_qs
                                                st.session_state['current_q'] = 0
                                                st.session_state['active_mission_info'] = {
                                                    'assignment_id': hw_id,
                                                    'title': f"Homework: {hw_book} ({units_txt})",
                                                    'skill': hw_skill,
                                                    'total_questions': len(mission_qs)
                                                }
                                                st.rerun()
                            st.markdown("---")

                        # SECTION B: FREE PRACTICE MISSIONS (100% English)
                        st.markdown("### 🎯 FREE PRACTICE MISSIONS")
                        
                        df_curriculum = get_curriculum_structure()
                        
                        if df_curriculum.empty:
                            st.warning("📭 Curriculum not loaded yet. Check back soon!")
                        else:
                            sel_skill = st.selectbox("⚡ Choose Skill:", ["All", "Listening", "Reading & Writing", "Vocabulary", "Speaking"])
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            tab_book, tab_topic = st.tabs(["📚 Textbook Path", "🏆 Exam Prep Path (Topic)"])
                            
                            with tab_book:
                                col_b, col_u = st.columns(2)
                                with col_b:
                                    books = sorted(df_curriculum['book'].dropna().unique().tolist())
                                    sel_book = st.selectbox("📖 Select Book:", books) if books else st.selectbox("📖 Select Book:", ["N/A"])
                                painted_units = sorted(df_curriculum[df_curriculum['book'] == sel_book]['unit'].dropna().unique().tolist()) if books else []
                                with col_u:
                                    sel_unit = st.selectbox("🏷️ Select Unit:", painted_units) if painted_units else st.selectbox("🏷️ Select Unit:", ["N/A"])
                                        
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
                                            mission_qs = build_mission_playlist(all_qs, max_q=20)
                                            
                                            if not mission_qs:
                                                st.warning("⚠️ No interactive exercises found for this selection.")
                                            else:
                                                st.session_state['playlist'] = mission_qs
                                                st.session_state['current_q'] = 0
                                                m_title = f"{sel_book} - {sel_unit}" if mode=="book" else f"{sel_level} - {sel_topic}"
                                                st.session_state['active_mission_info'] = {
                                                    'assignment_id': None,
                                                    'title': f"Practice: {m_title}",
                                                    'skill': sel_skill,
                                                    'total_questions': len(mission_qs)
                                                }
                                                st.rerun()
                                    except Exception as e:
                                        st.error(f"⚠️ Error fetching missions: {e}")

                    else:
                        # PLAYING EXERCISE STATE
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
                                    m_info = st.session_state.get('active_mission_info') or {}
                                    earned_stars = total_q
                                    log_payload = {
                                        "class_code": class_code_input,
                                        "student_name": selected_name,
                                        "assignment_id": m_info.get('assignment_id'),
                                        "mission_title": m_info.get('title', 'Quick Practice'),
                                        "skill": m_info.get('skill', 'All'),
                                        "total_questions": total_q,
                                        "stars_earned": earned_stars,
                                        "completed_at": datetime.datetime.now().isoformat()
                                    }
                                    save_study_log(log_payload)
                                    
                                    st.session_state['last_completed_info'] = {
                                        'title': m_info.get('title', 'Quick Practice'),
                                        'stars': earned_stars,
                                        'total': total_q
                                    }
                                    st.session_state['mission_completed'] = True
                                    st.session_state['playlist'] = []
                                    st.session_state['active_mission_info'] = None
                                    st.rerun()
                                    
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        ex_type = current_q_data.get('ex_type', '')
                        if ex_type == 'Ex1': run_ex1_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex2': run_ex2_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex3': run_ex3_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex4': run_ex4_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex5': run_ex5_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex6': run_ex6_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex7': run_ex7_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex8': run_ex8_dynamic(st.session_state['all_questions'], curr_idx)
                        else: st.error("⚠️ System cannot recognize this mission type.")
                
# ================= 6. TEACHER PORTAL =================
elif st.session_state['role'] == 'teacher':
    if not st.session_state['is_teacher_logged_in']:
        st.markdown("### 👨‍🏫 Teacher Login")
        u_tch = st.text_input("Username:")
        p_tch = st.text_input("Password:", type="password")
        if st.button("🔓 Login", type="primary"):
            try:
                res = supabase.table("teachers").select("*").eq("username", u_tch).execute()
                teacher = res.data[0] if res.data else None
                if teacher and verify_password(p_tch, teacher.get('password')):
                    # Tự động nâng cấp mật khẩu cũ (plaintext) sang dạng băm
                    if not str(teacher.get('password', '')).startswith("pbkdf2$"):
                        try:
                            supabase.table("teachers").update({"password": hash_password(p_tch)}).eq("username", teacher['username']).execute()
                        except Exception as e:
                            print(f"Không nâng cấp được mật khẩu: {e}")
                    st.session_state['is_teacher_logged_in'] = True
                    st.session_state['current_teacher'] = teacher['full_name']
                    st.session_state['current_teacher_username'] = teacher['username']
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please contact Admin.")
            except Exception as e:
                st.error("⚠️ Không thể kết nối tới cơ sở dữ liệu Supabase! Dự án có thể đang bị Tạm dừng (Paused) sau 7 ngày không hoạt động. Vui lòng vào https://supabase.com/dashboard để 'Restore project'.")
    else:
        c_title, c_btn = st.columns([4, 1])
        with c_title:
            st.success(f"✨ Welcome back, Teacher **{st.session_state['current_teacher']}**!")
        with c_btn:
            if st.button("🔒 Logout"):
                st.session_state['is_teacher_logged_in'] = False
                st.rerun()
            
        st.markdown("---")
        
        tab_assign, tab_reports, tab_bank, tab_student = st.tabs(["🛠️ Assign Homework", "📊 Learning Reports", "🏦 Question Bank", "👧🏻 Manage Students"])
        book_list = ["Kid's Box 1", "Kid's Box 2", "Kid's Box 3", "Kid's Box 4", "Kid's Box 5", "Kid's Box 6"]
        
        with tab_assign:
            st.markdown("#### 🛠️ Giao Bài Tập Về Nhà (Assign Homework)")
            
            # Lấy danh sách lớp của giáo viên
            try:
                res_tch_cls = supabase.table("classes").select("*").eq("teacher_username", st.session_state['current_teacher_username']).execute()
                teacher_classes = res_tch_cls.data or []
            except Exception:
                teacher_classes = []
                
            class_choices = ["ALL (Tất cả các lớp)"] + [f"{c['class_code']} - {c['class_name']}" for c in teacher_classes]
            
            col_cls, col_dur = st.columns([2, 1])
            with col_cls:
                c_target_class = st.selectbox("🏫 Giao cho lớp:", class_choices)
                chosen_class_code = "ALL" if c_target_class.startswith("ALL") else c_target_class.split(" - ")[0]
            with col_dur:
                thoi_gian = st.number_input("⏳ Thời hạn (Giờ):", min_value=1, value=48)
                
            col1, col2 = st.columns(2)
            with col1:
                sach = st.selectbox("📚 Select Book:", book_list)
                ky_nang = st.selectbox("🎯 Target Skill:", ["Listening", "Reading & Writing", "Speaking", "Vocabulary", "All"])
            with col2:
                units = st.multiselect("🏷️ Select Units:", ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7", "Unit 8"])
            
            if st.button("🚀 XÁC NHẬN GIAO BÀI (PUBLISH ASSIGNMENT)", type="primary", use_container_width=True):
                if not units:
                    st.error("⚠️ Vui lòng chọn ít nhất 1 Unit!")
                else:
                    deadline = datetime.datetime.now() + datetime.timedelta(hours=thoi_gian)
                    success_saved = False
                    try:
                        supabase.table("assignments").insert({
                            "teacher_username": st.session_state['current_teacher_username'],
                            "class_code": chosen_class_code,
                            "book": sach,
                            "units": units,
                            "skill": ky_nang,
                            "deadline": deadline.isoformat()
                        }).execute()
                        success_saved = True
                    except Exception as e:
                        try:
                            supabase.table("assignments").insert({
                                "teacher_username": st.session_state['current_teacher_username'],
                                "book": sach,
                                "units": units,
                                "skill": ky_nang,
                                "deadline": deadline.isoformat()
                            }).execute()
                            success_saved = True
                        except Exception as e2:
                            st.error(f"❌ Không thể lưu bài tập vào CSDL: {e2}")
                            
                    if success_saved:
                        get_active_assignments.clear()
                        get_teacher_assignments.clear()
                        st.success(f"🎉 Đã giao bài tập thành công cho {c_target_class}: {sach} ({', '.join(units)})! Hạn nộp: {deadline.strftime('%H:%M %d/%m/%Y')}")
                        st.rerun()

            st.markdown("---")
            st.markdown("#### 📋 Danh sách bài tập đã giao gần đây")
            tch_assignments = get_teacher_assignments(st.session_state['current_teacher_username'])
            if not tch_assignments:
                st.info("Chưa có bài tập nào được giao gần đây.")
            else:
                for a in tch_assignments[:5]:
                    a_units = ", ".join(a.get('units', [])) if isinstance(a.get('units'), list) else str(a.get('units', ''))
                    a_cls = a.get('class_code', 'ALL')
                    a_dl = a.get('deadline', '')[:16].replace('T', ' ')
                    st.caption(f"📌 **{a.get('book')}** ({a_units}) - Lớp: `{a_cls}` | Kỹ năng: `{a.get('skill')}` | Hạn chót: `{a_dl}`")

        with tab_reports:
            st.markdown("#### 📊 Báo cáo Học tập & Bảng Vàng Vinh Danh")
            
            try:
                res_tch_cls = supabase.table("classes").select("*").eq("teacher_username", st.session_state['current_teacher_username']).execute()
                teacher_classes = res_tch_cls.data or []
            except Exception:
                teacher_classes = []
                
            if not teacher_classes:
                st.warning("⚠️ Thầy/Cô chưa được phân công lớp học nào. Vui lòng liên hệ Admin tạo lớp!")
            else:
                class_map = {c['class_code']: c['class_name'] for c in teacher_classes}
                sel_report_class = st.selectbox(
                    "🏫 Chọn Lớp học để xem báo cáo:", 
                    options=list(class_map.keys()),
                    format_func=lambda x: f"{x} - {class_map.get(x, '')}"
                )
                
                col_ref1, col_ref2 = st.columns([3, 1])
                with col_ref2:
                    if st.button("🔄 Làm mới báo cáo", use_container_width=True):
                        get_class_study_logs.clear()
                        get_students_in_class.clear()
                        st.rerun()
                
                if sel_report_class:
                    students = get_students_in_class(sel_report_class)
                    logs = get_class_study_logs(sel_report_class)
                    
                    total_students = len(students)
                    total_submissions = len(logs)
                    total_stars = sum(l.get('stars_earned', 0) for l in logs)
                    
                    student_stats = {s['student_name']: {'stars': 0, 'submissions': 0, 'last_time': 'Chưa làm'} for s in students}
                    for l in logs:
                        name = l.get('student_name')
                        if name not in student_stats:
                            student_stats[name] = {'stars': 0, 'submissions': 0, 'last_time': 'Chưa làm'}
                        student_stats[name]['stars'] += l.get('stars_earned', 0)
                        student_stats[name]['submissions'] += 1
                        if student_stats[name]['last_time'] == 'Chưa làm' and l.get('completed_at'):
                            student_stats[name]['last_time'] = l.get('completed_at')[:16].replace('T', ' ')
                    
                    sorted_students = sorted(student_stats.items(), key=lambda item: (item[1]['stars'], item[1]['submissions']), reverse=True)
                    top_star_student = sorted_students[0][0] if sorted_students and sorted_students[0][1]['stars'] > 0 else "Chưa có"
                    
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("🎓 Học sinh", f"{total_students}")
                    with m2:
                        st.metric("📝 Lượt hoàn thành", f"{total_submissions}")
                    with m3:
                        st.metric("⭐ Tổng Sao đạt được", f"{total_stars}")
                    with m4:
                        st.metric("👑 Quán quân Top 1", f"{top_star_student}")
                        
                    st.markdown("---")
                    
                    st.markdown("### 🏆 BẢNG VÀNG VINH DANH (LEADERBOARD)")
                    
                    top_active = [s for s in sorted_students if s[1]['stars'] > 0]
                    if top_active:
                        pod_cols = st.columns(3)
                        podium_order = []
                        if len(top_active) >= 2:
                            podium_order.append((pod_cols[0], "🥈 HẠNG NHÌ", top_active[1], "#a0aec0"))
                        else:
                            podium_order.append((pod_cols[0], "", None, ""))
                            
                        podium_order.append((pod_cols[1], "🥇 QUÁN QUÂN", top_active[0], "#f6e05e"))
                        
                        if len(top_active) >= 3:
                            podium_order.append((pod_cols[2], "🥉 HẠNG BA", top_active[2], "#ed8936"))
                        else:
                            podium_order.append((pod_cols[2], "", None, ""))
                            
                        for col, rank_lbl, s_data, color in podium_order:
                            with col:
                                if s_data:
                                    s_name, s_val = s_data
                                    st.markdown(f"""
                                    <div style="background: white; border-radius: 16px; padding: 15px; text-align: center; border: 2px solid {color}; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                                        <div style="font-size: 16px; font-weight: 900; color: {color}; margin-bottom: 5px;">{rank_lbl}</div>
                                        <div style="font-size: 18px; font-weight: bold; color: #2d3436;">{s_name}</div>
                                        <div style="font-size: 22px; font-weight: 900; color: #e17055; margin: 6px 0;">⭐ {s_val['stars']}</div>
                                        <div style="font-size: 12px; color: #636e72;">{s_val['submissions']} bài đã làm</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    leaderboard_rows = []
                    for rank, (s_name, s_val) in enumerate(sorted_students, 1):
                        leaderboard_rows.append({
                            "Hạng": f"#{rank}",
                            "Tên Học Sinh": s_name,
                            "Tổng Sao ⭐": s_val['stars'],
                            "Số bài đã nộp": s_val['submissions'],
                            "Lần làm gần nhất": s_val['last_time']
                        })
                    
                    df_leaderboard = pd.DataFrame(leaderboard_rows)
                    st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    
                    st.markdown("### 📌 THEO DÕI NỘP BÀI TẬP VỀ NHÀ")
                    
                    try:
                        res_assign = supabase.table("assignments").select("*").execute()
                        all_assign = res_assign.data or []
                        class_assign = [a for a in all_assign if a.get('class_code') in ['ALL', sel_report_class, None]]
                    except Exception:
                        class_assign = []
                        
                    if not class_assign:
                        st.info("Chưa có bài tập về nhà nào được giao cho lớp này.")
                    else:
                        for assign in class_assign:
                            a_id = assign.get('id')
                            a_book = assign.get('book', 'Kid\'s Box')
                            a_units = ", ".join(assign.get('units', [])) if isinstance(assign.get('units'), list) else str(assign.get('units', ''))
                            a_dl = assign.get('deadline', '')[:16].replace('T', ' ')
                            
                            submitted_students = set()
                            for l in logs:
                                if l.get('assignment_id') == a_id:
                                    submitted_students.add(l.get('student_name'))
                            
                            sub_count = len(submitted_students)
                            pct = (sub_count / total_students) if total_students > 0 else 0
                            
                            with st.expander(f"📖 {a_book} ({a_units}) — Đã nộp: {sub_count}/{total_students} ({int(pct*100)}%) | Hạn: {a_dl}", expanded=True):
                                st.progress(pct)
                                c_sub, c_unsub = st.columns(2)
                                with c_sub:
                                    st.markdown("##### ✅ Đã nộp bài:")
                                    if submitted_students:
                                        for s in sorted(submitted_students):
                                            st.write(f"• **{s}**")
                                    else:
                                        st.caption("Chưa có học sinh nào nộp.")
                                with c_unsub:
                                    st.markdown("##### ⏳ Chưa nộp bài:")
                                    unsub = [s['student_name'] for s in students if s['student_name'] not in submitted_students]
                                    if unsub:
                                        for s in sorted(unsub):
                                            st.write(f"• {s}")
                                    else:
                                        st.success("Tất cả học sinh đã nộp bài! 🎉")
                                        
                    st.markdown("---")
                    
                    st.markdown("### 📝 NHẬT KÝ LÀM BÀI CHI TIẾT (GẦN ĐÂY)")
                    if not logs:
                        st.info("Chưa có nhật ký học tập nào được ghi nhận.")
                    else:
                        recent_rows = []
                        for l in logs[:30]:
                            recent_rows.append({
                                "Thời gian": l.get('completed_at', '')[:16].replace('T', ' '),
                                "Học Sinh": l.get('student_name'),
                                "Bài học / Nhiệm vụ": l.get('mission_title'),
                                "Kỹ năng": l.get('skill', 'All'),
                                "Số câu": l.get('total_questions', 20),
                                "Sao ⭐": l.get('stars_earned', 20)
                            })
                        st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)

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
                # Đây là dòng except bồ lỡ tay xóa làm báo lỗi nè
                except Exception as e:
                    st.error(f"❌ Invalid Excel file. Error: {e}")
                    
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
            st.markdown("#### 👧🏻 Manage Class Students")
            res_classes = supabase.table("classes").select("*").eq("teacher_username", st.session_state['current_teacher_username']).execute()
            db_classes = res_classes.data
            
            if not db_classes:
                st.warning("⚠️ No classes found. Please ask Admin to create a class first!")
            else:
                class_options = [f"{c['class_code']} - {c['class_name']}" for c in db_classes]
                selected_class_full = st.selectbox("Assign to Class:", class_options)
                selected_code = selected_class_full.split(" - ")[0]
                
                s_name = st.text_input("Student Name (e.g., Harry Potter):").strip()
                
                all_mascots_list = mascot_config.get_all_mascots()
                avatar_option = st.radio(
                    "Choose Avatar Style:",
                    ["🐾 Mascot Study Companion (Recommended)", "📷 Upload Custom Photo"],
                    horizontal=True
                )
                
                avatar_val = None
                if avatar_option.startswith("🐾"):
                    sel_mascot_id = st.selectbox(
                        "Select Companion Mascot:",
                        options=[m['id'] for m in all_mascots_list],
                        format_func=lambda x: f"{mascot_config.get_mascot(x)['badge']} {mascot_config.get_mascot(x)['name']} — {mascot_config.get_mascot(x)['personality']}"
                    )
                    avatar_val = f"mascot:{sel_mascot_id}"
                    m_preview = mascot_config.get_mascot(sel_mascot_id)
                    st.caption(f"💡 Mascot preview: **{m_preview['name']}** — *{m_preview['description']}*")
                else:
                    s_avatar = st.file_uploader("Upload Student Avatar (Optional)", type=["png", "jpg", "jpeg"])
                    if s_avatar:
                        st.info("✂️ Drag and resize the blue box to frame the face.")
                        img = Image.open(s_avatar)
                        cropped_img = st_cropper(img, aspect_ratio=(1, 1), box_color='#0984e3', return_type='image')
                        buffered = io.BytesIO()
                        cropped_img.save(buffered, format="PNG")
                        avatar_val = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    else:
                        avatar_val = f"mascot:{mascot_config.DEFAULT_MASCOT_ID}"
                
                if st.button("➕ ADD STUDENT", type="primary"):
                    if s_name:
                        try:
                            supabase.table("students").insert({
                                "class_code": selected_code, "student_name": s_name, "avatar": avatar_val
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
                                is_m, m_obj, avt_src = mascot_config.parse_student_avatar(student.get('avatar'))
                                companion_badge = f"{m_obj['badge']} {m_obj['name']}" if is_m and m_obj else "📷 Photo"
                                st.markdown(f"""
                                    <div style="text-align: center; background: rgba(255,255,255,0.85); padding: 15px; border-radius: 16px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.06); border: 2px solid transparent;">
                                        <img src="{avt_src}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #6c5ce7; padding: 2px; background: white;">
                                        <p style="font-weight: bold; margin-top: 10px; margin-bottom: 3px; color: #2d3436; font-size: 16px;">{student['student_name']}</p>
                                        <span style="font-size: 11px; color: #6c5ce7; font-weight: bold; background: #ede7f6; padding: 3px 8px; border-radius: 10px;">{companion_badge}</span>
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
            admin_user_cfg = st.secrets.get("ADMIN_USER")
            admin_pass_cfg = st.secrets.get("ADMIN_PASSWORD")
            if not admin_user_cfg or not admin_pass_cfg:
                st.error("⚠️ Admin account is not configured. Please set ADMIN_USER and ADMIN_PASSWORD in st.secrets.")
            elif hmac.compare_digest(u_admin.encode(), str(admin_user_cfg).encode()) and hmac.compare_digest(p_admin.encode(), str(admin_pass_cfg).encode()):
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
                            supabase.table("teachers").insert({"username": t_user, "password": hash_password(t_pass), "full_name": t_name}).execute()
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
