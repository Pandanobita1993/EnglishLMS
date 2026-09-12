# ==============================================================================
# ỨNG DỤNG HỌC TẬP CAMBRIDGE KIDS (ALL-IN-ONE)
# Yêu cầu cài đặt: pip install streamlit streamlit-sortables pandas streamlit-option-menu streamlit-lottie requests openpyxl
# ==============================================================================

import streamlit as st
from streamlit_sortables import sort_items
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
import pandas as pd
import datetime
import base64
import os
import random
import io
import requests

# ================= 1. SYSTEM & UI CONFIGURATION =================
st.set_page_config(page_title="Smart English Class", page_icon="🏫", layout="centered")

# LÁ BÙA 1: Lưu Lottie vào bộ nhớ đệm
@st.cache_data 
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# LÁ BÙA 2: Lưu ảnh nền vào bộ nhớ đệm
@st.cache_data 
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load sẵn Animation
lottie_hello = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_M9p23l.json") # Chó vẫy đuôi
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_a2chheio.json") # Pháo hoa/Cúp

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_kids_background(image_path):
    try:
        bin_str = get_base64_of_bin_file(image_path)
        bg_css = f'background-image: url("data:image/jpeg;base64,{bin_str}");'
    except FileNotFoundError:
        bg_css = 'background-color: #f5f6fa;' # Màu nền mặc định nếu thiếu ảnh

    st.markdown(f"""
        <style>
        /* Import Font chữ tròn trịa */
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Nunito', sans-serif;
        }}
        
        /* Hiệu ứng kính mờ (Glassmorphism) */
        [data-testid="stAppViewBlockContainer"] {{
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border-radius: 24px;
            padding: 40px 50px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.6);
            margin-top: 10px;
            margin-bottom: 30px;
        }}

        h1, h2, h3, h4, h5 {{ 
            color: transparent !important;
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
            -webkit-background-clip: text;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
            font-weight: 900 !important;
        }}

        .stSelectbox label, .stMultiSelect label, .stFileUploader label, .stTextInput label {{
            font-size: 16px; font-weight: 700; color: #34495e;
        }}

        /* Hiệu ứng Hover cho nút bấm */
        .stButton > button {{
            border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            font-weight: bold !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }}
        </style>
    """, unsafe_allow_html=True)

set_kids_background("image_e56c83.jpg")

st.markdown("<h1 style='text-align: center;'>🌟 CAMBRIDGE KIDS LMS 🌟</h1>", unsafe_allow_html=True)

# ================= 2. SESSION STATE MANAGEMENT =================
if 'role' not in st.session_state:
    st.session_state['role'] = None  
if 'is_teacher_logged_in' not in st.session_state:
    st.session_state['is_teacher_logged_in'] = False

# --- HỆ THỐNG DATABASE LỚP & HỌC SINH ---
if 'db_classes' not in st.session_state:
    # Key là Mã lớp, Value là Tên lớp
    st.session_state['db_classes'] = {"KID01": "Kid's Box 1A", "KID02": "Kid's Box 1B"}
    
if 'db_students' not in st.session_state:
    # Key là Mã lớp, Value là Danh sách Học sinh (Có chứa Avatar base64)
    st.session_state['db_students'] = {
        "KID01": [
            {"name": "Minh Xu", "avatar": None}, # None sẽ tự lấy avatar mặc định
            {"name": "Ngoc Nu", "avatar": None}
        ],
        "KID02": []
    }
# ================= 3. THANH ĐIỀU HƯỚNG SIÊU TỐC (NATIVE FAST MENU) =================
# Bọc menu trong một form để giữ layout đẹp (bằng css tự nhận ở trên)
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

# Xác định nút nào đang được chọn để tô màu đậm (primary), nút còn lại mờ (secondary)
btn_home = "primary" if st.session_state['role'] is None else "secondary"
btn_student = "primary" if st.session_state['role'] == 'student' else "secondary"
btn_teacher = "primary" if st.session_state['role'] == 'teacher' else "secondary"

with c1:
    if st.button("🏠 Home", type=btn_home, use_container_width=True):
        st.session_state['role'] = None
        st.rerun()
with c2:
    if st.button("🎒 Student Portal", type=btn_student, use_container_width=True):
        st.session_state['role'] = 'student'
        st.rerun()
with c3:
    if st.button("👨‍🏫 Teacher Portal", type=btn_teacher, use_container_width=True):
        st.session_state['role'] = 'teacher'
        st.rerun()
st.markdown("---")

# ================= 4. TRANG CHỦ (HOME) =================
if st.session_state['role'] is None:
    st.markdown("<h3 style='text-align: center; color: #0984e3 !important;'>Welcome to the Interactive Learning Platform!</h3>", unsafe_allow_html=True)
    if lottie_hello:
        st_lottie(lottie_hello, height=300, key="home_dog")
    st.info("👆 Please select your portal from the menu above to continue.")

# ================= 5. GÓC HỌC VIÊN (STUDENT PORTAL) =================
elif st.session_state['role'] == 'student':
    st.markdown("<h3 style='text-align: center; color: #0984e3;'>🎒 Student Login</h3>", unsafe_allow_html=True)
    
    # BƯỚC 1: HỌC SINH NHẬP MÃ LỚP
    class_code_input = st.text_input("🔑 Enter your Class Code (e.g., KID01):", placeholder="Ask your teacher for the code...").strip().upper()
    
    if class_code_input:
        if class_code_input not in st.session_state['db_classes']:
            st.error("❌ Class Code not found! Please check again.")
        else:
            class_name = st.session_state['db_classes'][class_code_input]
            st.success(f"🏫 Found class: **{class_name}**")
            
            # BƯỚC 2: CHỌN TÊN TRONG DANH SÁCH LỚP
            students_in_class = st.session_state['db_students'][class_code_input]
            
            if len(students_in_class) == 0:
                st.warning("No students added to this class yet!")
            else:
                student_options = ["👇 Click here to select your name..."] + [s['name'] for s in students_in_class]
                selected_name = st.selectbox("Who are you? 🕵️‍♂️", options=student_options)

                # BƯỚC 3: VÀO GIAO DIỆN HỌC TẬP
                if selected_name != "👇 Click here to select your name...":
                    st.markdown("---")
                    
                    # Lấy thông tin học sinh (để lấy avatar)
                    student_info = next(item for item in students_in_class if item["name"] == selected_name)
                    avatar_src = f"data:image/jpeg;base64,{student_info['avatar']}" if student_info['avatar'] else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        # Hiển thị ảnh Avatar tròn xoe tuyệt đẹp bằng CSS
                        st.markdown(f"""
                            <img src="{avatar_src}" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #0984e3; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        """, unsafe_allow_html=True)
                    with c2:
                        st.success(f"🎉 Hello **{selected_name}**! Let's complete today's missions!")
                 
        st.markdown("---")
        
        # ACTIVE SESSION BANNER
        if 'active_session' in st.session_state:
            session = st.session_state['active_session']
            st.error("🚨 **NEW ASSIGNMENT FROM TEACHER!**")
            st.info(f"📚 **Book:** {session['book']} | 🏷️ **Units:** {', '.join(session['units'])} | 🎯 **Skill:** {session['skill']}")
            st.write(f"⏳ **Deadline:** {session['deadline'].strftime('%d/%m/%Y %H:%M')}")
        else:
            st.success("✨ No mandatory assignments today. Let's practice freely!")
        
        # ---------------------------------------------------------
        # EXERCISE 1: SPELLING (DRAG & DROP)
        # ---------------------------------------------------------
        st.markdown("### 🧩 EXERCISE 1: WORD PUZZLE")
        st.info("Drag the letters into the correct order to spell an animal! 🐶")

        correct_word = "ELEPHANT"
        if 'ex1_letters' not in st.session_state:
            letters = []
            counts = {}
            for char in correct_word:
                counts[char] = counts.get(char, 0) + 1
                letters.append(char + "\u200b" * counts[char])
            random.shuffle(letters)
            st.session_state['ex1_letters'] = letters

        sorted_letters = sort_items(
            st.session_state['ex1_letters'], 
            direction="horizontal", 
            key="word_puzzle_unique"
        )

        if st.button("✨ CHECK PUZZLE", use_container_width=True):
            student_word = "".join([item[0] for item in sorted_letters])
            if student_word == correct_word:
                st.balloons()
                st.success(f"🎉 Excellent! '{student_word}' is absolutely correct!")
                if lottie_success: st_lottie(lottie_success, height=150, key="succ_1")
            else:
                st.error(f"❌ Not quite! You spelled '{student_word}'. Try again!")

        st.markdown("---")

        # ---------------------------------------------------------
        # EXERCISE 2: FILL IN THE BLANK (TAP TO FILL)
        # ---------------------------------------------------------
        st.markdown("### 📝 EXERCISE 2: FILL IN THE BLANK")
        st.info("Tap the correct word below to fill in the blank! 🐶")
        
        base_question = "She went ___________ to buy a new dress yesterday."
        correct_answer_ex2 = "shopping"
        options_ex2 = ["shopping", "supermarket", "BigC"]

        if 'ex2_selected' not in st.session_state:
            st.session_state['ex2_selected'] = None
            st.session_state['ex2_mistakes'] = 0
            st.session_state['ex2_done'] = False
            opts = options_ex2.copy()
            random.shuffle(opts)
            st.session_state['ex2_options'] = opts

        current_word = st.session_state['ex2_selected'] if st.session_state['ex2_selected'] else "..."
        blank_color = "#0984e3" if st.session_state['ex2_selected'] else "#b2bec3"
        
        display_question = base_question.replace(
            '___________', 
            f'<span style="color: {blank_color}; border: 2px dashed {blank_color}; background: #fff; padding: 2px 12px; border-radius: 8px; font-weight: bold;">{current_word}</span>'
        )

        st.markdown(f"""
            <div style="font-size: 18px; color: #2d3436; background: rgba(255,255,255,0.7); padding: 18px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                {display_question}
            </div>
        """, unsafe_allow_html=True)

        if not st.session_state['ex2_done']:
            cols = st.columns(len(options_ex2))
            for i, opt in enumerate(st.session_state['ex2_options']):
                with cols[i]:
                    is_chosen = (st.session_state['ex2_selected'] == opt)
                    btn_label = f"✨ [{opt}]" if is_chosen else f"📦 {opt}"
                    if st.button(btn_label, use_container_width=True, key=f"ex2_btn_{i}"):
                        st.session_state['ex2_selected'] = opt
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 SUBMIT ANSWER", use_container_width=True, type="primary"):
                if not st.session_state['ex2_selected']:
                    st.warning("⚠️ Please select a word first!")
                else:
                    if st.session_state['ex2_selected'] == correct_answer_ex2:
                        st.balloons()
                        st.session_state['ex2_done'] = True
                        mistakes = st.session_state['ex2_mistakes']
                        if mistakes == 0:
                            st.success(f"🎉 Perfect {student_name}! You got it right on the first try!")
                        else:
                            st.success(f"👏 Good job! You found the answer after {mistakes} incorrect attempts.")
                        st.rerun()
                    else:
                        st.session_state['ex2_mistakes'] += 1
                        st.error(f"❌ Oops, '{st.session_state['ex2_selected']}' is incorrect. (Mistakes: {st.session_state['ex2_mistakes']})")
        else:
            st.success(f"✅ Completed! Correct answer: **{correct_answer_ex2}** (Mistakes made: {st.session_state['ex2_mistakes']})")

        st.markdown("---")

        # ---------------------------------------------------------
        # EXERCISE 3: MATCHING (TAP TO CONNECT)
        # ---------------------------------------------------------
        st.markdown("### 🔗 EXERCISE 3: MATCHING")
        st.info("Tap an item in COLUMN A, then tap its match in COLUMN B. 🐶")

        matching_pairs = {
            "How are you?": "I'm fine, thanks.",
            "What's your name?": "My name is Nu.",
            "How old are you?": "I'm 8 years old."
        }

        if 'ex3_lefts' not in st.session_state:
            lefts = list(matching_pairs.keys())
            rights = list(matching_pairs.values())
            random.shuffle(lefts)
            random.shuffle(rights)
            st.session_state['ex3_lefts'] = lefts
            st.session_state['ex3_rights'] = rights
            st.session_state['ex3_sel_left'] = None
            st.session_state['ex3_sel_right'] = None
            st.session_state['ex3_completed'] = []
            st.session_state['ex3_mistakes'] = 0

        if st.session_state['ex3_sel_left'] and st.session_state['ex3_sel_right']:
            l_val = st.session_state['ex3_sel_left']
            r_val = st.session_state['ex3_sel_right']
            
            if matching_pairs[l_val] == r_val:
                st.session_state['ex3_completed'].append(l_val)
                st.toast("🎉 Correct Match!", icon="✅")
            else:
                st.session_state['ex3_mistakes'] += 1
                st.toast(f"❌ Incorrect! (Mistakes: {st.session_state['ex3_mistakes']})", icon="🚨")
            
            st.session_state['ex3_sel_left'] = None
            st.session_state['ex3_sel_right'] = None
            st.rerun()

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("<h5 style='text-align: center; color: #d63031;'>🔹 COLUMN A</h5>", unsafe_allow_html=True)
            for item in st.session_state['ex3_lefts']:
                is_done = item in st.session_state['ex3_completed']
                is_sel = item == st.session_state['ex3_sel_left']
                
                if is_done:
                    st.button(f"✅ {item}", key=f"L_{item}", disabled=True, use_container_width=True)
                elif is_sel:
                    if st.button(f"🟡 {item}", key=f"L_{item}", type="primary", use_container_width=True):
                        st.session_state['ex3_sel_left'] = None 
                        st.rerun()
                else:
                    if st.button(f"🟦 {item}", key=f"L_{item}", use_container_width=True):
                        st.session_state['ex3_sel_left'] = item
                        st.rerun()

        with col_b:
            st.markdown("<h5 style='text-align: center; color: #0984e3;'>🔸 COLUMN B</h5>", unsafe_allow_html=True)
            for item in st.session_state['ex3_rights']:
                parent_key = [k for k, v in matching_pairs.items() if v == item][0]
                is_done = parent_key in st.session_state['ex3_completed']
                is_sel = item == st.session_state['ex3_sel_right']

                if is_done:
                    st.button(f"✅ {item}", key=f"R_{item}", disabled=True, use_container_width=True)
                elif is_sel:
                    if st.button(f"🟡 {item}", key=f"R_{item}", type="primary", use_container_width=True):
                        st.session_state['ex3_sel_right'] = None
                        st.rerun()
                else:
                    if st.button(f"🟧 {item}", key=f"R_{item}", use_container_width=True):
                        st.session_state['ex3_sel_right'] = item
                        st.rerun()

        if len(st.session_state['ex3_completed']) == len(matching_pairs):
            st.balloons()
            if st.session_state['ex3_mistakes'] == 0:
                st.success("🎉 Awesome! You matched everything perfectly with 0 mistakes!")
                if lottie_success: st_lottie(lottie_success, height=200, key="succ_3")
            else:
                st.success(f"👏 Good effort! You finished the exercise with {st.session_state['ex3_mistakes']} incorrect attempts.")

        # ---------------------------------------------------------
        # EXERCISE 4: WORD SEARCH & DRAG (MINI GAME NÚT CHẠM)
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🕵️‍♀️ EXERCISE 4: WORD SEARCH & MATCH")
        st.info("Swipe through the letters in the grid to find the hidden words. When found, drag and drop the word into the correct picture! 🐶")

        html_game_code = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: 'Nunito', sans-serif; text-align: center; user-select: none; background: transparent;}
            
            /* Lưới chữ 10x10 */
            .grid { display: grid; grid-template-columns: repeat(10, 35px); gap: 4px; justify-content: center; margin: 15px auto; touch-action: none;}
            .cell { width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; background: #fff; border: 2px solid #dfe6e9; border-radius: 8px; font-weight: bold; font-size: 18px; color: #2d3436; cursor: crosshair; transition: transform 0.1s; }
            
            /* Trạng thái bôi đen và Đã tìm thấy */
            .cell.selecting { background: #ffeaa7; transform: scale(1.1); box-shadow: 0 0 10px #fdcb6e; border-color: #fdcb6e;}
            .cell.found { background: #55efc4; color: white; text-decoration: line-through; border-color: #00b894; opacity: 0.8;}
            
            /* Khu vực chứa từ rơi ra */
            .bank { min-height: 50px; padding: 15px; border: 2px dashed #b2bec3; border-radius: 15px; display: flex; gap: 10px; justify-content: center; align-items: center; background: rgba(255,255,255,0.7); margin: 15px 0; }
            .pill { padding: 8px 20px; background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white; border-radius: 20px; font-weight: bold; font-size: 16px; cursor: grab; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .pill:active { cursor: grabbing; transform: scale(0.95); }
            
            /* Khu vực hình ảnh thả vào */
            .pictures { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
            .pic-box { width: 90px; background: white; border-radius: 15px; padding: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: center; border: 3px solid transparent; transition: all 0.3s;}
            .pic { font-size: 45px; margin-bottom: 5px; }
            
            /* Ô đón từ được thả */
            .drop-zone { width: 100%; height: 35px; background: #f1f2f6; border: 2px dashed #ced6e0; border-radius: 8px; display: flex; align-items: center; justify-content: center; transition: all 0.2s;}
            .drop-zone.drag-over { background: #dfe6e9; border-color: #0984e3; transform: scale(1.05);}
            
            /* Nút chấm điểm */
            .btn-check { margin-top: 20px; padding: 12px 30px; background: linear-gradient(90deg, #ff6b6b, #feca57); color: white; border: none; border-radius: 25px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4); transition: transform 0.2s; }
            .btn-check:hover { transform: scale(1.05); }
            #message { margin-top: 15px; font-weight: bold; font-size: 18px; }
        </style>
        </head>
        <body>

        <!-- BẢNG LƯỚI CHỮ -->
        <div class="grid" id="grid"></div>
        
        <h4 style="color:#6c5ce7; margin-bottom: 5px;">Drag the found words into the pictures:</h4>
        <!-- KHO CHỨA TỪ BAY RA -->
        <div class="bank" id="bank"></div>
        
        <!-- CÁC ẢNH MỤC TIÊU -->
        <div class="pictures" id="pictures"></div>
        
        <button class="btn-check" onclick="checkAnswers()">🚀 CHECK ANSWERS</button>
        <div id="message"></div>

        <script>
            // 1. DỮ LIỆU ĐẦU VÀO
            const gridData = [
                ['A','P','P','L','E','X','Z','Q','M','E'],
                ['T','X','X','X','X','X','X','X','X','W'],
                ['G','X','B','A','N','A','N','A','X','P'],
                ['R','X','X','X','X','X','X','X','X','L'],
                ['A','O','R','A','N','G','E','X','X','M'],
                ['P','X','X','X','X','X','X','X','X','C'],
                ['E','X','M','E','L','O','N','X','X','V'],
                ['D','X','X','X','X','X','X','X','X','S'],
                ['F','X','X','X','X','X','X','X','X','D'],
                ['J','X','X','X','X','X','X','X','X','F']
            ];
            
            const targetWords = ["APPLE", "BANANA", "ORANGE", "GRAPE", "MELON"];
            const picMapping = { "🍎": "APPLE", "🍌": "BANANA", "🍊": "ORANGE", "🍇": "GRAPE", "🍈": "MELON" };
            let foundWords = [];

            // 2. VẼ BẢNG 10x10
            const gridEl = document.getElementById('grid');
            gridData.forEach((row, r) => {
                row.forEach((letter, c) => {
                    let cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.innerText = letter;
                    gridEl.appendChild(cell);
                });
            });

            // 3. THUẬT TOÁN QUÉT CHUỘT
            let isSelecting = false;
            let currentSelection = [];
            let selectedCells = [];

            function startSelect(target) {
                if(target.classList.contains('cell') && !target.classList.contains('found')) {
                    isSelecting = true;
                    target.classList.add('selecting');
                    currentSelection.push(target.innerText);
                    selectedCells.push(target);
                }
            }

            function moveSelect(target) {
                if(isSelecting && target.classList.contains('cell') && !target.classList.contains('found')) {
                    if(!selectedCells.includes(target)){ 
                        target.classList.add('selecting');
                        currentSelection.push(target.innerText);
                        selectedCells.push(target);
                    }
                }
            }

            function endSelect() {
                if(isSelecting) {
                    isSelecting = false;
                    let wordStr = currentSelection.join('');
                    let wordStrRev = currentSelection.slice().reverse().join(''); 
                    
                    let matchedWord = null;
                    if(targetWords.includes(wordStr) && !foundWords.includes(wordStr)) matchedWord = wordStr;
                    else if (targetWords.includes(wordStrRev) && !foundWords.includes(wordStrRev)) matchedWord = wordStrRev;

                    if (matchedWord) {
                        selectedCells.forEach(c => {
                            c.classList.remove('selecting');
                            c.classList.add('found');
                        });
                        foundWords.push(matchedWord);
                        createPill(matchedWord); 
                    } else {
                        selectedCells.forEach(c => c.classList.remove('selecting'));
                    }
                    
                    currentSelection = [];
                    selectedCells = [];
                }
            }

            gridEl.addEventListener('mousedown', (e) => startSelect(e.target));
            gridEl.addEventListener('mouseover', (e) => moveSelect(e.target));
            window.addEventListener('mouseup', endSelect);
            
            gridEl.addEventListener('touchstart', (e) => {
                let touch = e.touches[0];
                let target = document.elementFromPoint(touch.clientX, touch.clientY);
                if(target) startSelect(target);
                e.preventDefault(); 
            }, {passive: false});

            gridEl.addEventListener('touchmove', (e) => {
                let touch = e.touches[0];
                let target = document.elementFromPoint(touch.clientX, touch.clientY);
                if(target) moveSelect(target);
                e.preventDefault();
            }, {passive: false});

            window.addEventListener('touchend', endSelect);

            // 4. VẼ HÌNH ẢNH VÀ Ô DROP ZONE
            const picsEl = document.getElementById('pictures');
            Object.keys(picMapping).forEach(emoji => {
                let box = document.createElement('div');
                box.className = 'pic-box';
                
                let pic = document.createElement('div');
                pic.className = 'pic';
                pic.innerText = emoji;
                
                let dropZone = document.createElement('div');
                dropZone.className = 'drop-zone';
                dropZone.dataset.target = picMapping[emoji]; 
                
                dropZone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    dropZone.classList.add('drag-over');
                });
                dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
                dropZone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    dropZone.classList.remove('drag-over');
                    let pillId = e.dataTransfer.getData('text');
                    let pill = document.getElementById(pillId);
                    if (pill) {
                        dropZone.innerHTML = ''; 
                        dropZone.appendChild(pill);
                        dropZone.style.border = 'none';
                        dropZone.style.background = 'transparent';
                    }
                });

                box.appendChild(pic);
                box.appendChild(dropZone);
                picsEl.appendChild(box);
            });

            const bankEl = document.getElementById('bank');
            bankEl.addEventListener('dragover', (e) => e.preventDefault());
            bankEl.addEventListener('drop', (e) => {
                e.preventDefault();
                let pillId = e.dataTransfer.getData('text');
                let pill = document.getElementById(pillId);
                if(pill) bankEl.appendChild(pill);
            });

            function createPill(word) {
                let pill = document.createElement('div');
                pill.className = 'pill';
                pill.innerText = word;
                pill.id = 'pill_' + word;
                pill.draggable = true;
                pill.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text', e.target.id);
                });
                bankEl.appendChild(pill);
            }

            // 5. KIỂM TRA ĐÁP ÁN
            function checkAnswers() {
                let dropZones = document.querySelectorAll('.drop-zone');
                let allCorrect = true;
                let filledCount = 0;

                dropZones.forEach(zone => {
                    let pill = zone.querySelector('.pill');
                    if(pill) {
                        filledCount++;
                        let word = pill.innerText;
                        let target = zone.dataset.target;
                        if(word !== target) {
                            allCorrect = false;
                            zone.parentElement.style.borderColor = "#ff7675"; 
                        } else {
                            zone.parentElement.style.borderColor = "#55efc4"; 
                        }
                    } else {
                        allCorrect = false;
                    }
                });

                let msg = document.getElementById('message');
                if(filledCount < 5) {
                    msg.innerHTML = "<span style='color:#fdcb6e;'>⚠️ Nu says: You haven't found and dropped all 5 words yet!</span>";
                } else if (!allCorrect) {
                    msg.innerHTML = "<span style='color:#ff7675;'>❌ Oops, some matches are incorrect. Check the red borders and try again!</span>";
                } else {
                    msg.innerHTML = "<span style='color:#00b894;'>🎉 EXCELLENT! You found and matched everything perfectly! 🏆</span>";
                }
            }
        </script>
        </body>
        </html>
        """
        
        components.html(html_game_code, height=950)


# ================= 6. GÓC GIÁO VIÊN (TEACHER PORTAL) =================
elif st.session_state['role'] == 'teacher':
    if not st.session_state['is_teacher_logged_in']:
        st.markdown("### 🔑 Admin Login")
        user_input = st.text_input("Username:")
        pass_input = st.text_input("Password:", type="password")
        
        if st.button("🔓 Login", type="primary"):
            if user_input == "admin" and pass_input == "123456":
                st.session_state['is_teacher_logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")
    else:
        c_title, c_btn = st.columns([4, 1])
        with c_title:
            st.success("✨ Welcome back to the Teacher Dashboard!")
        with c_btn:
            if st.button("🔒 Logout"):
                st.session_state['is_teacher_logged_in'] = False
                st.rerun()
            
        st.markdown("---")
        
        # TEACHER DASHBOARD TABS
        tab_assign, tab_bank, tab_class = st.tabs(["🛠️ Assign Homework", "🏦 Question Bank", "👥 Class & Students"])
        
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
            sub_manual, sub_import = st.tabs(["✍️ Manual Entry", "📁 Excel Import"])
            
            with sub_manual:
                st.markdown("#### Create Question Manually")
                with st.form("manual_entry_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.selectbox("Book", ["Kid's Box 1", "Kid's Box 2"])
                        st.selectbox("Unit", ["Unit 1", "Unit 2"])
                    with c2:
                        st.selectbox("Task Type", ["Fill in the blank", "Word Puzzle", "Matching"])
                        st.selectbox("Skill", ["Vocabulary", "Grammar"])
                    
                    q_text = st.text_input("Question (Use ___ for blanks):")
                    q_ans = st.text_input("Correct Answer:")
                    q_dist = st.text_input("Distractors (comma separated):", placeholder="e.g. supermarket, BigC")
                    
                    if st.form_submit_button("💾 SAVE TO DATABASE", type="primary", use_container_width=True):
                        if q_text and q_ans:
                            st.success(f"✅ Successfully saved: '{q_text}'")
                        else:
                            st.error("⚠️ Please provide both Question and Answer.")
                            
            with sub_import:
                st.markdown("#### Bulk Import via Excel")
                
                # Tạo file Excel mẫu cho giáo viên tải về
                df_template = pd.DataFrame({
                    "Book": ["Kid's Box 1"],
                    "Unit": ["Unit 1"],
                    "Skill": ["Vocabulary"],
                    "Task_Type": ["Fill_in_the_blank"],
                    "Question": ["She went ___ to buy a dress."],
                    "Correct_Answer": ["shopping"],
                    "Distractors": ["supermarket, BigC"]
                })
                
                towrite = io.BytesIO()
                df_template.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                
                st.download_button(
                    label="⬇️ DOWNLOAD EXCEL TEMPLATE",
                    data=towrite,
                    file_name="QuestionBank_Template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.markdown("---")
                uploaded_file = st.file_uploader("Upload filled Excel file here", type=["xlsx", "xls"])
                
                if uploaded_file is not None:
                    try:
                        df_import = pd.read_excel(uploaded_file)
                        st.write(f"🔍 **Found {len(df_import)} questions in file:**")
                        st.dataframe(df_import, use_container_width=True)
                        
                        if st.button("🚀 CONFIRM IMPORT", type="primary"):
                            st.balloons()
                            st.success(f"✅ Successfully imported {len(df_import)} questions into the Database!")
                    except Exception as e:
                        st.error(f"❌ Error reading file: {e}")

        # --------- TAB 3: CLASS & STUDENT MANAGEMENT ---------
        with tab_class:
            st.markdown("#### 🏫 Class & Student Manager")
            
            sub_class, sub_student = st.tabs(["📚 Manage Classes", "👧🏻 Manage Students"])
            
            with sub_class:
                st.markdown("**Add a New Class**")
                with st.form("add_class_form", clear_on_submit=True):
                    c_code = st.text_input("Class Code (e.g., ENG101):")
                    c_name = st.text_input("Class Name (e.g., Movers 1):")
                    if st.form_submit_button("➕ ADD CLASS", type="primary"):
                        if c_code and c_name:
                            st.session_state['db_classes'][c_code.upper()] = c_name
                            st.session_state['db_students'][c_code.upper()] = []
                            st.success(f"✅ Class {c_name} ({c_code.upper()}) added successfully!")
                        else:
                            st.error("⚠️ Please enter both Code and Name.")
                
                # Bảng hiển thị danh sách lớp
                st.markdown("**Current Classes**")
                class_df = pd.DataFrame([{"Class Code": k, "Class Name": v, "Total Students": len(st.session_state['db_students'][k])} for k, v in st.session_state['db_classes'].items()])
                st.dataframe(class_df, use_container_width=True, hide_index=True)

            with sub_student:
                st.markdown("**Add Student to Class**")
                if not st.session_state['db_classes']:
                    st.warning("Please add a class first!")
                else:
                    with st.form("add_student_form", clear_on_submit=True):
                        # Chọn mã lớp (Kèm tên cho dễ nhớ)
                        class_options = [f"{code} - {name}" for code, name in st.session_state['db_classes'].items()]
                        selected_class_full = st.selectbox("Assign to Class:", class_options)
                        selected_code = selected_class_full.split(" - ")[0]
                        
                        s_name = st.text_input("Student Name (e.g., Harry Potter):")
                        
                        # Upload hình ảnh
                        s_avatar = st.file_uploader("Upload Student Avatar (Optional)", type=["png", "jpg", "jpeg"])
                        
                        if st.form_submit_button("➕ ADD STUDENT", type="primary"):
                            if s_name:
                                # Chuyển ảnh thành base64 để lưu thẳng vào Session/DB
                                avatar_b64 = None
                                if s_avatar is not None:
                                    avatar_b64 = base64.b64encode(s_avatar.read()).decode('utf-8')
                                
                                st.session_state['db_students'][selected_code].append({
                                    "name": s_name,
                                    "avatar": avatar_b64
                                })
                                st.success(f"✅ Added {s_name} to class {selected_code}!")
                            else:
                                st.error("⚠️ Please enter the student's name.")
                                
                # Chọn lớp để xem danh sách học sinh
                st.markdown("---")
                view_class = st.selectbox("View Students in Class:", options=list(st.session_state['db_classes'].keys()))
                if view_class:
                    students_list = st.session_state['db_students'][view_class]
                    if students_list:
                        # Hiển thị thẻ học sinh siêu đẹp
                        st.write(f"**Total: {len(students_list)} students**")
                        cols = st.columns(4) # Hiển thị 4 bé trên 1 hàng
                        for i, student in enumerate(students_list):
                            with cols[i % 4]:
                                avt_src = f"data:image/jpeg;base64,{student['avatar']}" if student['avatar'] else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                                st.markdown(f"""
                                    <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 15px; margin-bottom: 10px;">
                                        <img src="{avt_src}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #6c5ce7;">
                                        <p style="font-weight: bold; margin-top: 10px; margin-bottom: 0; color: #2d3436;">{student['name']}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No students in this class yet.")
