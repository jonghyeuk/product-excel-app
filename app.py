
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.title("상품등록 자동화 엑셀 생성기 (입력값만 덮어쓰기)")

category = st.selectbox("카테고리를 선택하세요", ["문구세트", "목쿠션"])
category_code = 50007969 if category == "문구세트" else 50003651

urls = st.text_area("상품 URL 5개 (한 줄에 하나씩)").splitlines()
price_input = st.text_input("가격 5개 입력 (쉼표로 구분)", "19900,15800,18800,8800,7500")
prices = list(map(int, price_input.split(",")))
details = st.text_area("상세페이지 링크 5개 (한 줄에 하나씩)").splitlines()
options = st.text_area("옵션 5개 (한 줄에 하나씩, 예: 종류:핑크,노랑)").splitlines()

def extract_keywords(url):
    return "문구세트"

def generate_product_name(keyword):
    return f"초등학생 {keyword} 팬시선물"

if st.button("엑셀 생성하기"):
    # 기존 엑셀 불러오기
    template = pd.read_excel("상품등록완료엑셀_기존데이터유지_정답형.xlsx", sheet_name=0)
    df = template.copy()

    today = datetime.today().strftime('%m%d')

    update_cols = {
        "상품상태": "신상품",
        "카테고리ID": category_code,
        "상품명": [generate_product_name(extract_keywords(u)) for u in urls],
        "판매가": prices,
        "재고수량": 999,
        "A/S 안내내용": "평일 10시부터 5시까지 톡상담가능합니다",
        "A/S 전화번호": "010-2909-3462",
        "대표 이미지 파일명": [f"{today}-{i+1}-1.JPG" for i in range(5)],
        "추가 이미지 파일명": [",".join([f"{today}-{i+1}-{j}.JPG" for j in range(2,6)]) for i in range(5)],
        "상품 상세정보": details,
        "AR": [100 if p <= 10000 else 200 if p <= 30000 else 300 for p in prices],
        "AS": [300 if p <= 10000 else 400 if p <= 30000 else 500 for p in prices],
        "AT": [500 if p <= 10000 else 600 if p <= 30000 else 700 for p in prices],
        "AU": [700 if p <= 10000 else 800 if p <= 30000 else 900 for p in prices],
        "옵션명": [opt.split(":")[0] if ":" in opt else "" for opt in options],
        "옵션값": [opt.split(":")[1] if ":" in opt else "" for opt in options]
    }

    for col, val in update_cols.items():
        if col in df.columns:
            if isinstance(val, list):
                df.loc[:4, col] = val
            else:
                df.loc[:4, col] = [val] * 5

    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("엑셀 파일 다운로드", data=output.getvalue(), file_name="상품등록완료엑셀.xlsx")

