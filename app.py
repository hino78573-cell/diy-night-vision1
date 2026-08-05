import cv2
import numpy as np
from flask import Flask, Response, render_template

app = Flask(__name__)

# បើកកាមេរ៉ា (Webcam ឬ កាមេរ៉ាទូរសព្ទដែលតភ្ជាប់តាម IP/USB)
camera = cv2.VideoCapture(0)

def advanced_ai_night_vision(frame):
    # ១. បម្លែងរូបភាពទៅជា LAB Color Space ដើម្បីញែកកម្រិតពន្លឺ (Luminance - L) ចេញពីពណ៌
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # ២. ប្រើប្រាស់ AI-based CLAHE កម្រិតខ្ពស់ (កាត់បន្ថយភាពរំខាន និងទាញពន្លឺអតិបរមាពីភាពងងឹត)
    clahe = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(4, 4))
    cl = clahe.apply(l)
    
    # ៣. ប្រើប្រាស់ Bilateral Filter ដើម្បីបំបាត់គ្រាប់អុចរំខាន (Noise Reduction) តែនៅតែរក្សាគែមវត្ថុឱ្យច្បាស់
    # នេះជាមុខងារសំខាន់ដែលធ្វើឱ្យរូបភាពមើលទៅរលោង និងមិនព្រិលពេលស្ថិតក្នុងទីងងឹតខ្លាំង
    denoised_l = cv2.bilateralFilter(cl, d=9, sigmaColor=75, sigmaSpace=75)
    
    # ៤. Adaptive Gamma Correction (កែតម្រូវអាំងតង់ស៊ីតេពន្លឺស្វ័យប្រវត្តិស្របតាមបរិយាកាសងងឹត)
    gamma = 1.6
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    bright_l = cv2.LUT(denoised_l, table)
    
    # រួមបញ្ចូលកាណាលពន្លឺ និងពណ៌ដើមវិញ
    limg = cv2.merge((bright_l, a, b))
    enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # ៥. បម្លែងទៅជា Grayscale ដើម្បីទម្លាក់ពណ៌ផ្សេង និងទាញយកតែពណ៌បៃតងយោធា (Phosphor Green)
    gray = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)
    
    # បន្ថែម Contrast ឱ្យកាន់តែមុតស្រួច
    processed = cv2.convertScaleAbs(gray, alpha=2.2, beta=20)
    
    # ៦. បង្កើតបែបផែនពណ៌បៃតងយោធា (PVS-7 Style Night Vision)
    night_vision = cv2.merge((
        np.zeros_like(processed),  # Blue
        processed,                 # Green (ពន្លឺបៃតងកម្រិតខ្ពស់)
        np.zeros_like(processed)   # Red
    ))
    
    # ៧. បន្ថែមបែបផែន Digital Phosphor Grain (គ្រាប់អុចស្រាលៗលក្ខណៈអាជីព)
    noise = np.random.normal(0, 8, processed.shape).astype(np.uint8)
    night_vision = cv2.add(night_vision, cv2.merge((noise, noise, noise)))
    
    return night_vision

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # ដំណើរការតាមរយៈកូដ AI កម្រិតខ្ពស់
            processed_frame = advanced_ai_night_vision(frame)
            
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
