import random
import streamlit as st


def generate_pair(decimals: int, min_int: int = 0, max_int: int = 99, allow_equal: float = 0.12):
    """Generate two decimal numbers with given decimal places and integer range.

    allow_equal: probability of generating an exactly equal pair (for practice)
    min_int/max_int: inclusive integer part range (e.g. 0..9 for small numbers)
    """
    scale = 10 ** decimals
    # integer part range scaled
    a = random.randint(min_int * scale, max_int * scale) / scale
    # sometimes make them equal to give '같다' 연습
    if random.random() < allow_equal:
        b = a
    else:
        b = random.randint(min_int * scale, max_int * scale) / scale
        # avoid accidental equality sometimes
        if b == a:
            # bump by one unit in the last decimal place and wrap within max_int
            b = ((int(b * scale) + 1) % ((max_int + 1) * scale)) / scale
    return a, b


def format_num(x: float, decimals: int):
    fmt = f"{{:.{decimals}f}}"
    return fmt.format(x)


st.set_page_config(page_title="소수(소수점) 비교 퀴즈", page_icon="🧠")

# --- Cute / kid-friendly styles ---
st.markdown(
        """
        <style>
            .big-title {font-size:38px; font-weight:800; color:#ff6b6b;}
            .subtitle {font-size:18px; color:#333333; margin-bottom:12px}
            .metric-big {font-size:22px; font-weight:700; color:#0b7285}
            .stButton>button {height:56px; font-size:18px; border-radius:12px;}
            .card {background: linear-gradient(135deg, #fff7f6 0%, #fffefc 100%); padding:12px; border-radius:12px}
        </style>
        """,
        unsafe_allow_html=True,
)

st.markdown("<div class='big-title'>🦊 소수 비교 퀴즈 — 누가 더 클까요?</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>간단한 대소비교 문제로 소수점 비교 연습을 해요. 큰 버튼을 눌러 정답을 골라보세요! 🎯</div>", unsafe_allow_html=True)

# --- 세팅 패널 ---
with st.sidebar:
    st.header("설정")
    # problem sets by grade / difficulty
    problem_sets = {
        "기본 연습 (중간)": {"decimals": 2, "min": 0, "max": 99},
        "1학년 — 쉬움 (소수 첫째자리, 0~9)": {"decimals": 1, "min": 0, "max": 9},
        "2학년 — 쉬움 (소수 첫째자리, 0~20)": {"decimals": 1, "min": 0, "max": 20},
        "3학년 — 중간 (소수 둘째자리, 0~50)": {"decimals": 2, "min": 0, "max": 50},
        "4학년 — 중간 (소수 둘째자리, 0~99)": {"decimals": 2, "min": 0, "max": 99},
        "5-6학년 — 어려움 (소수 셋째자리, 0~99)": {"decimals": 3, "min": 0, "max": 99},
    }
    chosen_set = st.selectbox("문제 세트(학년/난이도)", list(problem_sets.keys()), index=0)
    set_conf = problem_sets[chosen_set]
    decimals = set_conf["decimals"]
    min_int = set_conf["min"]
    max_int = set_conf["max"]

    if 'allow_equal' not in st.session_state:
        st.session_state.allow_equal = True
    st.session_state.allow_equal = st.checkbox("같은 값 문제 허용", value=st.session_state.allow_equal)

    if 'auto_generate' not in st.session_state:
        st.session_state.auto_generate = True
    st.session_state.auto_generate = st.checkbox("페이지 로드 시 자동 출제", value=st.session_state.auto_generate)

    if st.button("🔄 점수 초기화", key="reset_button"):
        for k in ['score','total','streak','left','right','message']:
            if k in st.session_state:
                del st.session_state[k]
        # Streamlit will re-run the script after this button press,
        # so explicit experimental_rerun() is not required (and may be unavailable).

# --- 상태 초기화 ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'message' not in st.session_state:
    st.session_state.message = "준비됐나요? 시작하려면 '다음 문제'를 눌러요."

cols = st.columns([1, 1, 1])
cols[0].metric("정답", st.session_state.score)
cols[1].metric("시도", st.session_state.total)
cols[2].metric("연속 정답", st.session_state.streak)

st.write(st.session_state.message)


def new_question():
    a, b = generate_pair(decimals, min_int=min_int, max_int=max_int,
                         allow_equal=0.12 if st.session_state.allow_equal else 0.0)
    st.session_state.left = a
    st.session_state.right = b


def show_explanation(a: float, b: float, decimals: int):
    A = format_num(a, decimals)
    B = format_num(b, decimals)
    # align by decimal point
    if '.' in A:
        left_int, left_frac = A.split('.')
    else:
        left_int, left_frac = A, ''
    if '.' in B:
        right_int, right_frac = B.split('.')
    else:
        right_int, right_frac = B, ''
    # pad
    max_int = max(len(left_int), len(right_int))
    max_frac = max(len(left_frac), len(right_frac))
    left_line = left_int.rjust(max_int) + '.' + left_frac.ljust(max_frac)
    right_line = right_int.rjust(max_int) + '.' + right_frac.ljust(max_frac)
    st.write("**정답 설명 (자리 맞춰 보기)**")
    st.code(f"왼쪽:  {left_line}\n오른쪽: {right_line}")


st.markdown("---")

# show current or prompt
if 'left' not in st.session_state or 'right' not in st.session_state:
    # auto-generate first question if the user enabled it
    if 'auto_generate' in st.session_state and st.session_state.auto_generate:
        new_question()
    else:
        st.info("문제 없음 — 아래 '다음 문제'를 눌러 문제를 출제하세요.")
else:
    st.subheader("문제")
    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    c1.metric("왼쪽", format_num(st.session_state.left, decimals))
    c2.metric("오른쪽", format_num(st.session_state.right, decimals))

    # buttons (cute labels + emoji)
    ans_cols = st.columns(3)
    left_btn = ans_cols[0].button("🐢 왼쪽이 더 커요", key="btn_left")
    eq_btn = ans_cols[1].button("🤝 같아요", key="btn_eq")
    right_btn = ans_cols[2].button("🐇 오른쪽이 더 커요", key="btn_right")

    submitted = False
    user_choice = None
    if left_btn:
        submitted = True
        user_choice = 'left'
    elif right_btn:
        submitted = True
        user_choice = 'right'
    elif eq_btn:
        submitted = True
        user_choice = 'eq'

    if submitted:
        a = st.session_state.left
        b = st.session_state.right
        correct = 'eq' if abs(a - b) < (1 / (10 ** decimals)) / 2 else ('left' if a > b else 'right')
        st.session_state.total += 1
        if user_choice == correct:
            st.session_state.score += 1
            st.session_state.streak += 1
            st.success("정답! 🎉")
        else:
            st.session_state.streak = 0
            st.error("아쉽습니다 — 틀렸어요.")
        show_explanation(a, b, decimals)

    # next/힌트
    hint_col, next_col = st.columns([1, 1])
    with hint_col:
        with st.expander("힌트 보기 (자리별로 맞춰서 비교해요)"):
            if 'left' in st.session_state and 'right' in st.session_state:
                show_explanation(st.session_state.left, st.session_state.right, decimals)
    if next_col.button("다음 문제 ➜", key="next_inside"):
        new_question()
        st.session_state.message = "새 문제 출제됨! 어떤 것이 큰지 골라보세요. 😊"
        # Button press causes Streamlit to re-run automatically; no explicit rerun needed.

st.markdown("---")
if st.button("다음 문제 ➜", key="next_outside") and ('left' not in st.session_state or 'right' not in st.session_state):
    new_question()
    # No explicit rerun required here either.

st.caption("원하면 '같은 값 문제 허용' 체크를 해제해 같은 문제가 나오지 않게 할 수 있어요.")
