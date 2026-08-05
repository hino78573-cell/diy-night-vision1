import cv2
import numpy as np
from flask import Flask, Response, render_template

app = Flask(__name__)

# បើកកាមេរ៉ា (ប្រសិនបើលេខ 0 เปิดមិនចេញ សូមប្តូរទៅជា 1 ឬ 2)
camera = cv2.VideoCapture(0)

# បើសិនជាកាមេរ៉ាមើលមិនឃើញ សូមពិនិត្យមើលថាតើមានកម្មវិធីផ្សេងកំពុងប្រើប្រាស់វាដែរឬទេ។
if not camera.isOpened():
    print(" সতর্কতা៖ មិនអាចបើកកាមេរ៉ាបានទេ! សូមពិនិត្យមើល Camera Index (ប្តូរ 0 ជា 1)")

def military_grade_night_vision(frame):
    # ១. បម្លែងរូបភាពទៅជា LAB Color Space
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # ២. ប្រើប្រាស់ CLAHE កម្រិតអតិបរមាសម្រាប់ទាញពន្លឺពីទីងងឹតខ្លាំង
    clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(4, 4))
    cl = clahe.apply(l)
    
    # ៣. Bilateral Filter កម្រិតខ្ពស់ ដើម្បីបំបាត់គ្រាប់អុចរំខានពេលទាញពន្លឺខ្លាំង
    denoised_l = cv2.bilateralFilter(cl, d=11, sigmaColor=85, sigmaSpace=85)
    
    # ៤. Advanced Gamma & Digital Gain
    gamma = 1.8
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    bright_l = cv2.LUT(denoised_l, table)
    
    # រួមបញ្ចូលកាណាលវិញ
    limg = cv2.merge((bright_l, a, b))
    enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # ៥. បម្លែងទៅជា Grayscale និងប្រើ Laplacian Edge Sharpening ឱ្យវត្ថុមុតស្រួចច្បាស់
    gray = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)
    
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    
    processed = cv2.convertScaleAbs(sharpened, alpha=2.5, beta=15)
    
    # ៦. បង្កើតបែបផែនពណ៌បៃតងយោធា (Military Phosphor Green PVS-14)
    night_vision = cv2.merge((
        np.zeros_like(processed),  # Blue
        processed,                 # Green
        np.zeros_like(processed)   # Red
    ))
    
    # ៧. បន្ថែមបែបផែន Digital Noise និង Phosphor Grain ស្រាលៗ
    noise = np.random.normal(0, 6, processed.shape).astype(np.uint8)
    night_vision = cv2.add(night_vision, cv2.merge((noise, noise, noise)))
    
    return night_vision

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            processed_frame = military_grade_night_vision(frame)
            
            # បម្លែងជា JPEG Stream
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
