from flask import Blueprint, render_template, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.report_service import ReportService
from functools import wraps

report_bp = Blueprint("report", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── N1-10: Thống kê & Báo cáo ─────────────────────────────────────────
@report_bp.route("/reports")
@login_required
def index():
    db = SessionLocal()
    try:
        summary = ReportService(db).get_summary()
    finally:
        db.close()
    return render_template("reports/index.html", summary=summary)
