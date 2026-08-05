import os
import base64
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 🤖 បង្កើតម៉ាស៊ីន AI ស្កេនចលនា និងស្រមោលកម្តៅមនុស្ស/សត្វក្នុងងងឹត (AI Core Initializer)
# (ប្រើប្រាស់រូបមន្ត គណិតវិទ្យាកម្រិតខ្ពស់ដើម្បីតាមដានគោលដៅដោយមិនពឹងលើ Google)
ai_detector = None

def get_ai_detector():
    import cv2  # ហៅ OpenCV មកដំឡើងខាងក្នុងប្រព័ន្ធ
    global ai_detector
    if ai_detector is None:
        # បង្កើតឧបករណ៍ AI ជំនាន់ចុងក្រោយសម្រាប់ស្វែងរកការផ្លាស់ប្តូរភាគល្អិតពន្លឺពេលយប់
        ai_detector = cv2.createBackgroundSubtractorMOG2(
            history=300, 
            varThreshold=24, 
            detectShadows=True
        )
    return ai_detector

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    import cv2
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data'}), 400
        
    try:
        # ១. ដោះកូដបំប្លែងទិន្នន័យ Base64 ពីទូរសព្ទ Oppo មកជារូបភាព BGR ធម្មតា
        img_data = data['image'].split(',')
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            # 🔄 ២. ម៉ាស៊ីន AI ទី១: ជម្រុញពន្លឺទម្លាយភាពងងឹតស្លុប ៨ដង (Super-Adaptive Amplification)
            yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            
            # AI គណនាទាញរស្មីពន្លឺងងឹត (Mathematical Max Gain)
            clahe = cv2.createCLEHE(clipLimit=6.0, tileGridSize=(8,8)) if hasattr(cv2, 'createCLEHE') else cv2.createCLAHE(clipLimit=6.0, tileGridSize=(8,8))
            y_boosted = clahe.apply(y)
            y_boosted = cv2.convertScaleAbs(y_boosted, alpha=2.5, beta=100) # Brightness Max Boost
            
            final_yuv = cv2.merge((y_boosted, u, v))
            boosted_bgr = cv2.cvtColor(final_yuv, cv2.COLOR_YUV2BGR)
            gray_boosted = cv2.cvtColor(boosted_bgr, cv2.COLOR_BGR2GRAY)

            # 🔄 ៣. ម៉ាស៊ីន AI ទី២: កាត់បន្ថយគ្រាប់បែក Noise និងព្រិលៗពេលយប់ (Bilateral Spatial Filter)
            # ជួយឱ្យសាច់វីដេអូបៃតងម៉ត់ស្អាត ងាយស្រួលមើលគែមវត្ថុ
            filtered_gray = cv2.bilateralFilter(gray_boosted, d=7, sigmaColor=65, sigmaSpace=65)

            # -----------------------------------------------------------------
            # 📝 [ចំណាំ]៖ កូដ AI ម៉ាស៊ីនទី៣ និងទី៤ (Part 2) សម្រាប់ស្កេនឡុក Lock គោលដៅមនុស្ស និងសត្វ 
            # នឹងត្រូវយកមកសរសេរដោតភ្ជាប់បន្តនៅខាងក្រោមជួរនេះ
            # -----------------------------------------------------------------

            # បំប្លែងរូបភាពជាពណ៌បៃតងយោធាជាបណ្តោះអាសន្នសម្រាប់ Part 1
            green_matrix = np.zeros_like(boosted_bgr)
            green_matrix[:, :, 1] = filtered_gray

            _, buffer = cv2.imencode('.jpg', green_matrix)
            encoded_img = base64.b64encode(buffer).decode('utf-8')
            return jsonify({'image': f'data:image/jpeg;base64,{encoded_img}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Processing failed'}), 500
import os
import base64
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 🤖 បង្កើតម៉ាស៊ីន AI ស្កេនចលនា និងស្រមោលកម្តៅមនុស្ស/សត្វក្នុងងងឹត (AI Core Initializer)
ai_detector = None

def get_ai_detector():
    import cv2
    global ai_detector
    if ai_detector is None:
        # បង្កើតឧបករណ៍ AI ជំនាន់ចុងក្រោយសម្រាប់ស្វែងរកការផ្លាស់ប្តូរភាគល្អិតពន្លឺពេលយប់
        ai_detector = cv2.createBackgroundSubtractorMOG2(
            history=300, 
            varThreshold=24, 
            detectShadows=True
        )
    return ai_detector

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    import cv2
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data'}), 400
        
    try:
        # ១. ដោះកូដបំប្លែងទិន្នន័យ Base64 ពីទូរសព្ទ Oppo មកជារូបភាព BGR ធម្មតា
        img_data = data['image'].split(',')
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            # 🔄 ២. ម៉ាស៊ីន AI ទី១: ជម្រុញពន្លឺទម្លាយភាពងងឹតស្លុប ៨ដង (Super-Adaptive Amplification)
            yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            
            # AI គណនាទាញរស្មីពន្លឺងងឹត (Mathematical Max Gain)
            clahe = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(8,8))
            y_boosted = clahe.apply(y)
            y_boosted = cv2.convertScaleAbs(y_boosted, alpha=2.5, beta=100) # Brightness Max Boost
            
            final_yuv = cv2.merge((y_boosted, u, v))
            boosted_bgr = cv2.cvtColor(final_yuv, cv2.COLOR_YUV2BGR)
            gray_boosted = cv2.cvtColor(boosted_bgr, cv2.COLOR_BGR2GRAY)

            # 🔄 ៣. ម៉ាស៊ីន AI ទី២: កាត់បន្ថយគ្រាប់បែក Noise និងព្រិលៗពេលយប់ (Bilateral Spatial Filter)
            filtered_gray = cv2.bilateralFilter(gray_boosted, d=7, sigmaColor=65, sigmaSpace=65)

            # 🔄 ៤. ម៉ាស៊ីន AI ទី៣: ស្កេនទាញយកតែស្រមោលរូបរាងមនុស្ស/សត្វ (Thermal Silhouette Segmentation)
            detector = get_ai_detector()
            ai_mask = detector.apply(filtered_gray)
            
            # លុបគ្រាប់អុចៗតូចៗដែលមិនមែនជាមនុស្សចេញពីម៉ាស៊ីន AI (Morphological Opening)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            ai_mask = cv2.morphologyEx(ai_mask, cv2.MORPH_OPEN, kernel)

            # 🔄 ៥. ម៉ាស៊ីន AI ទី៤: គណនាគូសខ្សែប្លង់ Lock គោលដៅ (AI Kernel Contour Predictor)
            contours, _ = cv2.findContours(ai_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # បង្កើតផ្ទាំងពណ៌បៃតងយោធាអាជីព (True Military Green Filter)
            green_matrix = np.zeros_like(boosted_bgr)
            green_matrix[:, :, 1] = filtered_gray

            for cnt in contours:
                # ស្កេនរកតែគោលដៅណាដែលមានទំហំធំល្មមដូចជា មនុស្ស ឬសត្វ
                if cv2.contourArea(cnt) > 2000:
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    # គូសប្រអប់ Target Lock ពណ៌បៃតងក្រាស់ៗ ដេញតាមគោលដៅចំពោះមុខ
                    cv2.rectangle(green_matrix, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    
                    # គូសផ្ទាំង Highlight ពណ៌បៃតងស្រាលនៅខាងក្នុងប្រអប់ដើម្បីឱ្យងាយមើលឃើញរូបរាងក្នុងងងឹត
                    overlay = green_matrix.copy()
                    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), -1)
                    cv2.addWeighted(overlay, 0.15, green_matrix, 0.85, 0, green_matrix)
                    
                    # សរសេរអក្សរ Lock គោលដៅពីលើក្បាលមនុស្ស ឬសត្វ
                    cv2.putText(green_matrix, "[NATIVE-AI: TARGET_LOCK]", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # បំប្លែងរូបភាពដែលកែច្នៃរួច ផ្ញើត្រឡប់ទៅបង្ហាញនៅលើ HTML វិញភ្លាមៗ
            _, buffer = cv2.imencode('.jpg', green_matrix)
            encoded_img = base64.b64encode(buffer).decode('utf-8')
            return jsonify({'image': f'data:image/jpeg;base64,{encoded_img}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Processing failed'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
