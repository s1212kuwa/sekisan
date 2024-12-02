from datetime import datetime
import math

class CompensationCalculator:
    def __init__(self):
        # 後遺障害等級別の労働能力喪失率
        self.disability_rates = {
            "1級": 100, "2級": 100, "3級": 100,
            "4級": 92, "5級": 79, "6級": 67,
            "7級": 56, "8級": 45, "9級": 35,
            "10級": 27, "11級": 20, "12級": 14,
            "13級": 9, "14級": 5
        }
        
        # 介護費用の基準額（日額）
        self.nursing_care_rates = {
            "常時介護": {
                "重度": 25000,
                "中度": 20000,
                "軽度": 15000
            },
            "随時介護": {
                "重度": 15000,
                "中度": 10000,
                "軽度": 7500
            }
        }

        # 年齢別就労可能年数とライプニッツ係数
        self.working_years = self._initialize_working_years()

    def _initialize_working_years(self):
        """年齢別の就労可能年数とライプニッツ係数のテーブルを初期化"""
        return {
            18: {"years": 49, "coefficient": 18.169},
            19: {"years": 48, "coefficient": 18.077},
            20: {"years": 47, "coefficient": 17.981},
            65: {"years": 2, "coefficient": 1.859},
            66: {"years": 1, "coefficient": 0.952}
        }

    def _calculate_leibnitz_coefficient(self, years, rate=0.05):
        """ライプニッツ係数を計算"""
        if years <= 0:
            return 0
        return (1 - math.pow(1 + rate, -years)) / rate

    def _calculate_income_base(self, income_info, employment_info):
        """基礎収入を計算"""
        monthly_base = (income_info["基本給"] + income_info["諸手当"]) * 10000
        
        if income_info.get("時間外手当", 0) > 0:
            monthly_base += income_info["時間外手当"] * 10000
        
        if income_info.get("賞与", 0) > 0:
            monthly_bonus = (income_info["賞与"] * 10000) / 12
            monthly_base += monthly_bonus
        
        if income_info.get("直近3年平均年収", 0) > 0:
            monthly_3years = (income_info["直近3年平均年収"] * 10000) / 12
            monthly_base = max(monthly_base, monthly_3years)
        
        return monthly_base

    def _calculate_disability_grade_adjustment(self, disability_info, basic_info):
        """後遺障害等級に基づく調整係数を計算"""
        base_rate = self.disability_rates[disability_info["後遺障害等級"]]
        
        age = basic_info["事故時年齢"]
        if age < 25:
            base_rate *= 1.1
        elif age > 60:
            base_rate *= 0.9
            
        if disability_info.get("障害の種類") == "精神的障害":
            base_rate *= 1.1
        elif disability_info.get("障害の種類") == "両方":
            base_rate *= 1.2
            
        return min(base_rate, 100)

    def _calculate_disability_loss(self, disability_info, basic_info, income_info, employment_info):
        """後遺障害による逸失利益の計算"""
        if not disability_info.get("後遺障害あり", False):
            return 0
            
        monthly_income = self._calculate_income_base(income_info, employment_info)
        annual_income = monthly_income * 12
        
        loss_rate = self._calculate_disability_grade_adjustment(disability_info, basic_info) / 100
        
        age = basic_info["事故時年齢"]
        if age in self.working_years:
            coefficient = self.working_years[age]["coefficient"]
        else:
            remaining_years = max(67 - age, 0)
            coefficient = self._calculate_leibnitz_coefficient(remaining_years)
        
        disability_loss = annual_income * loss_rate * coefficient
        
        if age < 25:
            disability_loss *= 1.2
            
        if employment_info.get("職種区分") in ["専門職", "技能職"]:
            disability_loss *= 1.1
        
        return int(disability_loss)

    def _calculate_treatment_cost(self, treatment_info):
        """治療関係費の計算"""
        current_cost = treatment_info["医療費合計"]
        
        transport_base = max(
            treatment_info["通院交通費合計"],
            treatment_info["通院日数"] * 2000
        )
        
        future_annual = treatment_info.get("今後の予想医療費", 0)
        future_years = int(treatment_info.get("今後の治療予定期間", 0))
        inflation_rate = 1.02
        future_cost = future_annual * sum(
            math.pow(inflation_rate, i) 
            for i in range(future_years)
        )
        
        nursing_cost = treatment_info.get("看護費用", 0)
        if treatment_info["入院日数"] > 30:
            nursing_cost *= 1.2
            
        other_cost = treatment_info.get("その他医療関連費用", 0)
        
        return int(current_cost + transport_base + future_cost + nursing_cost + other_cost)

    def calculate_compensation(self, input_data):
        """損害賠償額を計算（メインメソッド）"""
        try:
            treatment_cost = self._calculate_treatment_cost(input_data["治療情報"])
            
            disability_loss = self._calculate_disability_loss(
                input_data.get("後遺障害情報", {}),
                input_data["基本情報"],
                input_data["収入情報"],
                input_data["職業情報"]
            )
            
            # 簡易版の結果返却
            return {
                "治療関係費": treatment_cost,
                "後遺障害逸失利益": disability_loss,
                "合計額": treatment_cost + disability_loss
            }

        except Exception as e:
            print(f"計算エラー: {e}")
            raise
