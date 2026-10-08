"""분실물 목록, 등록, 상세 조회 라우트."""

from datetime import date
from math import ceil

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db
from .forms import CATEGORIES, ItemForm

bp = Blueprint("items", __name__)
PAGE_SIZE = 12


@bp.get("/")
def index():
    query = request.args.get("q", "").strip()[:100]
    category = request.args.get("category", "")
    page = request.args.get("page", 1, type=int)
    if page < 1 or (category and category not in CATEGORIES):
        abort(404)

    conditions, params = [], []
    if query:
        # 검색어의 %, _도 SQL 패턴이 아닌 실제 문자로 검색합니다.
        pattern = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        conditions.append(
            "(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\' "
            "OR found_location LIKE ? ESCAPE '\\')"
        )
        params.extend([pattern] * 3)
    if category:
        conditions.append("category = ?")
        params.append(category)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM items" + where, params).fetchone()[0]
    pages = max(1, ceil(total / PAGE_SIZE))
    if page > pages:
        abort(404)
    items = db.execute(
        "SELECT * FROM items" + where + " ORDER BY id DESC LIMIT ? OFFSET ?",
        [*params, PAGE_SIZE, (page - 1) * PAGE_SIZE],
    ).fetchall()
    return render_template(
        "items/index.html", items=items, query=query, category=category,
        categories=CATEGORIES, total=total, page=page, pages=pages,
    )


@bp.route("/items/new", methods=["GET", "POST"])
def create():
    form = ItemForm()
    if form.validate_on_submit():
        db = get_db()
        with db:
            cursor = db.execute(
                "INSERT INTO items "
                "(title, category, found_location, storage_location, found_date, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (form.title.data, form.category.data, form.found_location.data,
                 form.storage_location.data, form.found_date.data.isoformat(),
                 form.description.data or ""),
            )
        flash("분실물이 등록되었습니다.")
        return redirect(url_for("items.detail", item_id=cursor.lastrowid))
    status = 422 if request.method == "POST" else 200
    return render_template("items/create.html", form=form, today=date.today().isoformat()), status


@bp.get("/items/<int:item_id>")
def detail(item_id):
    item = get_db().execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        abort(404)
    return render_template("items/detail.html", item=item)
