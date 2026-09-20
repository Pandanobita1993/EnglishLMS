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
elif st.session_state['role'] == 'student':
    import random, string, json
    
# ---------------------------------------------------------------------
# KHAI BÁO CÁC HÀM BÀI TẬP - PHIÊN BẢN JAVASCRIPT SIÊU MƯỢT (NO LAG)
# ---------------------------------------------------------------------
@st.fragment
def run_ex1_dynamic(q_data, idx):
    st.markdown("### 🧩 EXERCISE 1: WORD PUZZLE")
    st.info(f"💡 **Hint:** {q_data['question']}")
    
    correct_word = str(q_data['answer']).upper().strip().replace(" ", "")
    chars = list(correct_word)
    random.shuffle(chars)
    
    js_word = json.dumps(correct_word)
    js_chars = json.dumps(chars)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; user-select: none; background: transparent; margin: 0; padding: 10px; }}
        .slots {{ display: flex; gap: 8px; justify-content: center; margin: 10px 0 20px 0; flex-wrap: wrap; min-height: 54px; }}
        .slot {{ width: 45px; height: 50px; border: 2px dashed #b2bec3; border-radius: 8px; background-color: rgba(255,255,255,0.5); display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 900; color: #2d3436; cursor: pointer; transition: all 0.2s; }}
        .slot.filled {{ border: 2px solid #0984e3; background-color: #e3f2fd; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .keyboard {{ display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; max-width: 400px; margin: 0 auto; }}
        .key-btn {{ width: 45px; height: 50px; background: linear-gradient(135deg, #ff7675, #d63031); color: white; border: none; border-radius: 8px; font-size: 22px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 0 #b2bec3; transition: all 0.1s; }}
        .key-btn:active {{ transform: translateY(4px); box-shadow: 0 0 0 #b2bec3; }}
        .key-btn:disabled {{ background: #dfe6e9; color: #b2bec3; box-shadow: none; cursor: not-allowed; transform: none; }}
        .controls {{ margin: 20px 0; display: flex; gap: 15px; justify-content: center; }}
        .ctrl-btn {{ padding: 10px 20px; font-size: 16px; font-weight: bold; border-radius: 20px; border: none; cursor: pointer; color: white; }}
        .btn-del {{ background: #feca57; }} .btn-reset {{ background: #a29bfe; }}
        #msg {{ margin-top: 15px; font-size: 18px; font-weight: bold; height: 30px; }}
    </style>
    </head>
    <body>
        <div class="slots" id="slots"></div>
        <div class="controls">
            <button class="ctrl-btn btn-del" onclick="deleteLast()">⌫ Delete</button>
            <button class="ctrl-btn btn-reset" onclick="resetAll()">↻ Reset</button>
        </div>
        <div class="keyboard" id="keyboard"></div>
        <div id="msg"></div>

        <script>
            const targetWord = {js_word};
            const initialChars = {js_chars};
            let answer = [];
            let keyStates = initialChars.map((c, i) => ({{ id: i, char: c, used: false }}));

            function render() {{
                // Render Slots
                const slotsEl = document.getElementById('slots');
                slotsEl.innerHTML = '';
                for (let i = 0; i < targetWord.length; i++) {{
                    let div = document.createElement('div');
                    div.className = 'slot' + (answer[i] ? ' filled' : '');
                    div.innerText = answer[i] ? answer[i].char : '';
                    div.onclick = () => {{ if(answer[i] && i === answer.length - 1) deleteLast(); }};
                    slotsEl.appendChild(div);
                }}
                
                // Render Keyboard
                const kbEl = document.getElementById('keyboard');
                kbEl.innerHTML = '';
                keyStates.forEach(k => {{
                    let btn = document.createElement('button');
                    btn.className = 'key-btn';
                    btn.innerText = k.char;
                    btn.disabled = k.used;
                    btn.onclick = () => {{
                        if (answer.length < targetWord.length) {{
                            k.used = true;
                            answer.push(k);
                            checkWin();
                            render();
                        }}
                    }};
                    kbEl.appendChild(btn);
                }});
            }}

            function deleteLast() {{
                if (answer.length > 0) {{
                    let last = answer.pop();
                    keyStates.find(k => k.id === last.id).used = false;
                    document.getElementById('msg').innerHTML = '';
                    render();
                }}
            }}

            function resetAll() {{
                answer = [];
                keyStates.forEach(k => k.used = false);
                document.getElementById('msg').innerHTML = '';
                render();
            }}

            function checkWin() {{
                if (answer.length === targetWord.length) {{
                    let currentStr = answer.map(a => a.char).join('');
                    if (currentStr === targetWord) {{
                        document.getElementById('msg').innerHTML = "<span style='color:#00b894;'>🎉 Awesome! You spelled it correctly!</span>";
                    }} else {{
                        document.getElementById('msg').innerHTML = "<span style='color:#d63031;'>❌ Not quite! Tap 'Delete' to try again!</span>";
                    }}
                }}
            }}
            render();
        </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_code, height=350)

@st.fragment
def run_ex2_dynamic(q_data, idx):
    st.markdown("### 📝 EXERCISE 2: FILL IN THE BLANK")
    base_q = str(q_data['question'])
    correct_ans = str(q_data['answer']).strip()
    raw_opts = str(q_data['options']).split(',')
    opts = [o.strip() for o in raw_opts if o.strip()]
    if correct_ans not in opts: opts.append(correct_ans)
    random.shuffle(opts)
    
    js_q = json.dumps(base_q)
    js_ans = json.dumps(correct_ans)
    js_opts = json.dumps(opts)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; background: transparent; padding: 10px; margin: 0; }}
        .question-box {{ font-size: 20px; background: rgba(255,255,255,0.7); padding: 25px; border-radius: 12px; margin-bottom: 25px; font-weight: bold; color: #2d3436; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .blank {{ display: inline-block; min-width: 80px; height: 30px; border-bottom: 3px dashed #b2bec3; margin: 0 10px; color: #0984e3; text-align: center; transition: all 0.2s; }}
        .blank.filled {{ border-bottom: 3px solid #0984e3; }}
        .opts {{ display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }}
        .opt-btn {{ padding: 12px 25px; font-size: 18px; font-weight: bold; border-radius: 30px; border: 2px solid #74b9ff; background: white; color: #0984e3; cursor: pointer; transition: all 0.1s; box-shadow: 0 4px 0 #74b9ff; }}
        .opt-btn:active {{ transform: translateY(4px); box-shadow: 0 0 0 #74b9ff; }}
        .opt-btn.selected {{ background: #0984e3; color: white; }}
        .btn-check {{ margin-top: 30px; padding: 12px 35px; background: linear-gradient(90deg, #ff6b6b, #feca57); color: white; border: none; border-radius: 25px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 15px rgba(255,107,107,0.4); }}
        #msg {{ margin-top: 15px; font-size: 18px; font-weight: bold; }}
    </style>
    </head>
    <body>
        <div class="question-box" id="q-box"></div>
        <div class="opts" id="opts-container"></div>
        <button class="btn-check" onclick="checkAnswer()">🚀 SUBMIT ANSWER</button>
        <div id="msg"></div>

        <script>
            const qText = {js_q};
            const correctAns = {js_ans};
            const options = {js_opts};
            let selectedOpt = null;

            function render() {{
                let displayWord = selectedOpt ? selectedOpt : "";
                let htmlQ = qText.replace('___________', `<span class="blank ${{selectedOpt ? 'filled' : ''}}">${{displayWord}}</span>`);
                document.getElementById('q-box').innerHTML = htmlQ;
                
                const optsEl = document.getElementById('opts-container');
                optsEl.innerHTML = '';
                options.forEach(opt => {{
                    let btn = document.createElement('button');
                    btn.className = 'opt-btn' + (selectedOpt === opt ? ' selected' : '');
                    btn.innerText = opt;
                    btn.onclick = () => {{ selectedOpt = opt; render(); document.getElementById('msg').innerHTML=''; }};
                    optsEl.appendChild(btn);
                }});
            }}

            function checkAnswer() {{
                if (!selectedOpt) {{
                    document.getElementById('msg').innerHTML = "<span style='color:#fdcb6e;'>⚠️ Please select a word first!</span>";
                    return;
                }}
                if (selectedOpt === correctAns) {{
                    document.getElementById('msg').innerHTML = "<span style='color:#00b894;'>✅ Perfect! That's correct!</span>";
                    document.querySelectorAll('.opt-btn').forEach(b => b.onclick = null);
                }} else {{
                    document.getElementById('msg').innerHTML = "<span style='color:#ff7675;'>❌ Oops, try again!</span>";
                }}
            }}
            render();
        </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_code, height=350)

@st.fragment
def run_ex3_dynamic(all_qs, idx):
    st.markdown("### 🔗 EXERCISE 3: MATCHING")
    ex3_qs = [q for q in all_qs if q['ex_type'] == 'Ex3']
    if not ex3_qs:
        st.error("Không đủ dữ liệu tạo bài nối.")
        return
        
    lefts = [q['question'] for q in ex3_qs]
    rights = [q['answer'] for q in ex3_qs]
    random.shuffle(lefts)
    random.shuffle(rights)
    
    js_pairs = json.dumps({q['question']: q['answer'] for q in ex3_qs})
    js_lefts = json.dumps(lefts)
    js_rights = json.dumps(rights)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; user-select: none; margin: 0; padding: 10px; }}
        .match-container {{ display: flex; justify-content: space-around; max-width: 600px; margin: 0 auto; }}
        .col {{ display: flex; flex-direction: column; gap: 15px; width: 45%; }}
        .m-btn {{ padding: 15px; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.2s; border: 3px solid transparent; }}
        .btn-a {{ background: #fab1a0; color: #d63031; box-shadow: 0 4px 0 #ff7675; }}
        .btn-b {{ background: #81ecec; color: #0984e3; box-shadow: 0 4px 0 #00cec9; }}
        .m-btn:active {{ transform: translateY(4px); box-shadow: 0 0 0 transparent; }}
        .m-btn.selected {{ border-color: #ffeaa7; box-shadow: 0 0 15px #ffeaa7; transform: scale(1.05); }}
        .m-btn.done {{ background: #55efc4; color: white; border-color: #00b894; box-shadow: none; cursor: default; transform: none; opacity: 0.8; }}
        #msg {{ margin-top: 25px; font-size: 18px; font-weight: bold; height: 30px; }}
    </style>
    </head>
    <body>
        <div class="match-container">
            <div class="col" id="col-a"></div>
            <div class="col" id="col-b"></div>
        </div>
        <div id="msg"></div>

        <script>
            const pairs = {js_pairs};
            const arrA = {js_lefts};
            const arrB = {js_rights};
            let selA = null; let selB = null;
            let doneA = []; let doneB = [];

            function render() {{
                const colA = document.getElementById('col-a');
                colA.innerHTML = '<h4 style="color: #d63031; margin-bottom: 5px;">COLUMN A</h4>';
                arrA.forEach(val => {{
                    let btn = document.createElement('div');
                    btn.className = 'm-btn btn-a' + (doneA.includes(val) ? ' done' : '') + (selA === val ? ' selected' : '');
                    btn.innerText = val;
                    btn.onclick = () => {{
                        if (!doneA.includes(val)) {{ selA = (selA === val ? null : val); checkMatch(); render(); }}
                    }};
                    colA.appendChild(btn);
                }});

                const colB = document.getElementById('col-b');
                colB.innerHTML = '<h4 style="color: #0984e3; margin-bottom: 5px;">COLUMN B</h4>';
                arrB.forEach(val => {{
                    let btn = document.createElement('div');
                    btn.className = 'm-btn btn-b' + (doneB.includes(val) ? ' done' : '') + (selB === val ? ' selected' : '');
                    btn.innerText = val;
                    btn.onclick = () => {{
                        if (!doneB.includes(val)) {{ selB = (selB === val ? null : val); checkMatch(); render(); }}
                    }};
                    colB.appendChild(btn);
                }});
            }}

            function checkMatch() {{
                if (selA && selB) {{
                    if (pairs[selA] === selB) {{
                        doneA.push(selA); doneB.push(selB);
                        document.getElementById('msg').innerHTML = "<span style='color:#00b894;'>🎉 Correct Match!</span>";
                    }} else {{
                        document.getElementById('msg').innerHTML = "<span style='color:#ff7675;'>❌ Incorrect Match! Try again.</span>";
                    }}
                    selA = null; selB = null;
                    
                    if (doneA.length === arrA.length) {{
                        document.getElementById('msg').innerHTML = "<span style='color:#00b894;'>🏆 Awesome! You matched everything!</span>";
                    }}
                }} else {{
                    document.getElementById('msg').innerHTML = "";
                }}
            }}
            render();
        </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_code, height=450)

    # ---------------------------------------------------------------------
    # GIAO DIỆN ĐĂNG NHẬP & LUỒNG HỌC TẬP CHÍNH
    # ---------------------------------------------------------------------
    st.markdown("<h3 style='text-align: center; color: #0984e3;'>🎒 Student Login</h3>", unsafe_allow_html=True)
    
    class_code_input = st.text_input("🔑 Enter your Class Code:").strip().upper()
    
    if class_code_input:
        # Lấy thông tin lớp từ Database
        class_res = supabase.table("classes").select("*").eq("class_code", class_code_input).execute()
        
        if not class_res.data:
            st.error("❌ Class Code not found!")
        else:
            class_name = class_res.data[0]['class_name']
            st.success(f"🏫 Found class: **{class_name}**")
            
            # Kéo toàn bộ học sinh của lớp đó từ Database về
            students_res = supabase.table("students").select("*").eq("class_code", class_code_input).execute()
            students_in_class = students_res.data
            
            if len(students_in_class) == 0:
                st.warning("No students added to this class yet!")
            else:
                student_options = ["👇 Click here..."] + [s['student_name'] for s in students_in_class]
                selected_name = st.selectbox("Who are you?", options=student_options)
                
                # BƯỚC 3: KIỂM TRA ĐĂNG NHẬP THÀNH CÔNG -> MỚI MỞ GIAO DIỆN HỌC TẬP
                if selected_name != "👇 Click here...":
                    st.markdown("---")
                    
                    # Lấy thông tin học sinh (để lấy avatar)
                    student_info = next(item for item in students_in_class if item["student_name"] == selected_name)
                    avatar_src = f"data:image/jpeg;base64,{student_info['avatar']}" if student_info['avatar'] else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    
                    # Dùng Flexbox gộp chung Avatar và Bong bóng chat
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                            <img src="{avatar_src}" style="width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 4px solid #0984e3; box-shadow: 0 4px 10px rgba(0,0,0,0.15); flex-shrink: 0;">
                            <div style="background-color: rgba(0, 184, 148, 0.15); border-left: 6px solid #00b894; padding: 18px 20px; border-radius: 12px; flex-grow: 1; color: #2d3436; font-size: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                                🎉 Hello <strong style="color: #00b894; font-size: 20px;">{selected_name}</strong>! Let's complete today's missions!
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                 
                    # Biến toàn cục lưu trạng thái bài học
                    if 'playlist' not in st.session_state:
                        st.session_state['playlist'] = []
                        st.session_state['current_q'] = 0
                        st.session_state['all_questions'] = []

                    st.markdown("---")

                    # =========================================================
                    # CƠ CHẾ GIẤU MENU (CHỈ HIỆN 1 TRONG 2 TRẠNG THÁI)
                    # =========================================================
                    if len(st.session_state['playlist']) == 0:
                        
                        # --- TRẠNG THÁI 1: CHƯA BẤM START -> HIỆN MENU CHỌN ---
                        st.markdown("### 🎯 CHOOSE YOUR MISSION")

                        col_b, col_u, col_t = st.columns(3)
                        with col_b:
                            sel_book = st.selectbox("📚 Book:", ["Kid's Box 1", "Kid's Box 2", "Kid's Box 3"])
                        with col_u:
                            sel_unit = st.selectbox("📖 Unit:", ["Unit 1", "Unit 2", "Unit 3", "Unit 4"])
                        with col_t:
                            sel_topic = st.selectbox("🌟 Topic:", ["Animals", "Colors", "Greetings", "Family"])

                        if st.button("🚀 START MISSION", type="primary", use_container_width=True):
                            with st.spinner("Đang xào bài và chuẩn bị thử thách..."):
                                try:
                                    # Kéo dữ liệu từ Supabase
                                    res = supabase.table("questions").select("*") \
                                            .eq("book", sel_book).eq("unit", sel_unit).eq("topic", sel_topic).execute()
                                    all_qs = res.data
                                    
                                    if not all_qs:
                                        st.warning("📭 Ôi! Chưa có bài tập nào trong kho cho phần này. Bé chọn chủ đề khác nhé!")
                                    else:
                                        st.session_state['all_questions'] = all_qs
                                        quick_qs = [q for q in all_qs if q['ex_type'] in ['Ex1', 'Ex2']]
                                        boss_qs = [q for q in all_qs if q['ex_type'] == 'Ex4']
                                        has_ex3 = any(q['ex_type'] == 'Ex3' for q in all_qs)
                                        
                                        num_quick = min(8, len(quick_qs))
                                        selected_playlist = random.sample(quick_qs, num_quick)
                                        if has_ex3: selected_playlist.append({'ex_type': 'Ex3'}) 
                                        random.shuffle(selected_playlist)
                                        if boss_qs: selected_playlist.append({'ex_type': 'Ex4'})
                                        
                                        st.session_state['playlist'] = selected_playlist
                                        st.session_state['current_q'] = 0
                                        st.rerun() # Load lại trang để chuyển sang trạng thái 2
                                except Exception as e:
                                    st.error(f"⚠️ Lỗi kết nối lấy đề bài: {e}")

                    else:
                        
                        # --- TRẠNG THÁI 2: ĐÃ BẤM START -> GIẤU MENU, HIỆN BÀI TẬP ---
                        total_q = len(st.session_state['playlist'])
                        curr_idx = st.session_state['current_q']
                        current_q_data = st.session_state['playlist'][curr_idx]
                        
                        st.progress((curr_idx + 1) / total_q)
                        st.caption(f"🚩 Tiến độ: Thử thách số {curr_idx + 1} / {total_q}")
                        
                        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
                        with col_nav2:
                            btn_label = "FINISH MISSION 🌟" if curr_idx == total_q - 1 else "NEXT MISSION ➔"
                            if st.button(btn_label, use_container_width=True, type="secondary"):
                                if curr_idx < total_q - 1:
                                    st.session_state['current_q'] += 1
                                    st.rerun()
                                else:
                                    st.balloons()
                                    st.success("🎉 XUẤT SẮC! BÉ ĐÃ ĐÁNH BẠI TOÀN BỘ THỬ THÁCH HÔM NAY!")
                                    st.session_state['playlist'] = [] # Xóa playlist để quay lại Trạng thái 1
                                    st.rerun()
                                    
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Gọi giao diện bài tập tương ứng
                        ex_type = current_q_data.get('ex_type', '')
                        if ex_type == 'Ex1': run_ex1_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex2': run_ex2_dynamic(current_q_data, curr_idx)
                        elif ex_type == 'Ex3': run_ex3_dynamic(st.session_state['all_questions'], curr_idx)
                        elif ex_type == 'Ex4': run_ex4_dynamic(st.session_state['all_questions'], curr_idx)
                        else: st.error("⚠️ Hệ thống không nhận diện được loại bài tập này.")
                
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
