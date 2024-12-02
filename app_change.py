import streamlit as st
from datetime import date
from calculator import CompensationCalculator
import random
from pdf_generator import CompensationPDFGenerator
from datetime import datetime
import os

def get_sample_data(reg_number):
    """登録番号に基づいてデータを取得（サンプル）"""
    return {
        "基本情報": {
            "生年月日": date(1980, 6, 15),
            "事故日": date(2023, 8, 1),
            "性別": "男性",
            "事故時年齢": 43,
            "扶養家族あり": True
        },
        "職業情報": {
            "雇用形態": "会社員",
            "職種区分": "一般",
            "勤続年数": 15,
            "会社規模": "大企業（500人以上）"
        },
        "収入情報": {
            "基本給": 45,
            "諸手当": 8,
            "賞与": 150,
            "時間外手当": 5,
            "その他収入": 20,
            "前年度年収": 650,
            "直近3年平均年収": 630
        },
        "治療情報": {
            "入院日数": 120,
            "通院日数": 80,
            "医療費合計": 2500000,
            "通院交通費合計": 160000,
            "今後の予想医療費": 500000,
            "今後の治療予定期間": 2,
            "看護費用": 300000,
            "その他医療関連費用": 100000
        }
    }

def main():
    # セッション状態の初期化
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'input_data' not in st.session_state:
        st.session_state.input_data = None

    st.title("損害賠償額計算システム（確認・修正）")

    # 登録番号入力
    reg_number = st.text_input("登録番号（7桁）を入力してください")
    
    if st.button("検索"):
        if len(reg_number) == 7 and reg_number.isdigit():
            st.success("検索成功！")
            st.session_state.current_data = get_sample_data(reg_number)
            st.session_state.data_loaded = True
        else:
            st.error("正しい登録番号を入力してください")

    # データが読み込まれている場合のみ表示
    if st.session_state.data_loaded and st.session_state.current_data:
        data = st.session_state.current_data
        
        # 基本情報
        st.subheader("基本情報")
        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input("生年月日", value=data["基本情報"]["生年月日"])
            accident_date = st.date_input("事故日", value=data["基本情報"]["事故日"])
            has_dependents = st.checkbox("扶養家族あり", value=data["基本情報"]["扶養家族あり"])
        with col2:
            gender = st.selectbox("性別", ["男性", "女性"], 
                                index=["男性", "女性"].index(data["基本情報"]["性別"]))
            age_at_accident = st.number_input("事故時年齢", 
                                            value=data["基本情報"]["事故時年齢"])

        # 職業情報
        st.subheader("職業情報")
        col1, col2 = st.columns(2)
        with col1:
            employment_type = st.selectbox(
                "雇用形態",
                ["会社員", "公務員", "自営業", "パート・アルバイト", "学生", "主婦・主夫", "無職", "その他"],
                index=["会社員", "公務員", "自営業", "パート・アルバイト", "学生", "主婦・主夫", "無職", "その他"].index(data["職業情報"]["雇用形態"])
            )
            job_type = st.selectbox(
                "職種区分",
                ["一般", "管理職", "専門職", "技能職", "販売・サービス", "その他"],
                index=["一般", "管理職", "専門職", "技能職", "販売・サービス", "その他"].index(data["職業情報"]["職種区分"])
            )
        with col2:
            years_of_service = st.number_input("勤続年数", value=data["職業情報"]["勤続年数"])
            if employment_type in ["会社員", "公務員"]:
                company_size = st.selectbox(
                    "会社規模",
                    ["大企業（500人以上）", "中企業（100-499人）", "小企業（100人未満）"],
                    index=["大企業（500人以上）", "中企業（100-499人）", "小企業（100人未満）"].index(data["職業情報"]["会社規模"])
                )

        # 収入情報
        st.subheader("収入情報")
        col1, col2, col3 = st.columns(3)
        with col1:
            base_salary = st.number_input("基本給（万円）", value=data["収入情報"]["基本給"])
            allowance = st.number_input("諸手当（万円）", value=data["収入情報"]["諸手当"])
            bonus = st.number_input("賞与（年間・万円）", value=data["収入情報"]["賞与"])
        with col2:
            overtime_pay = st.number_input("時間外手当（月額・万円）", value=data["収入情報"]["時間外手当"])
            other_income = st.number_input("その他収入（年間・万円）", value=data["収入情報"]["その他収入"])
        with col3:
            last_year_income = st.number_input("前年度年収（万円）", value=data["収入情報"]["前年度年収"])
            avg_3years_income = st.number_input("直近3年平均年収（万円）", value=data["収入情報"]["直近3年平均年収"])

        # 治療情報
        st.subheader("治療情報")
        col1, col2 = st.columns(2)
        with col1:
            hospital_days = st.number_input("入院日数", value=data["治療情報"]["入院日数"])
            outpatient_days = st.number_input("通院日数", value=data["治療情報"]["通院日数"])
            medical_cost = st.number_input("医療費合計", value=data["治療情報"]["医療費合計"])
            transport_cost = st.number_input("通院交通費合計", value=data["治療情報"]["通院交通費合計"])
        with col2:
            future_medical_cost = st.number_input("今後の予想医療費（年間）", value=data["治療情報"]["今後の予想医療費"])
            future_medical_years = st.number_input("今後の治療予定期間（年）", value=data["治療情報"]["今後の治療予定期間"])
            nursing_cost = st.number_input("看護費用", value=data["治療情報"]["看護費用"])
            other_medical_cost = st.number_input("その他医療関連費用", value=data["治療情報"]["その他医療関連費用"])

        # 後遺障害情報（以下同様に他の情報も追加）
        # ... 

        # 計算ボタン
        if st.button("計算実行", type="primary"):
            input_data = {
                "基本情報": {
                    "生年月日": birth_date.strftime("%Y-%m-%d"),
                    "事故日": accident_date.strftime("%Y-%m-%d"),
                    "性別": gender,
                    "事故時年齢": age_at_accident,
                    "扶養家族あり": has_dependents
                },
                "職業情報": {
                    "雇用形態": employment_type,
                    "職種区分": job_type,
                    "勤続年数": years_of_service,
                    "会社規模": company_size if employment_type in ["会社員", "公務員"] else None
                },
                "収入情報": {
                    "基本給": base_salary,
                    "諸手当": allowance,
                    "賞与": bonus,
                    "時間外手当": overtime_pay,
                    "その他収入": other_income,
                    "前年度年収": last_year_income,
                    "直近3年平均年収": avg_3years_income
                },
                "治療情報": {
                    "入院日数": hospital_days,
                    "通院日数": outpatient_days,
                    "医療費合計": medical_cost,
                    "通院交通費合計": transport_cost,
                    "今後の予想医療費": future_medical_cost,
                    "今後の治療予定期間": future_medical_years,
                    "看護費用": nursing_cost,
                    "その他医療関連費用": other_medical_cost
                }
            }

            st.session_state.input_data = input_data  # ここで保存
            calculator = CompensationCalculator()
            st.session_state.results = calculator.calculate_compensation(input_data)

        # 計算結果の表示
        if st.session_state.results is not None:
            if st.button("更新"):
                st.success("データが更新されました！")
            
            st.subheader("計算結果")
            for item, amount in st.session_state.results.items():
                if isinstance(amount, int):
                    st.metric(label=item, value=f"¥{amount:,}")
                else:
                    st.metric(label=item, value=str(amount))

            # PDF生成ボタン
            if st.button("賠償責任額のご案内をPDF出力"):
                pdf_generator = CompensationPDFGenerator()
                pdf_path = f"compensation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                pdf_generator.generate_pdf(
                    st.session_state.results,
                    st.session_state.input_data,
                    pdf_path
                )
                
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                st.download_button(
                    label="PDFをダウンロード",
                    data=pdf_bytes,
                    file_name=pdf_path,
                    mime="application/pdf"
                )
                
                os.remove(pdf_path)

if __name__ == "__main__":
    main()