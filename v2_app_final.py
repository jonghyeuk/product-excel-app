
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="상품등록 자동화", layout="wide")
st.title("📦 상품등록 자동화 v2 (상품명 직접 입력 버전)")

# ✅ 카테고리 선택
category = st.selectbox("카테고리를 선택하세요", ["문구세트", "라텍스베개"])
category_map = {"문구세트": 50007969, "라텍스베개": 50016741}
category_code = category_map[category]

# ✅ 사용자 입력
product_names = st.text_area("상품명 5개 (한 줄에 하나씩)").splitlines()
price_input = st.text_input("판매가 5개 입력 (쉼표로 구분)", "19900,15800,18800,8800,7500")
details = st.text_area("상세페이지 HTML 5개 (한 줄에 하나씩)").splitlines()
options = st.text_area("옵션 5개 (한 줄에 하나씩, 예: 종류:핑크,노랑)").splitlines()
seller_codes = st.text_area("판매자 코드 5개 (한 줄에 하나씩)").splitlines()

if len(product_names) == 5 and len(details) == 5 and len(options) == 5 and len(seller_codes) == 5:
    if st.button("📥 엑셀 생성하기"):
        prices = list(map(int, price_input.split(",")))
        today = datetime.today().strftime('%m%d')

        def point(val, p):
            if p <= 10000:
                return 100
            elif p <= 30000:
                return 200
            else:
                return 300

        template = pd.read_excel("상품등록완료엑셀_기존데이터유지_정답형.xlsx", sheet_name=0)
        df = template.copy()

        update_cols = {
            "상품상태": "신상품",
            "카테고리ID": category_code,
            "상품명": product_names,
            "판매가": prices,
            "재고수량": 999,
            "A/S 안내내용": "평일 10시부터 5시까지 톡상담가능합니다",
            "A/S 전화번호": "010-2909-3462",
            "대표 이미지 파일명": [f"{today}-{i+1}-1.JPG" for i in range(5)],
            "추가 이미지 파일명": [",".join([f"{today}-{i+1}-{j}.JPG" for j in range(2,6)]) for i in range(5)],
            "상품 상세정보": details,
            "자체상품코드": seller_codes,
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
