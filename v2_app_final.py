
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="상품등록 자동화", layout="wide")
st.title("📦 상품등록 자동화 v2 (최종 수정본)")

# ✅ 1. 카테고리 선택: 문구세트 / 라텍스베개
category = st.selectbox("카테고리를 선택하세요", ["문구세트", "라텍스베개"])
category_map = {"문구세트": 50007969, "라텍스베개": 50016741}
category_code = category_map[category]

# ✅ 2. 사용자 입력
urls = st.text_area("상품 URL 5개 (한 줄에 하나씩)").splitlines()
price_input = st.text_input("판매가 5개 입력 (쉼표로 구분)", "19900,15800,18800,8800,7500")
details = st.text_area("상세페이지 HTML 5개 (한 줄에 하나씩)").splitlines()
options = st.text_area("옵션 5개 (한 줄에 하나씩, 예: 종류:핑크,노랑)").splitlines()

# ✅ 3. 상품명 추출 함수 (오너클랜 제거 포함)
def extract_product_title(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string if soup.title else "상품명없음"
        clean_title = title.strip().replace("\n", " ").replace("\t", " ").split("|")[0]
        return clean_title.replace("오너클랜", "").strip()
    except:
        return "상품명없음"

# ✅ 4. 키워드 추출
def extract_keywords(title):
    raw = title.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    tokens = raw.split()
    stopwords = ["무료", "배송", "최신", "정품", "할인", "사은품"]
    return [kw for kw in tokens if kw not in stopwords and len(kw) >= 2]

# ✅ 5. 최적화 상품명 생성 (3개 추천)
def generate_optimized_names(keywords, max_len=25):
    keywords = list(dict.fromkeys(keywords))
    base = keywords[0]
    name1 = base
    name2 = base
    name3 = base
    for k in keywords[1:]:
        if len(name1 + k) <= max_len:
            name1 += k
        if len(name2 + " " + k) <= max_len:
            name2 += " " + k
        if len(k + base) <= max_len:
            name3 = k + base
    return [name1.strip(), name2.strip(), name3.strip()]

# ✅ 6. 세션 상태로 선택값 유지
if "selected_names" not in st.session_state:
    st.session_state.selected_names = [None] * 5

# ✅ 7. 추천 상품명 보여주고 선택
if len(urls) == 5:
    prices = list(map(int, price_input.split(",")))
    titles = [extract_product_title(url) for url in urls]
    keyword_sets = [extract_keywords(t) for t in titles]
    recommended_names = [generate_optimized_names(kws) for kws in keyword_sets]

    for i in range(5):
        with st.container():
            st.markdown(f"**✅ 상품 {i+1} 추천 이름 선택:**")
            selected = st.radio(
                f"상품명 선택 (상품 {i+1})",
                recommended_names[i],
                key=f"radio_{i}",
                index=0
            )
            st.session_state.selected_names[i] = selected

# ✅ 8. 엑셀 생성 처리
if all(st.session_state.selected_names) and st.button("📥 엑셀 생성하기"):
    today = datetime.today().strftime('%m%d')
    seller_codes = [url.split("selfcode=")[-1] if "selfcode=" in url else "" for url in urls]

    def point(val, p):
        if p <= 10000:
            return 100
        elif p <= 30000:
            return 200
        else:
            return 300

    # ✅ 기존 템플릿 로딩
    template = pd.read_excel("상품등록완료엑셀_기존데이터유지_정답형.xlsx", sheet_name=0)
    df = template.copy()

    # ✅ 업데이트할 열만 정의하여 덮어쓰기
    update_cols = {
        "상품상태": "신상품",
        "카테고리ID": category_code,
        "상품명": st.session_state.selected_names,
        "판매가": prices,
        "재고수량": 999,
        "A/S 안내내용": "평일 10시부터 5시까지 톡상담가능합니다",
        "A/S 전화번호": "010-2909-3462",
        "대표 이미지 파일명": [f"{today}-{i+1}-1.JPG" for i in range(5)],
        "추가 이미지 파일명": [",".join([f"{today}-{i+1}-{j}.JPG" for j in range(2,6)]) for i in range(5)],
        "상품 상세정보": details,
        "판매자코드": seller_codes,
        "텍스트리뷰 작성시 지급 포인트": [point("text", p) for p in prices],
        "포토/동영상 리뷰 작성시 지급 포인트": [point("photo", p)+200 for p in prices],
        "한달사용 텍스트리뷰 작성시 지급 포인트": [point("text", p) for p in prices],
        "한달사용 포토/동영상 리뷰 작성시 지급 포인트": [point("photo", p)+200 for p in prices],
        "알림받기동의 고객 리뷰 작성 시 지급 포인트": [point("alarm", p) for p in prices],
        "AR": [point("ar", p) for p in prices],
        "AS": [point("as", p)+200 for p in prices],
        "AT": [point("at", p)+400 for p in prices],
        "AU": [point("au", p)+600 for p in prices],
        "옵션명": [opt.split(":")[0] for opt in options],
        "옵션값": [opt.split(":")[1] for opt in options],
    }

    for col, val in update_cols.items():
        if col in df.columns:
            df.loc[:4, col] = val if isinstance(val, list) else [val] * 5

    output = BytesIO()
    df.to_excel(output, index=False)
    st.success("✅ 엑셀 생성 완료! 아래에서 다운로드하세요.")
    st.download_button("엑셀 다운로드", data=output.getvalue(), file_name="상품등록완료엑셀_v2.xlsx")
