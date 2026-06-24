from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("reminder.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = SessionLocal()
        try:
            service = AuthService(db)
            user = service.login(username, password)
            if user:
                session["user_id"]   = user.UserID
                session["username"]  = user.Username
                session["role"]      = user.Role
                session["department"] = getattr(user, "Department", "general")
                flash("Đăng nhập thành công!", "success")
                return redirect(url_for("reminder.dashboard"))
            else:
                flash("Tên đăng nhập hoặc mật khẩu không đúng.", "danger")
        finally:
            db.close()

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))
