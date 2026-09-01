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
# 2구역. 일관객 합계 상위 5편 비교
# ------------------------------------------------------------
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

st.info("**이 그래프로 알 수 있는 것:** (여기에 한 문장으로 해석을 적어보세요.)")

st.divider()

# ------------------------------------------------------------
# 3구역. 날짜별 전체(10위권) 일관객 합계 추이
# ------------------------------------------------------------
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

st.info("**이 그래프로 알 수 있는 것:** (여기에 한 문장으로 해석을 적어보세요.)")

st.divider()

# ------------------------------------------------------------
# 4구역. 일관객 합계 TOP 10 영화
# ------------------------------------------------------------
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

st.info("**이 그래프로 알 수 있는 것:** (여기에 한 문장으로 해석을 적어보세요.)")

st.divider()

# ------------------------------------------------------------
# 5구역. 월 x 요일별 일관객 합계 히트맵
# ------------------------------------------------------------
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

st.info("**이 그래프로 알 수 있는 것:** (여기에 한 문장으로 해석을 적어보세요.)")
