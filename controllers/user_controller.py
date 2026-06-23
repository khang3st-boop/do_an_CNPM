from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from controllers.auth_controller import login_required
from models.user import User
from repositories import user_repository
from services.auth_service import hash_password


user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if user_repository.get_by_email(g.db, email):
            flash("Email đã tồn tại.", "danger")
            return redirect(url_for("users.index"))

        user_repository.create(
            g.db,
            User(
                full_name=request.form.get("full_name", "").strip(),
                email=email,
                password_hash=hash_password(request.form.get("password", "123456")),
                role=request.form.get("role", "staff"),
                phone=request.form.get("phone", "").strip() or None,
                status="active",
            ),
        )
        flash("Tạo tài khoản nhân viên thành công.", "success")
        return redirect(url_for("users.index"))

    users = user_repository.get_all(g.db)
    return render_template("users.html", users=users)


@user_bp.route("/<int:user_id>/toggle-status", methods=["POST"])
@login_required
def toggle_status(user_id):
    user = user_repository.get_by_id(g.db, user_id)

    if not user:
        flash("Không tìm thấy tài khoản.", "danger")
        return redirect(url_for("users.index"))

    user_repository.toggle_status(g.db, user)
    flash("Cập nhật trạng thái tài khoản thành công.", "success")
    return redirect(url_for("users.index"))

