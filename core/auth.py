from functools import wraps
from flask import session, redirect

def login_required(role=None):
    def wrapper(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/login")

            if role and session.get("role") != role:
                return redirect("/")

            return view(*args, **kwargs)
        return wrapped
    return wrapper
