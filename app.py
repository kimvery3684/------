import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import io

# --- 페이지 설정 ---
st.set_page_config(page_title="틀린 숫자 찾기 생성기", layout="wide")

st.title("🧩 틀린 숫자/글자 찾기 이미지 생성기")

# --- 사이드바: 설정 컨트롤 ---
with st.sidebar:
    st.header("1. 콘텐츠 설정")
    
    # 추천 조합 리스트
    presets = {
        "직접 입력": ("?", "?"),
        "88 vs 98 (클래식)": ("88", "98"),
        "5 vs 2": ("5", "2"),
        "6 vs 9": ("6", "9"),
        "3 vs 8": ("3", "8"),
        "1 vs 7": ("1", "7"),
        "0 vs 8": ("0", "8"),
        "F vs E": ("F", "E"),
        "O vs Q": ("O", "Q"),
        "M vs W": ("M", "W"),
        "B vs 8": ("B", "8"),
        "S vs 5": ("S", "5"),
        "Z vs 2": ("Z", "2"),
        "R vs P": ("R", "P"),
        "K vs X": ("K", "X"),
        "Il vs 1": ("Il", "1"),
        "한글: 갹 vs 가": ("갹", "가"),
        "한글: 먕 vs 밍": ("먕", "밍"),
        "한글: 쀼 vs 뀨": ("쀼", "뀨"),
    }
    
    selected_preset = st.selectbox("추천 조합 선택", list(presets.keys()), index=1)
    
    if selected_preset == "직접 입력":
        base_char = st.text_input("배경 글자 (99개)", value="A")
        target_char = st.text_input("정답 글자 (1개)", value="B")
    else:
        base_char, target_char = presets[selected_preset]
        st.info(f"배경: {base_char} / 정답: {target_char}")

    st.header("2. 상단 바 설정")
    header_text = st.text_input("상단 텍스트", value=f"3초 안에 '{target_char}' 찾기")
    header_bg_color = st.color_picker("상단 배경색", "#1D4ED8") # 파란색 계열
    header_text_color = st.color_picker("상단 글자색", "#FFFF00") # 노란색
    header_height_ratio = st.slider("상단 바 높이 비율", 10, 30, 15)
    header_font_size = st.slider("상단 글자 크기", 20, 100, 45)

    st.header("3. 그리드 설정")
    grid_font_size = st.slider("숫자(본문) 크기", 20, 80, 40)
    grid_gap = st.slider("숫자 간격", 0, 50, 10)

# --- 이미지 생성 로직 ---

def create_puzzle_image(base, target, h_text, h_bg, h_fg, h_ratio, h_f_size, g_f_size, g_gap):
    # 캔버스 설정 (고해상도)
    W, H = 800, 1000
    background_color = "white"
    img = Image.new("RGB", (W, H), background_color)
    draw = ImageDraw.Draw(img)

    # 폰트 로드 (시스템에 있는 한글 폰트 경로로 변경 권장)
    try:
        # 윈도우/맥 환경에 따라 폰트 경로가 다를 수 있습니다.
        # 같은 폴더에 'malgun.ttf'나 'NanumGothic.ttf'를 두고 쓰는 것이 가장 안전합니다.
        font_path = "NanumGothic.ttf" 
        header_font = ImageFont.truetype(font_path, h_f_size)
        grid_font = ImageFont.truetype(font_path, g_f_size)
    except:
        # 폰트가 없으면 기본 폰트 사용 (한글 깨질 수 있음)
        header_font = ImageFont.load_default()
        grid_font = ImageFont.load_default()

    # 1. 상단 바 그리기
    header_height = int(H * (h_ratio / 100))
    draw.rectangle([(0, 0), (W, header_height)], fill=h_bg)
    
    # 상단 텍스트 중앙 정렬
    bbox = draw.textbbox((0, 0), h_text, font=header_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(((W - text_w) / 2, (header_height - text_h) / 2 - 5), h_text, font=header_font, fill=h_fg)

    # 2. 그리드 그리기 (10x10)
    rows, cols = 10, 10
    
    # 정답 위치 랜덤 선정
    target_pos = random.randint(0, rows * cols - 1)
    
    # 그리드 시작 위치 (상단 바 아래부터)
    start_y = header_height + 50
    # 사용 가능한 높이
    available_h = H - start_y - 50
    
    cell_w = W / cols
    cell_h = available_h / rows
    
    for i in range(rows * cols):
        r = i // cols
        c = i % cols
        
        # 현재 위치의 글자 결정
        current_char = target if i == target_pos else base
        
        # 각 셀의 중심 좌표 계산
        cx = c * cell_w + cell_w / 2
        cy = start_y + r * cell_h + cell_h / 2
        
        # 글자 크기 계산 및 그리기
        char_bbox = draw.textbbox((0, 0), current_char, font=grid_font)
        char_w = char_bbox[2] - char_bbox[0]
        char_h = char_bbox[3] - char_bbox[1]
        
        draw.text((cx - char_w / 2, cy - char_h / 2), current_char, fill="black", font=grid_font)

    return img

# --- 메인 화면 출력 ---

# 이미지 생성 버튼 없이 실시간 반영 또는 버튼 클릭 시 생성
if st.button("이미지 생성 (또는 새로고침)", type="primary"):
    generated_img = create_puzzle_image(
        base_char, target_char, 
        header_text, header_bg_color, header_text_color, 
        header_height_ratio, header_font_size, 
        grid_font_size, grid_gap
    )
    
    # 이미지 표시
    st.image(generated_img, caption="생성된 퍼즐 이미지", use_container_width=True)
    
    # 다운로드 버튼
    buf = io.BytesIO()
    generated_img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="이미지 다운로드",
        data=byte_im,
        file_name="puzzle_game.png",
        mime="image/png"
    )
else:
    st.info("왼쪽 사이드바에서 설정을 마친 후 '이미지 생성' 버튼을 눌러주세요.")