from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile

class CompensationPDFGenerator:
    def __init__(self):
        # フォントパスの設定（優先順位順）
        font_paths = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc',  # 読みやすい太さ
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',  # 代替
            '/System/Library/Fonts/AppleGothic.ttf',           # 最終代替
        ]
        
        self.font_path = None
        for path in font_paths:
            if os.path.exists(path):
                self.font_path = path
                break
        
        if self.font_path is None:
            raise ValueError("適切なフォントが見つかりません")

    def create_text_image(self, text, font_size, width, height, bold=False):
        """テキストを画像として生成"""
        # 高DPIで作成して縮小することで、文字の品質を向上
        scale = 3
        img = Image.new('RGB', (width * scale, height * scale), 'white')
        draw = ImageDraw.Draw(img)
        
        if bold and os.path.exists('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'):
            font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', font_size * scale)
        else:
            font = ImageFont.truetype(self.font_path, font_size * scale)
        
        # テキストのサイズを取得
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # テキストを中央に配置
        x = (width * scale - text_width) // 2
        y = (height * scale - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='black')
        
        # 高DPI画像を適切なサイズに縮小
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return img

    def generate_pdf(self, calculation_data, input_data, filename):
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        with tempfile.TemporaryDirectory() as temp_dir:
            # ヘッダー（タイトル）
            header = self.create_text_image("賠償責任額に関するご案内", 24, 400, 40, bold=True)
            header_path = os.path.join(temp_dir, "header.png")
            header.save(header_path)
            c.drawImage(header_path, 30*mm, 277*mm, width=150*mm, height=10*mm)

            # 日付
            date_text = f"作成日: {datetime.now().strftime('%Y年%m月%d日')}"
            date_img = self.create_text_image(date_text, 10, 200, 20)
            date_path = os.path.join(temp_dir, "date.png")
            date_img.save(date_path)
            c.drawImage(date_path, 130*mm, 270*mm, width=60*mm, height=5*mm)

            # 本文
            content = [
                "拝啓",
                "",
                "平素より格別のお引き立てを賜り、厚く御礼申し上げます。",
                "この度の事故により被られたご負傷とご不便について、心よりお見舞い申し上げます。",
                "ご請求いただきました損害賠償につきまして、現時点でのご提示金額を以下の通り",
                "ご案内させていただきます。",
                "",
                "■ご確認事項",
                ""
            ]

            y_position = 255
            for line in content:
                if line == "":
                    y_position -= 5
                    continue
                
                is_header = line.startswith("■")
                temp_path = os.path.join(temp_dir, f"text_{y_position}.png")
                text_img = self.create_text_image(line, 12, 500, 20, bold=is_header)
                text_img.save(temp_path)
                c.drawImage(temp_path, 25*mm, y_position*mm, width=160*mm, height=5*mm)
                y_position -= 7

            # 基本情報
            info_items = [
                f"事故発生日: {datetime.strptime(input_data['基本情報']['事故日'], '%Y-%m-%d').strftime('%Y年%m月%d日')}",
                f"ご本人様: {input_data['基本情報']['性別']}",
                f"年齢: {input_data['基本情報']['事故時年齢']}歳"
            ]

            for item in info_items:
                temp_path = os.path.join(temp_dir, f"info_{y_position}.png")
                text_img = self.create_text_image(item, 11, 500, 30)
                text_img.save(temp_path)
                c.drawImage(temp_path, 35*mm, y_position*mm, width=150*mm, height=6*mm)
                y_position -= 7

            y_position -= 10

            # 賠償金額
            header_text = "■賠償金額の内訳"
            header_img = self.create_text_image(header_text, 12, 500, 30, bold=True)
            header_path = os.path.join(temp_dir, "amount_header.png")
            header_img.save(header_path)
            c.drawImage(header_path, 25*mm, y_position*mm, width=160*mm, height=6*mm)
            
            y_position -= 12

            # 金額項目
            for item, amount in calculation_data.items():
                if isinstance(amount, int):
                    item_path = os.path.join(temp_dir, f"item_{y_position}.png")
                    amount_path = os.path.join(temp_dir, f"amount_{y_position}.png")
                    
                    item_img = self.create_text_image(item, 11, 300, 30)
                    amount_text = f"¥{amount:,}"
                    amount_img = self.create_text_image(amount_text, 11, 200, 30)
                    
                    item_img.save(item_path)
                    amount_img.save(amount_path)
                    
                    c.drawImage(item_path, 35*mm, y_position*mm, width=80*mm, height=6*mm)
                    c.drawImage(amount_path, 120*mm, y_position*mm, width=55*mm, height=6*mm)
                    
                    y_position -= 7

            y_position -= 5

            # 注意事項
            y_position -= 20
            notes = [
                "■ご留意事項",
                "",
                "・本書面の金額は、現時点でご提供いただいた資料に基づく概算額でございます。",
                "・今後の治療経過や後遺障害の認定等により、金額が変動する可能性がございます。",
                "・ご不明な点やご心配な点がございましたら、担当者までお気軽にご相談ください。",
                "・お客様の回復と今後の生活再建を第一に考え、誠意を持って対応させていただきます。",
                "",
                "なお、本件に関しまして、ご不明な点やご質問等ございましたら、",
                "担当者まで遠慮なくお申し付けください。",
                "",
                "私どもは、お客様の一日も早いご回復を心よりお祈り申し上げております。",
                "",
                "敬具"
            ]

            for note in notes:
                if note == "":
                    y_position -= 5
                    continue
                
                is_header = note.startswith("■")
                temp_path = os.path.join(temp_dir, f"note_{y_position}.png")
                note_img = self.create_text_image(note, 11, 500, 30, bold=is_header)
                note_img.save(temp_path)
                c.drawImage(temp_path, 25*mm, y_position*mm, width=160*mm, height=6*mm)
                y_position -= 7

            # フッター
            footer_text = "担当者連絡先：TEL: 03-XXXX-XXXX（平日 9:00-17:00）"
            footer_img = self.create_text_image(footer_text, 10, 500, 30)
            footer_path = os.path.join(temp_dir, "footer.png")
            footer_img.save(footer_path)
            c.drawImage(footer_path, 25*mm, 15*mm, width=160*mm, height=6*mm)

            c.save()
