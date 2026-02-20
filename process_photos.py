import os
import shutil
import json
from PIL import Image, ImageOps

# ================= 參數設定區 =================
INPUT_DIR = 'D:\\過年給阿媽的禮物\\grandma-memory\\Original_Photos'      # 原始高畫質資料夾
OUTPUT_DIR = 'D:\\過年給阿媽的禮物\\grandma-memory\\Web_Photos'          # 壓縮後輸出的網頁用資料夾
JSON_OUTPUT = 'timeline_data.json'   # 資料庫檔名

# 瘦身魔法參數 (專門對付 1GB 限制)
MAX_IMAGE_SIZE = 1024  # 將長邊限制在 1024 像素
IMAGE_QUALITY = 50     # 圖片品質降為 50 (網頁載入更快，手機看依然清晰)
# ==============================================

def process_media():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timeline_data = []

    # 排序資料夾，確保時間軸順序正確
    folders = sorted([f for f in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, f))])

    for folder_name in folders:
        # 解析資料夾名稱 (例如: "20230121 過年圍爐")
        parts = folder_name.split(' ', 1)
        date_str = parts[0]
        title_str = parts[1] if len(parts) > 1 else "美好回憶" 

        input_folder_path = os.path.join(INPUT_DIR, folder_name)
        output_folder_path = os.path.join(OUTPUT_DIR, folder_name)
        
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        folder_media_list = []
        files = os.listdir(input_folder_path)
        
        print(f"正在處理: {folder_name} (共 {len(files)} 個檔案)...")

        for file_name in files:
            file_ext = file_name.split('.')[-1].lower()
            input_file_path = os.path.join(input_folder_path, file_name)
            output_file_path = os.path.join(output_folder_path, file_name)
            
            # 網頁圖片相對路徑
            web_path = f"./Web_Photos/{folder_name}/{file_name}"

            if file_ext in ['jpg', 'jpeg', 'png', 'heic']:
                # 壓縮並調整圖片大小
                try:
                    with Image.open(input_file_path) as img:
                        # 修正手機拍攝常遇到的旋轉問題
                        try:
                            img = ImageOps.exif_transpose(img)
                        except:
                            pass
                        
                        # 執行等比例縮小
                        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
                        
                        # 統一轉成 RGB 避免 PNG 透明底變黑塊
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                            
                        # 替換副檔名為 jpg 以減少大小
                        output_file_path = os.path.splitext(output_file_path)[0] + '.jpg'
                        web_path = f"./Web_Photos/{folder_name}/{os.path.splitext(file_name)[0]}.jpg"
                        
                        # 核心瘦身步驟：套用 IMAGE_QUALITY
                        img.save(output_file_path, "JPEG", quality=IMAGE_QUALITY)
                        folder_media_list.append({"type": "image", "src": web_path})
                except Exception as e:
                    print(f"  [錯誤] 圖片 {file_name} 處理失敗: {e}")

            elif file_ext in ['mp4', 'mov', 'webm']:
                # 影片直接複製 (Python 影像套件不處理影片壓縮)
                try:
                    shutil.copy2(input_file_path, output_file_path)
                    folder_media_list.append({"type": "video", "src": web_path})
                except Exception as e:
                    print(f"  [錯誤] 影片 {file_name} 複製失敗: {e}")

        # 若該資料夾內有成功處理的檔案，才加入時間軸
        if folder_media_list:
            timeline_data.append({
                "date": date_str,
                "title": title_str,
                "folder": folder_name,
                "media": folder_media_list
            })

    # 將結果寫入 JSON 檔案
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ 瘦身處理完成！已成功輸出至 {OUTPUT_DIR}")
    print(f"✅ 資料庫檔案已更新：{JSON_OUTPUT}")

if __name__ == "__main__":
    process_media()