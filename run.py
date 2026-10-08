"""로컬 개발 서버 실행: python run.py"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
