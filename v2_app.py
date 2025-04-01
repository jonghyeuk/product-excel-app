
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import requests
from bs4 import BeautifulSoup

st.title("📦 상품등록 자동화 v2 (최적화 상품명 포함)")

# 입력
urls = st.text_area("상품 URL 5개 (한 줄에 하나씩)").splitlines()
price_input = st.text_input("판매가 5개 입력 (쉼표로 구분)", "19900,15800,18800,8800,7500")
details = st.text_area("상세페이지 HTML 5개 (한 줄에 하나씩)").splitlines()
options = st.text_area("옵션 5개 (한 줄에 하나씩, 예: 종류:핑크,노랑)").splitlines()

# 상품명 추출
def extract_product_title(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string if soup.title else "상품명없음"
        return title.strip().replace("\n", " ").replace("\t", " ").split("|")[0]
    except:
        return "상품명없음"

# 키워드 분석 (간단 모사)
def extract_keywords(title):
    raw = title.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    tokens = raw.split()
    stopwords = ["무료", "배송", "최신", "정품", "할인", "사은품"]
    return [kw for kw in tokens if kw not in stopwords and len(kw) >= 2]

# 최적화 상품명 생성
def generate_optimized_names(keywords, max_len=25):
    keywords = list(dict.fromkeys(keywords))  # 중복 제거
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

# 메인 처리
if st.button("엑셀 생성하기") and len(urls) == 5:
    prices = list(map(int, price_input.split(",")))
    titles = [extract_product_title(url) for url in urls]
    keyword_sets = [extract_keywords(t) for t in titles]
    recommended_names = [generate_optimized_names(kws) for kws in keyword_sets]

    selected_names = []
    for i, name_set in enumerate(recommended_names):
        st.markdown(f"**[{i+1}번 상품명 추천]**")
        selected = st.radio(f"추천 상품명 선택 (상품 {i+1})", name_set, key=f"name_{i}")
        selected_names.append(selected)

    today = datetime.today().strftime('%m%d')
    seller_codes = [url.split("selfcode=")[-1] if "selfcode=" in url else "" for url in urls]

    # 가격 기반 포인트
    def point(val, p):
        if p <= 10000:
            return 100
        elif p <= 30000:
            return 200
        else:
            return 300

    data = {
        "상품상태": ["신상품"] * 5,
        "카테고리ID": [50007969] * 5,
        "상품명": selected_names,
        "판매가": prices,
        "재고수량": [999] * 5,
        "A/S 안내내용": ["평일 10시부터 5시까지 톡상담가능합니다"] * 5,
        "A/S 전화번호": ["010-2909-3462"] * 5,
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

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    st.success("✅ 엑셀 생성 완료! 아래에서 다운로드하세요.")
    st.download_button("엑셀 다운로드", data=output.getvalue(), file_name="상품등록완료엑셀_v2.xlsx")
