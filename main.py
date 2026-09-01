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
    # 인코딩이 다를 수 있으니 UTF-8을 먼저 시도하고, 실패하면 CP949(EUC-KR)로 재시도
    try:
        df = pd.read_csv(url, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(url, encoding="cp949")

    required_cols = ["날짜", "순위", "영화코드", "영화명", "일관객", "누적관객", "스크린수", "상영횟수"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"필요한 열이 없습니다: {missing} (원본 열: {list(df.columns)})")

    # 날짜 열: 하이픈 없는 여덟 자리 숫자(예: 20230101) -> datetime으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 숫자 열들이 문자열(쉼표 포함 등)로 들어올 수 있으니 안전하게 숫자형으로 변환
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

    return df


try:
    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_data(DATA_URL)
except Exception as e:
    st.error(
        "데이터를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()

# ------------------------------------------------------------
# 사이드바 목차
# ------------------------------------------------------------
st.sidebar.title("📖 목차")
st.sidebar.markdown(
    """
- [1. 영화별 일별 관객수 변화](#section-1)
- [2. 일관객 합계 상위 5편 비교](#section-2)
- [3. 날짜별 전체(10위권) 일관객 합계 추이](#section-3)
- [4. 일관객 합계 TOP 10 영화](#section-4)
- [5. 월 x 요일별 일관객 합계 히트맵](#section-5)
- [6. 선택 영화의 누적관객 변화](#section-6)
"""
)

# ------------------------------------------------------------
# 전체 데이터 요약
# ------------------------------------------------------------
n_days = df["날짜"].nunique()
n_movies = df["영화명"].nunique()
top_movie_row = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index[0]
)

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("수집 기간", f"{df['날짜'].min().date()} ~ {df['날짜'].max().date()}")
col_b.metric("총 일수", f"{n_days:,}일")
col_c.metric("등장 영화 수", f"{n_movies:,}편")
col_d.metric("전체 1위 (합계 기준)", top_movie_row)

st.divider()

# ------------------------------------------------------------
# 1구역. 영화별 일별 관객수 변화
# ------------------------------------------------------------
st.markdown('<div id="section-1"></div>', unsafe_allow_html=True)
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

peak_row = movie_df.loc[movie_df["일관객"].idxmax()]
st.info(
    f"**이 그래프로 알 수 있는 것:** '{selected_movie}'는 "
    f"{peak_row['날짜'].strftime('%Y-%m-%d')}에 일일 관객 수가 "
    f"{int(peak_row['일관객']):,}명으로 가장 많았습니다."
)

st.divider()

# ------------------------------------------------------------
# 2구역. 일관객 합계 상위 5편 비교
# ------------------------------------------------------------
st.markdown('<div id="section-2"></div>', unsafe_allow_html=True)
st.header("2. 일관객 합계 상위 5편 비교")

top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

top5_df = (
    df[df["영화명"].isin(top5_movies)]
    .sort_values("날짜")
    .loc[:, ["날짜", "영화명", "일관객"]]
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일관객 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수", "영화명": "영화명"},
)
fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra></extra>"
)
fig2.update_layout(hovermode="x unified", legend_title_text="영화명 (클릭하여 켜기/끄기)")

st.plotly_chart(fig2, use_container_width=True)

top1_movie = top5_movies[0]
top1_sum = int(df.loc[df["영화명"] == top1_movie, "일관객"].sum())
st.info(
    f"**이 그래프로 알 수 있는 것:** 상위 5편 중 '{top1_movie}'가 "
    f"기간 합계 {top1_sum:,}명으로 가장 많은 관객을 모았습니다."
)

st.divider()

# ------------------------------------------------------------
# 3구역. 날짜별 전체(10위권) 일관객 합계 추이
# ------------------------------------------------------------
st.markdown('<div id="section-3"></div>', unsafe_allow_html=True)
st.header("3. 날짜별 전체(10위권) 일관객 합계 추이")

daily_total = (
    df.groupby("날짜")["일관객"]
    .sum()
    .reset_index()
    .sort_values("날짜")
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={"날짜": "날짜", "일관객": "일일 관객수 합계"},
)
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수 합계: %{y:,}명<extra></extra>"
)
fig3.update_layout(hovermode="x unified")

# 합계가 가장 컸던 상위 3일 찾기
top3_days = daily_total.sort_values("일관객", ascending=False).head(3)

# 상위 3일을 그래프 위에 점 + 날짜 라벨로 표시
fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers+text",
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    marker=dict(color="red", size=10, symbol="star"),
    name="합계 상위 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수 합계: %{y:,}명<extra></extra>",
)

st.plotly_chart(fig3, use_container_width=True)

best_day = top3_days.iloc[0]
st.info(
    f"**이 그래프로 알 수 있는 것:** 10위권 전체 일일 관객 합계는 "
    f"{best_day['날짜'].strftime('%Y-%m-%d')}에 {int(best_day['일관객']):,}명으로 "
    f"1년 중 가장 많았습니다."
)

st.divider()

# ------------------------------------------------------------
# 4구역. 일관객 합계 TOP 10 영화
# ------------------------------------------------------------
st.markdown('<div id="section-4"></div>', unsafe_allow_html=True)
st.header("4. 일관객 합계 TOP 10 영화")

movie_summary = (
    df.groupby("영화명")
    .agg(일관객합계=("일관객", "sum"), 상영일수=("날짜", "count"))
    .reset_index()
)

top10_summary = movie_summary.sort_values("일관객합계", ascending=False).head(10)

fig4 = px.bar(
    top10_summary,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="일관객 합계 TOP 10 영화",
    labels={"일관객합계": "일관객 합계", "영화명": "영화명"},
    custom_data=["상영일수"],
)
fig4.update_traces(
    hovertemplate=(
        "영화명: %{y}<br>"
        "일관객 합계: %{x:,}명<br>"
        "10위권 진입 날수: %{customdata[0]}일"
        "<extra></extra>"
    )
)
# 관객이 많은 영화가 위쪽에 오도록 정렬
fig4.update_layout(yaxis=dict(categoryorder="total ascending"))

st.plotly_chart(fig4, use_container_width=True)

top1_row = top10_summary.iloc[0]
st.info(
    f"**이 그래프로 알 수 있는 것:** '{top1_row['영화명']}'가 합계 "
    f"{int(top1_row['일관객합계']):,}명으로 1위이며, "
    f"{int(top1_row['상영일수'])}일간 10위권에 머물렀습니다."
)

st.divider()

# ------------------------------------------------------------
# 5구역. 월 x 요일별 일관객 합계 히트맵
# ------------------------------------------------------------
st.markdown('<div id="section-5"></div>', unsafe_allow_html=True)
st.header("5. 월 x 요일별 일관객 합계 히트맵")

heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month
heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek  # 0=월요일 ... 6=일요일

weekday_labels = ["월", "화", "수", "목", "금", "토", "일"]

heatmap_pivot = (
    heatmap_df.groupby(["월", "요일"])["일관객"]
    .sum()
    .reset_index()
    .pivot(index="요일", columns="월", values="일관객")
    .reindex(index=range(7))  # 월요일(0)부터 일요일(6) 순서 고정
    .fillna(0)
)
heatmap_pivot.index = weekday_labels
heatmap_pivot.columns = [f"{m}월" for m in heatmap_pivot.columns]

fig5 = px.imshow(
    heatmap_pivot,
    color_continuous_scale="Reds",
    aspect="auto",
    labels=dict(x="월", y="요일", color="일관객 합계"),
    title="월 x 요일별 일관객 합계 히트맵 (색이 진할수록 관객 많음)",
)
fig5.update_traces(
    hovertemplate="%{x} %{y}요일<br>일관객 합계: %{z:,.0f}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

max_idx = heatmap_pivot.stack().idxmax()
max_val = heatmap_pivot.stack().max()
st.info(
    f"**이 그래프로 알 수 있는 것:** {max_idx[1]} {max_idx[0]}요일의 일관객 합계가 "
    f"{int(max_val):,}명으로 가장 높았습니다."
)

st.divider()

# ------------------------------------------------------------
# 6구역. 선택 영화의 누적관객 변화
# ------------------------------------------------------------
st.markdown('<div id="section-6"></div>', unsafe_allow_html=True)
st.header("6. 선택 영화의 누적관객 변화")

selected_movie_6 = st.selectbox("영화를 선택하세요", movie_list, key="movie_select_6")

movie_df_6 = (
    df[df["영화명"] == selected_movie_6]
    .sort_values("날짜")
    .loc[:, ["날짜", "누적관객"]]
)

fig6 = px.line(
    movie_df_6,
    x="날짜",
    y="누적관객",
    markers=True,
    title=f"'{selected_movie_6}' 누적관객 변화",
    labels={"날짜": "날짜", "누적관객": "누적 관객수"},
)
fig6.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>누적 관객수: %{y:,}명<extra></extra>"
)
fig6.update_layout(hovermode="x unified")

st.plotly_chart(fig6, use_container_width=True)

first_row_6 = movie_df_6.iloc[0]
last_row_6 = movie_df_6.iloc[-1]
st.info(
    f"**이 그래프로 알 수 있는 것:** '{selected_movie_6}'는 "
    f"{first_row_6['날짜'].strftime('%Y-%m-%d')} 기준 누적관객 {int(first_row_6['누적관객']):,}명에서 "
    f"{last_row_6['날짜'].strftime('%Y-%m-%d')} 기준 {int(last_row_6['누적관객']):,}명까지 늘었습니다."
)
