from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="..")
CORS(app)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

PROMPTS = {
    "boss": """คุณคือ BOSS ผู้จัดการทีม Content Creator
รับโจทย์แล้วสรุปสั้นๆ ว่าจะสั่งงานทีม IDEA, RES, CAP อย่างไร ตอบเป็นภาษาไทย""",
    "idea": """คุณคือ IDEA นักคิด Content Creator
คิด: 1.แนวคิด 3 แบบพร้อม angle 2.กลุ่มเป้าหมาย 3.Hook เปิดคลิป 3 ตัวเลือก ตอบภาษาไทย""",
    "res": """คุณคือ RES นักวิจัยข้อมูล
หา: 1.เทรนด์ปัจจุบัน 2.ข้อมูล/สถิติน่าสนใจ 5 ข้อ 3.โอกาสที่ยังไม่มีใครทำ ตอบภาษาไทย""",
    "cap": """คุณคือ CAP ผู้เชี่ยวชาญ SEO YouTube สร้าง:
[ชื่อคลิป] ไทย 3 ตัวเลือก / อังกฤษ 3 ตัวเลือก
[คำอธิบาย] ไทย 150 คำ / อังกฤษ 150 คำ
[Tags] ไทย 15 อัน / อังกฤษ 15 อัน
[Comment ปักหมุด] ไทย / อังกฤษ"""
}

def call_gemini(system_prompt, task):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=task
    )
    return response.text

@app.route("/")
def home():
    return send_from_directory("..", "index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    topic = data.get("topic", "")
    agent = data.get("agent", "boss")
    context = data.get("context", "")

    if not topic:
        return jsonify({"error": "กรุณาใส่โจทย์"}), 400

    task = f"โจทย์: {topic}"
    if context:
        task += f"\n\nบริบทเพิ่มเติม:\n{context}"

    result = call_gemini(PROMPTS[agent], task)
    return jsonify({"result": result})
