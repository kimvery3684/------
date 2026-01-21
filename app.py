import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random
from io import BytesIO

# --- [1. 기본 설정] ---
st.set_page_config(page_title="글자 크기/간격 정밀 조절기 (v10.0)", page_icon="🎚️", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"
SAVE_DIR = "saved_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- [2. 문제 데이터 (예시)] ---
PROBLEM_SETS = {
    "숫자 6 vs 0": ("60", "06", "숫자 '06'"),
    "한글 나 vs 너": ("나", "너", "글자 '너'"),
    "알파벳 O vs Q": ("O", "Q", "알파벳 'Q'"),
    "한자 大 vs 太": ("大", "太", "한자 '太'"),
}

# --- [3. 기능 함수들] ---
def get_font(size):
    if os.path.exists(FONT_FILE): return ImageFont.truetype(FONT_FILE, size)
    else: return ImageFont.load_default()

def create_puzzle_image(params):
    # 캔버스 생성 (기본 1080 x 1350, 혹은 조절 가능)
    W, H = 1080, 1350 
    img = Image.new('RGB', (W, H), "#FFFFFF") # 전체 배경 흰색 고정 (필요시 변경)
    draw = ImageDraw.Draw(img)
    
    # 1. 헤더 배경 그리기
    draw.rectangle([(0, 0), (W, params['header_h'])], fill=params['header_bg'])
    
    # 2. 제목 1 (큰 글씨) 그리기
    font_t1 = get_font(params['t1_size'])
    # anchor="mt" (Middle Top) -> X는 중앙, Y는 지정한 값
    draw.text((W/2, params['t1_y']), params['t1_text'], font=font_t1, fill=params['t1_color'], anchor="mt")
    
    # 3. 제목 2 (작은 글씨) 그리기
    # {target} 치환 기능
    final_t2_text = params['t2_text'].replace("{target}", params['target_name'])
    
    font_t2 = get_font(params['t2_size'])
    draw.text((W/2, params['t2_y']), final_t2_text, font=font_t2, fill=params['t2_color'], anchor="mt")
    
    # 4. 중앙 숫자판(그리드) 그리기
    font_grid = get_font(params['grid_size'])
    
    rows = params['rows']
    cols = params['cols']
    
    # 정답 위치 랜덤 선정
    target_r = random.randint(0, rows-1)
    target_c = random.randint(0, cols-1)
    
    for r in range(rows):
        for c in range(cols):
            # 현재 글자 결정 (정답 or 오답)
            is_target = (r == target_r and c == target_c)
            char = params['target_char'] if is_target else params['wrong_char']
            
            # [핵심] 정밀 좌표 계산
            # X = 시작점X + (칸번호 * 가로간격)
            # Y = 시작점Y + (줄번호 * 세로간격)
            x = params['start_x'] + (c * params['x_spacing'])
            y = params['start_y'] + (r * params['y_spacing'])
            
            # 정답 모드일 때 정답 강조
            color = params['grid_color']
            if params['is_answer_mode'] and is_target:
                color = "#FF0000" # 빨강
                # 동그라미 (옵션)
                # bounds = [x-40, y-40, x+40, y+40]
                # draw.ellipse(bounds, outline="red", width=5)

            # anchor="lt" (Left Top) 기준이면 좌표 잡기가 편함. 
            # 하지만 중앙 정렬을 위해 보통 anchor="mm" 등을 씀. 
            # 여기서는 사장님 설정값(X=79)이 좌측 시작점 같으니 anchor="lt"나 "mm" 중 조절 필요.
            # Start X가 79면 꽤 왼쪽이므로, 글자의 왼쪽 위(lt) 기준일 확률이 높음.
            # 혹은 Start X가 첫 글자의 중심점일 수도 있음. 일단 'mm'(중앙)으로 잡고 테스트.
            
            draw.text((x, y), char, font=font_grid, fill=color, anchor="mm")
            
    return img

# --- [4. 메인 UI] ---
st.title("🎚️ 글자 크기/간격 정밀 조절기 (v10.0)")

col_L, col_R = st.columns([1, 1.5])

with col_L:
    # --- 1. 상단(헤더) 글자 & 간격 ---
    with st.expander("🔽 상단(헤더) 글자 & 간격", expanded=True):
        st.write("🟦 **헤더 배경**")
        # [사진값] 헤더 높이: 310
        header_h = st.slider("헤더 높이", 100, 600, 310) 
        header_bg = st.color_picker("헤더 배경색", "#1E2A47") # 짙은 남색 추정
        
        st.markdown("---")
        st.write("📝 **제목 1 (큰 글씨)**")
        t1_text = st.text_input("제목 1 내용", "숫자 찾기 도전")
        
        c1, c2 = st.columns(2)
        # [사진값] 크기: 60, Y: 90
        with c1: t1_size = st.slider("크기(Size) 1", 10, 200, 60)
        with c2: t1_y = st.slider("위치 Y(1)", 0, 500, 90)
        t1_color = st.color_picker("글자색 1", "#FFFFFF")

        st.markdown("---")
        st.write("📝 **제목 2 (작은 글씨)**")
        t2_text = st.text_input("제목 2 내용", "3초 안에 숫자 '{target}' 찾기")
        
        c3, c4 = st.columns(2)
        # [사진값] 크기: 80, Y: 180
        with c3: t2_size = st.slider("크기(Size) 2", 10, 200, 80)
        with c4: t2_y = st.slider("위치 Y(2)", 0, 500, 180)
        t2_color = st.color_picker("글자색 2", "#FFD700") # 노란색

    # --- 2. 중앙 숫자판 설정 ---
    with st.expander("🔽 중앙 숫자판 설정", expanded=True):
        c_row, c_col = st.columns(2)
        # [사진값] 10 x 10
        with c_row: rows = st.number_input("세로 줄 수", 5, 20, 10)
        with c_col: cols = st.number_input("가로 줄 수", 5, 20, 10)
        
        # [사진값] 숫자 크기: 70
        grid_size = st.slider("숫자 크기", 10, 200, 70)
        grid_color = st.color_picker("숫자 색상", "#000000")
        
        st.markdown("---")
        st.write("📏 **간격 및 시작점 (정밀)**")
        
        # [사진값] 가로간격: 100, 세로간격: 100
        x_spacing = st.slider("가로 간격 (X Spacing)", 10, 200, 100)
        y_spacing = st.slider("세로 간격 (Y Spacing)", 10, 200, 100)
        
        # [사진값] 시작점X: 79, 시작점Y: 400
        start_x = st.slider("시작점 X (첫 글자 위치)", 0, 500, 79)
        start_y = st.slider("시작점 Y (첫 글자 위치)", 0, 800, 400)

with col_R:
    st.header("📝 문제 입력 & 확인")
    
    # 문제 프리셋
    pset = st.selectbox("문제 세트 선택", list(PROBLEM_SETS.keys()))
    w_char, t_char, t_name = PROBLEM_SETS[pset]
    
    # 직접 입력 가능하도록
    c_w, c_t = st.columns(2)
    with c_w: wrong_char = st.text_input("바탕 글자 (많은 거)", w_char)
    with c_t: target_char = st.text_input("찾을 글자 (정답)", t_char)
    
    # 파라미터 패킹
    params = {
        'header_h': header_h, 'header_bg': header_bg,
        't1_text': t1_text, 't1_size': t1_size, 't1_y': t1_y, 't1_color': t1_color,
        't2_text': t2_text, 't2_size': t2_size, 't2_y': t2_y, 't2_color': t2_color,
        'target_name': t_name, # 제목2의 {target} 치환용
        
        'rows': rows, 'cols': cols, 
        'grid_size': grid_size, 'grid_color': grid_color,
        'wrong_char': wrong_char, 'target_char': target_char,
        
        'x_spacing': x_spacing, 'y_spacing': y_spacing,
        'start_x': start_x, 'start_y': start_y,
        
        'is_answer_mode': False
    }

    tab1, tab2 = st.tabs(["❓ 문제용 이미지", "⭕ 정답용 이미지"])
    
    with tab1:
        if st.button("🚀 퀴즈 이미지 생성", type="primary"):
            st.session_state['img_q'] = create_puzzle_image(params)
            
            # 정답용도 미리 생성
            params_ans = params.copy()
            params_ans['is_answer_mode'] = True
            st.session_state['img_a'] = create_puzzle_image(params_ans)

        if 'img_q' in st.session_state:
            st.image(st.session_state['img_q'], caption="문제 이미지", use_container_width=True)
            buf = BytesIO()
            st.session_state['img_q'].save(buf, format="JPEG")
            st.download_button("💾 다운로드 (문제)", buf.getvalue(), "quiz_q.jpg", "image/jpeg")

    with tab2:
        if 'img_a' in st.session_state:
            st.image(st.session_state['img_a'], caption="정답 이미지", use_container_width=True)
            buf = BytesIO()
            st.session_state['img_a'].save(buf, format="JPEG")
            st.download_button("💾 다운로드 (정답)", buf.getvalue(), "quiz_a.jpg", "image/jpeg")