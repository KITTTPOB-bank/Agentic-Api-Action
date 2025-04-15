AGENTIC AI หาข้อมูลหุ้น กองทุน คุยเศรษฐกิจ

```
python -m venv project-Api
```
```
project-Api\Scripts\activate
```
```
pip install -r .\requirements.txt
```
```
uvicorn main:app --host=0.0.0.0 --port=8000                                                                                                                                 
```

สร้างไฟล์ .env 
```
GEMINI_KEY = "" ถ้าไม่ใช้ เป็น "" ก็พอคับ กรณีทำรูปภาพมีม ตรง `meme` ในส่วน api
GPT_KEY = ""
NEWS_API_KEY = "" สร้างที่ https://newsapi.org/
```

เข้าไปที่ http://localhost:8000/docs
```
จะมีตัวอย่างการถาม มี 2 role human กับ ai สำหรับ message conversions
```
