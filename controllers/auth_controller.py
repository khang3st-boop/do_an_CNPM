from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from services.auth_service import authenticate


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@auth_bp.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = authenticate(g.db, email, password)

        if not user:
            flash("Email hoặc mật khẩu không đúng, hoặc tài khoản đã bị khóa.", "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.full_name
        session["user_role"] = user.role
        flash("Đăng nhập thành công.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất khỏi hệ thống.", "success")
    return redirect(url_for("auth.login"))

