import streamlit as st
from datetime import date, datetime
from calculator import CompensationCalculator
import random
from pdf_generator import CompensationPDFGenerator
import os

def generate_registration_number():
    """7桁のランダムな登録番号を生成"""
    return str(random.randint(1000000, 9999999))

def main():
    # セッション状態の初期化
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'registered' not in st.session_state:
        st.session_state.registered = False
    if 'reg_number' not in st.session_state:
        st.session_state.reg_number = None
    if 'input_data' not in st.session_state:
        st.session_state.input_data = None

    st.title("損害賠償額計算システム")

    # 基本情報
    st.subheader("基本情報")
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("生年月日", value=date(1980, 6, 15))
        accident_date = st.date_input("事故日", value=date(2023, 8, 1))
        has_dependents = st.checkbox("扶養家族あり")
    with col2:
        gender = st.selectbox("性別", ["男性", "女性"])
        age_at_accident = st.number_input("事故時年齢", min_value=0, max_value=120)

    # 職業情報
    st.subheader("職業情報")
    col1, col2 = st.columns(2)
    with col1:
        employment_type = st.selectbox(
            "雇用形態",
            ["会社員", "公務員", "自営業", "パート・アルバイト", "学生", "主婦・主夫", "無職", "その他"]
        )
        job_type = st.selectbox(
            "職種区分",
            ["一般", "管理職", "専門職", "技能職", "販売・サービス", "その他"]
        )
    with col2:
        years_of_service = st.number_input("勤続年数", min_value=0)
        if employment_type in ["会社員", "公務員"]:
            company_size = st.selectbox(
                "会社規模",
                ["大企業（500人以上）", "中企業（100-499人）", "小企業（100人未満）"]
            )

    # 収入情報
    st.subheader("収入情報")
    col1, col2, col3 = st.columns(3)
    with col1:
        base_salary = st.number_input("基本給（万円）", value=45)
        allowance = st.number_input("諸手当（万円）", value=8)
        bonus = st.number_input("賞与（年間・万円）", value=150)
    with col2:
        overtime_pay = st.number_input("時間外手当（月額・万円）")
        other_income = st.number_input("その他収入（年間・万円）")
    with col3:
        last_year_income = st.number_input("前年度年収（万円）")
        avg_3years_income = st.number_input("直近3年平均年収（万円）")

    # 治療情報
    st.subheader("治療情報")
    col1, col2 = st.columns(2)
    with col1:
        hospital_days = st.number_input("入院日数", value=120)
        outpatient_days = st.number_input("通院日数", value=80)
        medical_cost = st.number_input("医療費合計", value=2500000)
        transport_cost = st.number_input("通院交通費合計", value=160000)
    with col2:
        future_medical_cost = st.number_input("今後の予想医療費（年間）")
        future_medical_years = st.number_input("今後の治療予定期間（年）")
        nursing_cost = st.number_input("看護費用")
        other_medical_cost = st.number_input("その他医療関連費用")

    # 後遺障害情報
    st.subheader("後遺障害情報")
    has_disability = st.checkbox("後遺障害あり")
    if has_disability:
        col1, col2 = st.columns(2)
        with col1:
            disability_grade = st.selectbox(
                "後遺障害等級",
                [f"{i}級" for i in range(1, 15)]
            )
            disability_type = st.selectbox(
                "後遺障害の種類",
                ["身体的障害", "精神的障害", "両方"]
            )
        with col2:
            needs_nursing = st.checkbox("介護が必要")
            if needs_nursing:
                nursing_level = st.selectbox(
                    "介護レベル",
                    ["常時介護", "随時介護"]
                )
                nursing_years = st.number_input("介護必要期間（年）")

    # 休業損害情報
    st.subheader("休業損害情報")
    col1, col2 = st.columns(2)
    with col1:
        full_time_off = st.number_input("全日休業日数")
        half_time_off = st.number_input("半日休業日数")
        salary_during_off = st.number_input("休業期間中の給与支給額")
    with col2:
        expected_promotion = st.checkbox("昇進・昇給の予定があった")
        if expected_promotion:
            expected_salary_increase = st.number_input("予定されていた昇給額（年額・万円）")

    # 事故状況
    st.subheader("事故状況")
    col1, col2 = st.columns(2)
    with col1:
        fault_percentage = st.slider("過失割合", 0, 100, 20)
        accident_type = st.selectbox(
            "事故の種類",
            ["交通事故", "労災事故", "医療事故", "その他"]
        )
    with col2:
        malicious_factors = st.multiselect(
            "加害者の悪質性",
            ["飲酒運転", "速度超過", "信号無視", "無免許運転", "危険運転", "ひき逃げ"]
        )

    # 素因・既往症情報
    st.subheader("素因・既往症情報")
    col1, col2 = st.columns(2)
    with col1:
        has_preexisting = st.checkbox("既往症あり")
        if has_preexisting:
            preexisting_impact = st.slider("既往症の影響度", 0, 100, 10)
    with col2:
        has_constitutional = st.checkbox("体質的素因あり")
        if has_constitutional:
            constitutional_impact = st.slider("体質的素因の影響度", 0, 100, 10)

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
            },
            "後遺障害情報": {
                "後遺障害あり": has_disability,
                "後遺障害等級": disability_grade if has_disability else None,
                "障害の種類": disability_type if has_disability else None,
                "介護必要": needs_nursing if has_disability else False,
                "介護レベル": nursing_level if has_disability and needs_nursing else None,
                "介護必要期間": nursing_years if has_disability and needs_nursing else 0
            },
            "休業損害情報": {
                "全日休業日数": full_time_off,
                "半日休業日数": half_time_off,
                "休業期間中の給与支給額": salary_during_off,
                "昇進昇給予定": expected_promotion,
                "予定昇給額": expected_salary_increase if expected_promotion else 0
            },
            "事故状況": {
                "事故の種類": accident_type,
                "過失割合": fault_percentage,
                "加害者の悪質性": malicious_factors
            },
            "素因・既往症情報": {
                "既往症あり": has_preexisting,
                "既往症の影響度": preexisting_impact if has_preexisting else 0,
                "体質的素因あり": has_constitutional,
                "体質的素因の影響度": constitutional_impact if has_constitutional else 0
            }
        }
        
        st.session_state.input_data = input_data
        calculator = CompensationCalculator()
        st.session_state.results = calculator.calculate_compensation(input_data)

    # 計算結果の表示
    if st.session_state.results is not None:
        if st.button("登録"):
            st.session_state.registered = True
            st.session_state.reg_number = generate_registration_number()
            
        if st.session_state.registered:
            st.success(f"登録されました。登録番号は{st.session_state.reg_number}です。")
        
        st.subheader("計算結果")
        for item, amount in st.session_state.results.items():
            if isinstance(amount, int):
                st.metric(label=item, value=f"¥{amount:,}")
            else:
                st.metric(label=item, value=str(amount))

        # PDF生成ボタンを追加
        if st.button("賠償責任額のご案内をPDF出力"):
            pdf_generator = CompensationPDFGenerator()
            pdf_path = f"compensation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_generator.generate_pdf(
                st.session_state.results, 
                st.session_state.input_data, 
                pdf_path
            )
            
            # PDFファイルをダウンロード可能にする
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            st.download_button(
                label="PDFをダウンロード",
                data=pdf_bytes,
                file_name=pdf_path,
                mime="application/pdf"
            )
            # 一時ファイルを削除
            os.remove(pdf_path)

if __name__ == "__main__":
    main()