import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO

# --- [1. 기본 설정] ---
st.set_page_config(page_title="숨은 글자 찾기 생성기", page_icon="👀", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- [2. 문제 세트 데이터] ---
PROBLEM_SETS = {
    "나 vs 너 (한글)": ("나", "너", "숫자 '너'"), # (오답, 정답, 타겟이름)
    "3 vs 8 (숫자)": ("3", "8", "숫자 '8'"),
    "5 vs 2 (숫자)": ("5", "2", "숫자 '2'"),
    "6 vs 9 (숫자)": ("6", "9", "숫자 '9'"),
    "F vs E (알파벳)": ("F", "E", "알파벳 'E'"),
    "O vs Q (알파벳)": ("O", "Q", "알파벳 'Q'"),
    "R vs P (알파벳)": ("R", "P", "알파벳 'P'"),
    "大 vs 太 (한자)": ("大", "太", "한자 '클 태(太)'"),
    "왕 vs 욍 (한글)": ("왕", "욍", "글자 '욍'"),
    "숲 vs 슾 (한글)": ("숲", "슾", "글자 '슾'"),
}

# --- [3. 기능 함수들] ---
def get_font(size):
    if os.path.exists(FONT_FILE): return ImageFont.truetype(FONT_FILE, size)
    else: return ImageFont.load_default()

def create_puzzle_image(params):
    # 캔버스 생성
    W, H = 1080, 1080 # 인스타/쇼츠 썸네일용 1:1 비율 (필요시 변경 가능)
    if params['ratio'] == "9:16 (쇼츠)": W, H = 1080, 1920
        
    img = Image.new('RGB', (W, H), params['bg_color'])
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드
    font_header = get_font(params['header_fs'])
    font_grid = get_font(params['grid_fs'])
    
    # --- 1. 헤더(상단바) 그리기 ---
    header_h = params['header_h']
    draw.rectangle([(0, 0), (W, header_h)], fill=params['header_bg'])
    
    # 헤더 텍스트
    # anchor="mm" : 텍스트의 정중앙을 기준으로 좌표를 잡음
    # X좌표: 화면 중앙 (W/2)
    # Y좌표: 헤더 높이의 절반 + 사용자 미세조정 값
    text_x = W / 2
    text_y = (header_h / 2) + params['header_y_adj']
    
    draw.text((text_x, text_y), params['header_text'], font=font_header, fill=params['header_color'], anchor="mm")

    # --- 2. 그리드(글자들) 그리기 ---
    rows = params['rows']
    cols = params['cols']
    
    # 그리드 영역 계산
    grid_start_y = header_h + 50
    grid_w = W - 100 # 좌우 여백 50씩
    grid_h = H - grid_start_y - 50
    
    cell_w = grid_w / cols
    cell_h = grid_h / rows
    
    # 정답 위치 랜덤 선정
    target_row = random.randint(0, rows-1)
    target_col = random.randint(0, cols-1)
    
    wrong_char = params['wrong_char']
    target_char = params['target_char']
    
    for r in range(rows):
        for c in range(cols):
            # 현재 위치의 글자 결정
            char = target_char if (r == target_row and c == target_col) else wrong_char
            
            # 좌표 계산 (각 셀의 중앙)
            cx = 50 + (c * cell_w) + (cell_w / 2)
            cy = grid_start_y + (r * cell_h) + (cell_h / 2)
            
            # 글자 그리기
            # 정답 이미지가 아닐 경우(문제용)에는 그냥 그림
            # 정답용 이미지일 경우, 정답에만 동그라미나 색상 표시 (여기선 간단히 색상 변경)
            
            text_color = params['grid_color']
            if params['is_answer_mode'] and (r == target_row and c == target_col):
                text_color = "#FF0000" # 정답은 빨간색
                # 동그라미 그리기
                left = cx - (params['grid_fs']/1.5)
                top = cy - (params['grid_fs']/1.5)
                right = cx + (params['grid_fs']/1.5)
                bottom = cy + (params['grid_fs']/1.5)
                draw.ellipse([(left, top), (right, bottom)], outline="#FF0000", width=10)

            draw.text((cx, cy), char, font=font_grid, fill=text_color, anchor="mm")
            
    return img

# --- [4. 메인 UI] ---
st.title("👀 숨은 글자 찾기 생성기 (정밀조절판)")

col_L, col_R = st.columns([1, 1.5])

with col_L:
    st.header("1. 문제 설정")
    
    # 문제 프리셋 선택
    pset_name = st.selectbox("추천 문제 세트", list(PROBLEM_SETS.keys()))
    wrong, target, t_name = PROBLEM_SETS[pset_name]
    
    # 커스텀 가능하도록
    c1, c2 = st.columns(2)
    with c1: wrong_char = st.text_input("오답 글자 (배경)", value=wrong)
    with c2: target_char = st.text_input("정답 글자 (타겟)", value=target)
    
    # 헤더 문구 자동 생성
    default_header = f"3초 안에 {t_name} 찾기"
    header_text = st.text_input("상단 문구 내용", value=default_header)

    st.write("---")
    st.header("2. 디자인 & 배치 설정")
    
    with st.expander("🎨 색상 설정", expanded=False):
        c_bg, c_grid = st.columns(2)
        bg_color = c_bg.color_picker("전체 배경색", "#FFFFFF")
        grid_color = c_grid.color_picker("글자 색상", "#000000")
        
        c_hbg, c_htxt = st.columns(2)
        header_bg = c_hbg.color_picker("상단바 배경", "#334488")
        header_color = c_htxt.color_picker("상단바 글자", "#FFD700")

    with st.expander("📏 상단바(헤더) 정밀 조절", expanded=True):
        st.info("여기서 제목의 크기와 위치를 조절하세요!")
        
        header_h = st.slider("상단바 높이 (배경)", 100, 600, 300)
        
        # [요청하신 기능] 글자 크기 & 위치
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            header_fs = st.slider("제목 글자 크기", 30, 200, 90)
        with col_h2:
            header_y_adj = st.slider("제목 위치 (위/아래)", -150, 150, 0, help="양수면 아래로, 음수면 위로 움직입니다.")

    with st.expander("▦ 그리드(글자판) 설정", expanded=False):
        col_g1, col_g2 = st.columns(2)
        with col_g1: rows = st.slider("세로 줄 수", 5, 20, 10)
        with col_g2: cols = st.slider("가로 줄 수", 5, 20, 10)
        
        grid_fs = st.slider("글자판 글자 크기", 20, 150, 80)

    ratio = st.radio("이미지 비율", ["1:1 (피드/썸네일)", "9:16 (쇼츠)"], horizontal=True)

    # 파라미터 딕셔너리 생성
    params = {
        'wrong_char': wrong_char, 'target_char': target_char,
        'header_text': header_text, 'header_h': header_h, 
        'header_fs': header_fs, 'header_y_adj': header_y_adj, # [NEW]
        'header_bg': header_bg, 'header_color': header_color,
        'rows': rows, 'cols': cols, 'grid_fs': grid_fs, 'grid_color': grid_color,
        'bg_color': bg_color, 'ratio': ratio,
        'is_answer_mode': False
    }

with col_R:
    st.header("3. 결과물 확인")
    
    tab1, tab2 = st.tabs(["❓ 문제용 이미지", "⭕ 정답용 이미지"])
    
    # 문제 이미지 생성
    with tab1:
        img_q = create_puzzle_image(params)
        st.image(img_q, caption="문제 이미지", use_container_width=True)
        
        buf_q = BytesIO()
        img_q.save(buf_q, format="JPEG", quality=95)
        st.download_button("💾 문제 이미지 다운로드", buf_q.getvalue(), "puzzle_question.jpg", "image/jpeg")

    # 정답 이미지 생성
    with tab2:
        params_ans = params.copy()
        params_ans['is_answer_mode'] = True
        
        img_a = create_puzzle_image(params_ans)
        st.image(img_a, caption="정답 이미지", use_container_width=True)
        
        buf_a = BytesIO()
        img_a.save(buf_a, format="JPEG", quality=95)
        st.download_button("💾 정답 이미지 다운로드", buf_a.getvalue(), "puzzle_answer.jpg", "image/jpeg")