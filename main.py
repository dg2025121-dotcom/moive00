import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# ------------------------------------------------------------
# 데이터 불러오기 & 전처리
# ------------------------------------------------------------
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 날짜 열: 하이픈 없는 여덟 자리 숫자(예: 20230101) -> datetime으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 숫자 열들이 문자열(쉼표 포함 등)로 들어올 수 있으니 안전하게 숫자형으로 변환
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
            )

    return df


with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

st.caption(f"데이터 기간: {df['날짜'].min().date()} ~ {df['날짜'].max().date()} · 총 {len(df):,}행")

st.divider()

# ------------------------------------------------------------
# 1구역. 영화별 일별 관객수 변화
# ------------------------------------------------------------
st.header("1. 영화별 일별 관객수 변화")

movie_list = sorted(df["영화명"].dropna().unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list, key="movie_select_1")

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    .loc[:, ["날짜", "일관객"]]
)

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수"},
)
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra></extra>"
)
fig1.update_layout(hovermode="x unified")

st.plotly_chart(fig1, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 한 문장으로 해석을 적어보세요.)")

st.divider()

# ------------------------------------------------------------
# 2구역. (다음 그래프를 추가할 자리)
# ------------------------------------------------------------
st.header("2. (다음 그래프 추가 예정)")
st.write("여기에 다음 그래프를 이어서 추가하세요.")

# st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 3구역. (다음 그래프를 추가할 자리)
# ------------------------------------------------------------
st.header("3. (다음 그래프 추가 예정)")
st.write("여기에 다음 그래프를 이어서 추가하세요.")

# st.info("**이 그래프로 알 수 있는 것:** ")
