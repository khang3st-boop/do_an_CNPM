from flask import Blueprint, g, render_template

from controllers.auth_controller import login_required
from services.dashboard_service import get_dashboard_stats


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("")
@login_required
def index():
    stats = get_dashboard_stats(g.db)
    return render_template("dashboard.html", stats=stats)

