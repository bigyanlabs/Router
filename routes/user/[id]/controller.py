from flask import render_template, request
from typing import Any

def handler(request: Any) -> Any:
    user_id: str = request.view_args.get("id", "Unknown")
    return render_template("page.html", title=f"User {user_id}")
