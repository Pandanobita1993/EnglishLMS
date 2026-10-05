# ==============================================================================
# TỆP CHỨA CÁC MODULE BÀI TẬP JAVASCRIPT (CHẠY ĐỘC LẬP)
# Giao diện 100% Tiếng Anh
# ==============================================================================
import streamlit as st
import streamlit.components.v1 as components
import random
import string
import json
import html

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
                const slotsEl = document.getElementById('slots');
                slotsEl.innerHTML = '';
                for (let i = 0; i < targetWord.length; i++) {{
                    let div = document.createElement('div');
                    div.className = 'slot' + (answer[i] ? ' filled' : '');
                    div.innerText = answer[i] ? answer[i].char : '';
                    div.onclick = () => {{ if(answer[i] && i === answer.length - 1) deleteLast(); }};
                    slotsEl.appendChild(div);
                }}
                
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
                const blankHtml = `<span class="blank ${{selectedOpt ? 'filled' : ''}}">${{displayWord}}</span>`;
                let htmlQ = /_{{2,}}/.test(qText) ? qText.replace(/_{{2,}}/, blankHtml) : (qText + ' ' + blankHtml);
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
    components.html(html_code, height=350)

@st.fragment
def run_ex3_dynamic(all_qs, idx):
    st.markdown("### 🔗 EXERCISE 3: MATCHING")
    ex3_qs = [q for q in all_qs if q['ex_type'] == 'Ex3']
    if not ex3_qs:
        st.error("⚠️ Not enough data to create a matching exercise.")
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
    components.html(html_code, height=450)

@st.fragment
def run_ex4_dynamic(all_qs, idx):
    st.markdown("### 🕵️‍♀️ EXERCISE 4: THE BIG BOSS WORD SEARCH")
    st.info("Swipe through the letters in the grid to find the hidden words. Drag and drop them into the correct pictures!")
    ex4_qs = [q for q in all_qs if q['ex_type'] == 'Ex4' and len(str(q['answer']).replace(" ", "")) <= 12]
    if not ex4_qs:
        st.error("⚠️ Not enough data to create a word search exercise.")
        return
    if len(ex4_qs) > 8: ex4_qs = random.sample(ex4_qs, 8)
    target_words = [q['answer'].upper().replace(" ", "") for q in ex4_qs]
    pic_mapping = {q['question']: q['answer'].upper().replace(" ", "") for q in ex4_qs}
    
    def generate_grid(words, size=12):
        grid = [['' for _ in range(size)] for _ in range(size)]
        for word in words:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction = random.choice([(0,1), (1,0)]) 
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
    js_grid = json.dumps(grid_data)
    js_targets = json.dumps(target_words)
    js_mapping = json.dumps(pic_mapping)
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
            if(filledCount < Object.keys(picMapping).length) msg.innerHTML = "<span style='color:#fdcb6e;'>⚠️ You haven't found all words yet!</span>";
            else if (!allCorrect) msg.innerHTML = "<span style='color:#ff7675;'>❌ Oops, some matches are incorrect. Try again!</span>";
            else msg.innerHTML = "<span style='color:#00b894;'>🎉 EXCELLENT! You found and matched everything perfectly! 🏆</span>";
        }}
    </script>
    </body>
    </html>
    """
    components.html(html_game_code, height=1050)
    
@st.fragment
def run_ex5_dynamic(all_qs, idx):
    st.markdown("### 🎴 EXERCISE 5: MEMORY FLIP CARDS")
    st.info("💡 **Mission:** Find and flip the matching pairs (English - Meaning).")
    
    ex5_qs = [q for q in all_qs if q['ex_type'] == 'Ex5']
    if not ex5_qs:
        st.error("⚠️ Not enough data to create a flip card exercise.")
        return
        
    if len(ex5_qs) > 6: ex5_qs = random.sample(ex5_qs, 6)
    
    cards = []
    for i, q in enumerate(ex5_qs):
        cards.append({'id': f"en_{i}", 'pair_id': i, 'text': q['question'], 'type': 'en'})
        cards.append({'id': f"vi_{i}", 'pair_id': i, 'text': q['answer'], 'type': 'vi'})
    
    random.shuffle(cards)
    js_cards = json.dumps(cards)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; user-select: none; background: transparent; margin: 0; padding: 10px; }}
        .grid-container {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; max-width: 600px; margin: 0 auto; perspective: 1000px; }}
        .card {{ width: 100%; aspect-ratio: 4/3; position: relative; transform-style: preserve-3d; transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1); cursor: pointer; }}
        .card.flipped {{ transform: rotateY(180deg); }}
        .card.matched {{ visibility: hidden; opacity: 0; transition: visibility 0s 0.5s, opacity 0.5s linear; }}
        .card-face {{ position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: bold; padding: 10px; box-sizing: border-box; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .card-front {{ background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; font-size: 24px; }}
        .card-front::after {{ content: '?'; }}
        .card-back {{ background: white; color: #2d3436; transform: rotateY(180deg); border: 2px solid #0984e3; }}
        .card-back.type-en {{ color: #d63031; border-color: #ff7675; }}
        .card-back.type-vi {{ color: #00b894; border-color: #55efc4; }}
        #msg {{ margin-top: 25px; font-size: 18px; font-weight: bold; height: 30px; }}
        @media (max-width: 480px) {{ .grid-container {{ grid-template-columns: repeat(3, 1fr); }} }}
    </style>
    </head>
    <body>
        <div class="grid-container" id="grid"></div>
        <div id="msg"></div>

        <script>
            const cardsData = {js_cards};
            const gridEl = document.getElementById('grid');
            let hasFlippedCard = false;
            let lockBoard = false;
            let firstCard, secondCard;
            let matchedPairs = 0;

            cardsData.forEach((card, index) => {{
                const cardEl = document.createElement('div');
                cardEl.classList.add('card');
                cardEl.dataset.pair = card.pair_id;
                
                const front = document.createElement('div');
                front.classList.add('card-face', 'card-front');
                
                const back = document.createElement('div');
                back.classList.add('card-face', 'card-back', 'type-' + card.type);
                back.innerText = card.text;
                
                cardEl.appendChild(front);
                cardEl.appendChild(back);
                cardEl.addEventListener('click', flipCard);
                gridEl.appendChild(cardEl);
            }});

            function flipCard() {{
                if (lockBoard) return;
                if (this === firstCard) return;

                this.classList.add('flipped');

                if (!hasFlippedCard) {{
                    hasFlippedCard = true;
                    firstCard = this;
                    return;
                }}

                secondCard = this;
                checkForMatch();
            }}

            function checkForMatch() {{
                let isMatch = firstCard.dataset.pair === secondCard.dataset.pair;
                isMatch ? disableCards() : unflipCards();
            }}

            function disableCards() {{
                lockBoard = true;
                setTimeout(() => {{
                    firstCard.classList.add('matched');
                    secondCard.classList.add('matched');
                    resetBoard();
                    matchedPairs++;
                    if (matchedPairs === cardsData.length / 2) {{
                        document.getElementById('msg').innerHTML = "<span style='color:#00b894;'>🎉 Excellent! You have a super memory!</span>";
                    }}
                }}, 800);
            }}

            function unflipCards() {{
                lockBoard = true;
                setTimeout(() => {{
                    firstCard.classList.remove('flipped');
                    secondCard.classList.remove('flipped');
                    resetBoard();
                }}, 1000);
            }}

            function resetBoard() {{
                [hasFlippedCard, lockBoard] = [false, false];
                [firstCard, secondCard] = [null, null];
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=500)
        
@st.fragment
def run_ex6_dynamic(q_data, idx):
    st.markdown("### 🚂 EXERCISE 6: SENTENCE TRAIN")
    
    # 1. Lấy dữ liệu gợi ý và hình ảnh
    hint_text = str(q_data.get('question', '')).strip()
    image_url = str(q_data.get('options', '')).strip()
    
    if hint_text and hint_text.lower() not in ['nan', 'none', '']:
        st.info(f"💡 **Hint:** {hint_text}")
        
    correct_sentence = str(q_data.get('answer', '')).strip()
    words = correct_sentence.split()
    
    # 2. Xáo trộn từ vựng
    shuffled_words = words.copy()
    while shuffled_words == words and len(set(words)) > 1:
        random.shuffle(shuffled_words)
        
    js_correct = json.dumps(correct_sentence)
    js_words = json.dumps(shuffled_words)
    
    # 3. Chèn khối hình ảnh nếu có link trong cột Options
    img_html = f'<div class="img-wrap"><img src="{html.escape(image_url, quote=True)}" class="hint-img"></div>' if image_url and image_url.lower() not in ['nan', 'none', ''] else ''
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; background: transparent; padding: 10px; margin: 0; user-select: none; }}
        .img-wrap {{ display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 15px; }}
        .hint-img {{ display: block; margin: 0 auto; max-width: 100%; max-height: 250px; width: auto; height: auto; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border: 3px solid #dfe6e9; object-fit: contain; background: white; }}
        
        /* Bọc nền trắng cho chữ hướng dẫn để luôn đọc được trên mọi phông nền */
        .instruction-text {{ 
            color: #2d3436 !important; 
            background: rgba(255, 255, 255, 0.9) !important; 
            padding: 8px 15px; 
            border-radius: 10px; 
            display: inline-block; 
            margin-bottom: 15px; 
            margin-top: 5px;
            border: 2px solid #dfe6e9;
            font-size: 16px;
            font-weight: bold;
        }}
        
        /* Ép khung nền luôn sáng sủa */
        .train-track {{ background: rgba(255, 255, 255, 0.85) !important; padding: 25px; border-radius: 15px; border: 3px dashed #74b9ff !important; min-height: 80px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-items: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        
        /* Ép các viên gạch từ vựng nền trắng, chữ xanh */
        .word-box {{ padding: 12px 20px; font-size: 18px; font-weight: bold; background: #ffffff !important; color: #0984e3 !important; border: 2px solid #74b9ff !important; border-radius: 8px; cursor: grab; box-shadow: 0 4px 0 #74b9ff !important; display: inline-block; transition: transform 0.1s; text-shadow: none !important; }}
        .word-box:active {{ cursor: grabbing; transform: translateY(4px); box-shadow: 0 0 0 #74b9ff !important; }}
        
        .sortable-ghost {{ opacity: 0.4; background-color: #dfe6e9 !important; border-color: #b2bec3 !important; box-shadow: none !important; }}
        .btn-check {{ margin-top: 15px; padding: 12px 35px; background: linear-gradient(90deg, #ff6b6b, #feca57) !important; color: white !important; border: none !important; border-radius: 25px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 15px rgba(255,107,107,0.4) !important; text-shadow: none !important; }}
        #msg {{ margin-top: 20px; font-size: 18px; font-weight: bold; text-shadow: 1px 1px 3px rgba(255,255,255,0.8); }}
    </style>
    </head>
    <body>
        {img_html}
        <div class="instruction-text">Drag and drop to rearrange the words into the correct sentence:</div>
        <div class="train-track" id="sortable-list"></div>
        <button class="btn-check" onclick="checkOrder()">🚀 SUBMIT SENTENCE</button>
        <div id="msg"></div>

        <script>
            const words = {js_words};
            const correctSentence = {js_correct};
            const listEl = document.getElementById('sortable-list');

            words.forEach(word => {{
                let box = document.createElement('div');
                box.className = 'word-box';
                box.innerText = word;
                listEl.appendChild(box);
            }});
            
            new Sortable(listEl, {{
                animation: 150,
                ghostClass: 'sortable-ghost'
            }});

            function checkOrder() {{
                const currentOrder = Array.from(listEl.children).map(el => el.innerText).join(' ');
                if (currentOrder === correctSentence) {{
                    document.getElementById('msg').innerHTML = "<span style='color:#00b894;'>✅ Awesome! You've matched the sentence correctly!</span>";
                    listEl.style.borderColor = '#00b894';
                    listEl.style.backgroundColor = '#e1fcf4';
                }} else {{
                    document.getElementById('msg').innerHTML = "<span style='color:#ff7675;'>❌ Not quite! Let's try rearranging them again!</span>";
                    listEl.style.borderColor = '#ff7675';
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    # Tự động nới rộng khung giao diện, bật scroll chống lấp nút
    frame_height = 750 if image_url and image_url.lower() not in ['nan', 'none', ''] else 450
    components.html(html_code, height=frame_height, scrolling=True)

@st.fragment
def run_ex7_dynamic(all_qs, idx):
    st.markdown("### 🔍 EXERCISE 7: ODD ONE OUT")
    st.info("💡 **Mission:** In each row, tap the word that is different, then press CHECK!")

    ex7_qs = [q for q in all_qs if q['ex_type'] == 'Ex7']

    # Mỗi câu cần có đáp án và tối thiểu 2 lựa chọn (cột Options, ngăn cách bằng dấu phẩy)
    items = []
    for q in ex7_qs:
        correct_ans = str(q.get('answer', '')).strip()
        raw_opts = str(q.get('options', '')).split(',')
        opts = [o.strip() for o in raw_opts if o.strip() and o.strip().lower() not in ['nan', 'none']]
        if correct_ans and correct_ans not in opts: opts.append(correct_ans)
        if not correct_ans or len(opts) < 2: continue
        random.shuffle(opts)
        prompt_text = str(q.get('question', '')).strip()
        if prompt_text.lower() in ['nan', 'none']: prompt_text = ''
        items.append({'prompt': prompt_text, 'answer': correct_ans, 'options': opts})

    if not items:
        st.error("⚠️ Not enough data to create an odd-one-out exercise.")
        return

    # Mỗi lượt hiện khoảng 6 câu (xáo ngẫu nhiên từ các câu đang có trong nhiệm vụ)
    if len(items) > 6: items = random.sample(items, 6)

    js_items = json.dumps(items)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Nunito', sans-serif; text-align: center; user-select: none; background: transparent; margin: 0; padding: 10px; }}
        .row {{ background: rgba(255,255,255,0.75); border: 3px solid #dfe6e9; border-radius: 15px; padding: 12px 10px 14px 10px; margin: 0 auto 14px auto; max-width: 620px; transition: border-color 0.2s, background 0.2s; }}
        .row.row-correct {{ border-color: #00b894; background: #e1fcf4; }}
        .row.row-wrong {{ border-color: #ff7675; }}
        .row-title {{ font-size: 15px; font-weight: 900; color: #6c5ce7; margin-bottom: 10px; }}
        .row-title .num {{ display: inline-block; background: #6c5ce7; color: white; border-radius: 50%; width: 24px; height: 24px; line-height: 24px; margin-right: 6px; }}
        .cards {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
        .card {{ flex: 1 1 110px; max-width: 150px; padding: 14px 8px; font-size: 19px; font-weight: 900; border-radius: 12px; border: 3px solid #74b9ff; background: white; color: #0984e3; cursor: pointer; box-shadow: 0 4px 0 #74b9ff; transition: all 0.15s; word-break: break-word; box-sizing: border-box; }}
        .card:active {{ transform: translateY(4px); box-shadow: 0 0 0 #74b9ff; }}
        .card.selected {{ background: #ffeaa7; border-color: #fdcb6e; color: #2d3436; box-shadow: 0 4px 0 #fdcb6e; transform: scale(1.04); }}
        .card.wrong {{ background: #ffeaea; border-color: #ff7675; color: #d63031; box-shadow: 0 4px 0 #ff7675; }}
        .card.correct {{ background: #55efc4; border-color: #00b894; color: white; box-shadow: 0 4px 0 #00b894; }}
        .card.locked {{ cursor: default; }}
        .btn-check {{ margin-top: 10px; padding: 12px 35px; background: linear-gradient(90deg, #ff6b6b, #feca57); color: white; border: none; border-radius: 25px; font-size: 18px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 15px rgba(255,107,107,0.4); }}
        #msg {{ margin: 15px 0 5px 0; font-size: 18px; font-weight: bold; min-height: 28px; }}
    </style>
    </head>
    <body>
        <div id="rows"></div>
        <button class="btn-check" id="btn" onclick="checkAll()">🚀 CHECK MY ANSWERS</button>
        <div id="msg"></div>

        <script>
            const items = {js_items};
            // state[i]: selected = từ đang chọn, done = đã đúng (khóa), wrongSet = các từ đã chọn sai
            const state = items.map(() => ({{ selected: null, done: false, wrongSet: [] }}));

            function setMsg(color, text) {{
                const m = document.getElementById('msg');
                m.innerText = text;
                m.style.color = color;
            }}

            function render() {{
                const container = document.getElementById('rows');
                container.innerHTML = '';
                items.forEach((it, i) => {{
                    const st = state[i];
                    const row = document.createElement('div');
                    row.className = 'row' + (st.done ? ' row-correct' : '');

                    const title = document.createElement('div');
                    title.className = 'row-title';
                    const num = document.createElement('span');
                    num.className = 'num';
                    num.innerText = i + 1;
                    title.appendChild(num);
                    title.appendChild(document.createTextNode(it.prompt || 'Which one is different?'));
                    row.appendChild(title);

                    const cards = document.createElement('div');
                    cards.className = 'cards';
                    it.options.forEach(opt => {{
                        const card = document.createElement('div');
                        let cls = 'card';
                        if (st.done) {{
                            cls += ' locked' + (opt === it.answer ? ' correct' : '');
                        }} else {{
                            if (st.selected === opt) cls += ' selected';
                            else if (st.wrongSet.includes(opt)) cls += ' wrong';
                        }}
                        card.className = cls;
                        card.innerText = opt;
                        card.onclick = () => {{
                            if (st.done) return;
                            st.selected = opt;
                            setMsg('', '');
                            render();
                        }};
                        cards.appendChild(card);
                    }});
                    row.appendChild(cards);
                    container.appendChild(row);
                }});
            }}

            function checkAll() {{
                const unanswered = state.filter(s => !s.done && !s.selected).length;
                if (unanswered > 0) {{
                    setMsg('#e17055', '⚠️ Please choose a word in every row first!');
                    return;
                }}
                state.forEach((s, i) => {{
                    if (s.done) return;
                    if (s.selected === items[i].answer) {{
                        s.done = true;
                    }} else {{
                        s.wrongSet.push(s.selected);
                    }}
                    s.selected = null;
                }});
                render();

                const correctCount = state.filter(s => s.done).length;
                if (correctCount === items.length) {{
                    document.getElementById('btn').style.display = 'none';
                    setMsg('#00b894', '🏆 Perfect! ' + correctCount + '/' + items.length + ' — You found every odd one out!');
                }} else {{
                    setMsg('#ff7675', '⭐ ' + correctCount + '/' + items.length + ' correct. Fix the rows without a green frame and try again!');
                }}
            }}
            render();
        </script>
    </body>
    </html>
    """
    # Chiều cao tự co giãn theo số câu (mỗi hàng ~ 120px)
    components.html(html_code, height=180 + 125 * len(items), scrolling=True)


@st.fragment
def run_ex8_dynamic(all_qs, idx):
    st.markdown("### 🗂️ EXERCISE 8: CATEGORY SORTING")
    st.info("💡 **Mission:** Tap a word from the Word Bank, then tap the box where it belongs!")

    ex8_qs = [q for q in all_qs if q.get('ex_type') == 'Ex8']
    if not ex8_qs:
        st.error("⚠️ Not enough data to create a Category Sorting exercise.")
        return

    cat_words = {}
    for q in ex8_qs:
        cat = str(q.get('question', '')).strip()
        if not cat or cat.lower() in ['nan', 'none']:
            cat = str(q.get('topic', '')).strip()
        if not cat or cat.lower() in ['nan', 'none']:
            cat = "General"

        words = []
        raw_opts = str(q.get('options', '')).strip()
        if raw_opts and raw_opts.lower() not in ['nan', 'none']:
            for w in raw_opts.split(','):
                w_clean = w.strip()
                if w_clean and w_clean.lower() not in ['nan', 'none']:
                    words.append(w_clean)

        ans = str(q.get('answer', '')).strip()
        if ans and ans.lower() not in ['nan', 'none'] and ans not in words:
            words.append(ans)

        if cat not in cat_words:
            cat_words[cat] = []
        for w in words:
            if w not in cat_words[cat]:
                cat_words[cat].append(w)

    cat_words = {c: ws for c, ws in cat_words.items() if len(ws) > 0}

    if len(cat_words) < 2:
        st.error("⚠️ Need at least 2 different categories with words to create a Category Sorting exercise.")
        return

    chosen_cats = list(cat_words.keys())
    if len(chosen_cats) > 3:
        chosen_cats = random.sample(chosen_cats, 3)

    items = []
    word_id = 0
    for cat in chosen_cats:
        words = cat_words[cat]
        sample_count = min(len(words), 4)
        picked = random.sample(words, sample_count)
        for w in picked:
            items.append({
                "id": word_id,
                "text": w,
                "cat": cat
            })
            word_id += 1

    random.shuffle(items)

    js_cats = json.dumps(chosen_cats)
    js_words = json.dumps(items)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Nunito', sans-serif;
            text-align: center;
            user-select: none;
            background: transparent;
            margin: 0;
            padding: 10px;
        }}
        .bank-wrapper {{
            background: rgba(255, 255, 255, 0.88);
            border: 3px dashed #74b9ff;
            border-radius: 16px;
            padding: 12px 15px;
            margin-bottom: 18px;
            min-height: 60px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        }}
        .bank-title {{
            font-size: 13px;
            font-weight: 900;
            color: #0984e3;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .bank-pool {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            align-items: center;
            min-height: 44px;
        }}
        .pill {{
            background: #ffffff;
            color: #0984e3;
            border: 2.5px solid #74b9ff;
            border-radius: 22px;
            padding: 8px 18px;
            font-size: 17px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 4px 0 #74b9ff;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .pill:active {{
            transform: translateY(3px);
            box-shadow: 0 1px 0 #74b9ff;
        }}
        .pill.selected {{
            background: #ffeaa7 !important;
            border-color: #fdcb6e !important;
            color: #2d3436 !important;
            box-shadow: 0 4px 0 #fdcb6e, 0 0 12px rgba(254, 202, 87, 0.6) !important;
            transform: scale(1.08) translateY(-2px);
        }}
        .pill.correct {{
            background: #55efc4 !important;
            border-color: #00b894 !important;
            color: #006248 !important;
            box-shadow: 0 4px 0 #00b894 !important;
            cursor: default;
        }}
        .pill.wrong {{
            background: #ff7675 !important;
            border-color: #d63031 !important;
            color: white !important;
            box-shadow: 0 4px 0 #d63031 !important;
            animation: shake 0.4s ease;
        }}
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-5px); }}
            75% {{ transform: translateX(5px); }}
        }}
        .buckets-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .bucket {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            border: 3px solid #dfe6e9;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.2s;
            box-shadow: 0 6px 15px rgba(0,0,0,0.05);
            min-height: 190px;
        }}
        .bucket.target-hover {{
            border-color: #feca57 !important;
            transform: scale(1.02);
            box-shadow: 0 8px 20px rgba(254, 202, 87, 0.4);
        }}
        .bucket-0 {{ border-color: #81ecec; }}
        .bucket-0 .bucket-header {{ background: linear-gradient(135deg, #00cec9, #81ecec); color: #005a58; }}
        .bucket-1 {{ border-color: #fab1a0; }}
        .bucket-1 .bucket-header {{ background: linear-gradient(135deg, #ff7675, #fab1a0); color: #6d1b1a; }}
        .bucket-2 {{ border-color: #a29bfe; }}
        .bucket-2 .bucket-header {{ background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: #2c216b; }}
        .bucket-header {{
            padding: 10px 12px;
            font-size: 17px;
            font-weight: 900;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            border-bottom: 2px solid rgba(0,0,0,0.06);
        }}
        .bucket-content {{
            padding: 12px;
            flex-grow: 1;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-content: flex-start;
            justify-content: center;
            min-height: 120px;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.5);
        }}
        .bucket-empty-hint {{
            color: #b2bec3;
            font-size: 14px;
            font-weight: 700;
            margin: auto;
            pointer-events: none;
            padding: 15px 5px;
            border: 2px dashed #dfe6e9;
            border-radius: 10px;
            width: 85%;
        }}
        .controls {{
            display: flex;
            gap: 15px;
            justify-content: center;
            align-items: center;
            margin-top: 5px;
        }}
        .btn-submit {{
            padding: 12px 35px;
            background: linear-gradient(90deg, #ff6b6b, #feca57);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 18px;
            font-weight: 900;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(255,107,107,0.4);
            transition: transform 0.1s;
        }}
        .btn-submit:active {{ transform: translateY(3px); }}
        .btn-reset {{
            padding: 12px 20px;
            background: #dfe6e9;
            color: #2d3436;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 3px 0 #b2bec3;
        }}
        .btn-reset:active {{ transform: translateY(3px); box-shadow: none; }}
        #msg {{
            margin-top: 15px;
            font-size: 18px;
            font-weight: 900;
            min-height: 32px;
        }}
    </style>
    </head>
    <body>
        <div class="bank-wrapper" id="bank-wrap">
            <div class="bank-title">📦 Word Bank</div>
            <div class="bank-pool" id="word-bank"></div>
        </div>

        <div class="buckets-grid" id="buckets-grid"></div>

        <div class="controls">
            <button class="btn-submit" id="btn-check" onclick="checkAnswers()">🚀 CHECK ANSWERS</button>
            <button class="btn-reset" onclick="resetAll()">↻ RESET</button>
        </div>
        <div id="msg"></div>

        <script>
            const categories = {js_cats};
            const initialWords = {js_words};
            
            let placements = {{}};
            let selectedWordId = null;
            let checked = false;
            let verifiedResults = {{}};

            function init() {{
                initialWords.forEach(w => {{
                    placements[w.id] = null;
                }});
                render();
            }}

            function setMsg(color, text) {{
                const m = document.getElementById('msg');
                m.innerText = text;
                m.style.color = color;
            }}

            function render() {{
                const bankEl = document.getElementById('word-bank');
                bankEl.innerHTML = '';
                const unplacedWords = initialWords.filter(w => placements[w.id] === null);

                if (unplacedWords.length === 0) {{
                    bankEl.innerHTML = '<span style="color:#00b894; font-weight:800; font-size:15px;">🎉 All words placed into boxes!</span>';
                }} else {{
                    unplacedWords.forEach(w => {{
                        const pill = createPillElement(w);
                        bankEl.appendChild(pill);
                    }});
                }}

                const gridEl = document.getElementById('buckets-grid');
                gridEl.innerHTML = '';

                categories.forEach((cat, idx) => {{
                    const bucket = document.createElement('div');
                    bucket.className = `bucket bucket-${{idx % 3}}`;
                    if (selectedWordId !== null) {{
                        bucket.classList.add('target-hover');
                    }}

                    const header = document.createElement('div');
                    header.className = 'bucket-header';
                    header.innerText = cat;
                    bucket.appendChild(header);

                    const content = document.createElement('div');
                    content.className = 'bucket-content';
                    content.onclick = () => onBucketClicked(cat);

                    content.ondragover = (e) => {{ e.preventDefault(); }};
                    content.ondrop = (e) => {{
                        e.preventDefault();
                        const wid = parseInt(e.dataTransfer.getData('text/plain'));
                        if (!isNaN(wid)) placeWord(wid, cat);
                    }};

                    const bucketWords = initialWords.filter(w => placements[w.id] === cat);
                    if (bucketWords.length === 0) {{
                        const hint = document.createElement('div');
                        hint.className = 'bucket-empty-hint';
                        hint.innerText = 'Tap here to put word';
                        content.appendChild(hint);
                    }} else {{
                        bucketWords.forEach(w => {{
                            const pill = createPillElement(w, true);
                            content.appendChild(pill);
                        }});
                    }}

                    bucket.appendChild(content);
                    gridEl.appendChild(bucket);
                }});
            }}

            function createPillElement(w, isInBucket = false) {{
                const pill = document.createElement('div');
                let cls = 'pill';
                if (selectedWordId === w.id) cls += ' selected';
                
                if (checked && isInBucket) {{
                    if (verifiedResults[w.id] === true) cls += ' correct';
                    else if (verifiedResults[w.id] === false) cls += ' wrong';
                }}

                pill.className = cls;
                pill.innerText = w.text;
                pill.draggable = !checked || verifiedResults[w.id] === false;

                pill.ondragstart = (e) => {{
                    e.dataTransfer.setData('text/plain', w.id);
                }};

                pill.onclick = (e) => {{
                    e.stopPropagation();
                    if (isInBucket) {{
                        if (!checked || verifiedResults[w.id] === false) {{
                            returnWordToBank(w.id);
                        }}
                    }} else {{
                        if (checked) {{
                            checked = false;
                            verifiedResults = {{}};
                            setMsg('', '');
                        }}
                        selectedWordId = (selectedWordId === w.id) ? null : w.id;
                        render();
                    }}
                }};

                return pill;
            }}

            function onBucketClicked(cat) {{
                if (selectedWordId !== null) {{
                    placeWord(selectedWordId, cat);
                }}
            }}

            function placeWord(wordId, targetCat) {{
                placements[wordId] = targetCat;
                selectedWordId = null;
                if (checked) {{
                    checked = false;
                    verifiedResults = {{}};
                    setMsg('', '');
                }}
                render();
            }}

            function returnWordToBank(wordId) {{
                placements[wordId] = null;
                if (selectedWordId === wordId) selectedWordId = null;
                if (checked) {{
                    delete verifiedResults[wordId];
                }}
                render();
            }}

            function resetAll() {{
                selectedWordId = null;
                checked = false;
                verifiedResults = {{}};
                setMsg('', '');
                init();
            }}

            function checkAnswers() {{
                const unplaced = initialWords.filter(w => placements[w.id] === null);
                if (unplaced.length > 0) {{
                    setMsg('#e17055', '⚠️ Please place all words into the category boxes first!');
                    return;
                }}

                checked = true;
                verifiedResults = {{}};
                let correctCount = 0;

                initialWords.forEach(w => {{
                    const isCorrect = (placements[w.id] === w.cat);
                    verifiedResults[w.id] = isCorrect;
                    if (isCorrect) correctCount++;
                }});

                render();

                if (correctCount === initialWords.length) {{
                    setMsg('#00b894', '🎉 HOORAY! You sorted all ' + correctCount + ' words correctly! 🏆');
                    document.getElementById('btn-check').style.display = 'none';
                }} else {{
                    setMsg('#ff7675', '⭐ ' + correctCount + '/' + initialWords.length + ' correct! Tap on the red words (❌) to return them to the Word Bank!');
                }}
            }}

            init();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=620, scrolling=True)
