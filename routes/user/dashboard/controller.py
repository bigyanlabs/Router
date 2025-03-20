from flask import render_template
from typing import Any

def handler(_) -> Any:
    return render_template("page.html", title="User Dashboard")
