"""Flask 애플리케이션 팩토리."""

import os
import secrets
from pathlib import Path

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=str(Path(app.instance_path) / "lost_and_found.sqlite3"),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    csrf.init_app(app)

    from . import db
    from .routes import bp

    db.init_app(app)
    app.register_blueprint(bp)

    # 처음 실행할 때 테이블만 생성하며, 기존 데이터는 유지합니다.
    with app.app_context():
        db.init_db()

    @app.errorhandler(404)
    def not_found(error):
        return render_template(
            "error.html", code=404, message="요청한 페이지나 분실물을 찾을 수 없습니다."
        ), 404

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template(
            "error.html", code=400,
            message="등록 화면을 새로 열고 다시 제출해 주세요. 보안 토큰이 만료되었거나 올바르지 않습니다.",
        ), 400

    @app.errorhandler(413)
    def request_too_large(error):
        return render_template(
            "error.html", code=413, message="입력 내용이 너무 큽니다. 내용을 줄여 주세요."
        ), 413

    return app
