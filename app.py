import os
import re
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


app = Flask(__name__)
app.secret_key = "gatelog-demo-secret-key"


# In-memory user store for the two login types.
RESIDENT_USERS = {
    "A101": {"password": "resident123", "name": "User A"},
    "B202": {"password": "welcome202", "name": "User B"},
    "C303": {"password": "guest303", "name": "User C"},
}

SECURITY_USERS = {
    "security 1": {"password": "gate123", "name": "Security 1"},
    "security 2": {"password": "gate234", "name": "Security 2"},
    "security 3": {"password": "gate345", "name": "Security 3"},
}


# In-memory guest register. Each guest entry is a dictionary.
guest_records = []
guest_id_counter = 1


NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s.'-]{1,49}$")
PHONE_PATTERN = re.compile(r"^\d{10}$")


def current_timestamp():
    """Return the current date-time in a user-friendly format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def current_date():
    """Return today's date for comparison and form defaults."""
    return datetime.now().strftime("%Y-%m-%d")


def get_status(guest):
    """Compute guest status from entry and exit timestamps."""
    if not guest.get("entry_time"):
        return "Not Arrived"
    if guest.get("entry_time") and not guest.get("exit_time"):
        return "Inside"
    return "Exited"


def login_required(role):
    """Protect routes so each dashboard is only visible to the right user type."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if session.get("user_role") != role:
                flash("Please log in to continue.", "error")
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def sort_guests_by_flat(guests):
    """Sort guest records by flat number, then visit date and guest name."""
    return sorted(
        guests,
        key=lambda guest: (
            guest.get("flat_number", ""),
            guest.get("visit_date", ""),
            guest.get("name", "").lower(),
        ),
    )


@app.context_processor
def inject_helpers():
    return {"today_date": current_date()}


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_type = request.form.get("login_type", "").strip()
        password = request.form.get("password", "").strip()

        if login_type == "resident":
            flat_number = request.form.get("flat_number", "").strip().upper()
            resident = RESIDENT_USERS.get(flat_number)

            if not flat_number or not password:
                flash("Flat number and password are required.", "error")
            elif not resident or resident["password"] != password:
                flash("Invalid resident credentials.", "error")
            else:
                session.clear()
                session["user_role"] = "resident"
                session["flat_number"] = flat_number
                session["display_name"] = resident["name"]
                return redirect(url_for("resident_dashboard"))

        elif login_type == "security":
            security_name = " ".join(
                request.form.get("security_name", "").strip().lower().split()
            )
            security_user = SECURITY_USERS.get(security_name)

            if not security_name or not password:
                flash("Security name and password are required.", "error")
            elif not security_user or security_user["password"] != password:
                flash("Invalid security credentials.", "error")
            else:
                session.clear()
                session["user_role"] = "security"
                session["username"] = security_name
                session["display_name"] = security_user["name"]
                return redirect(url_for("security_dashboard"))

        else:
            flash("Please choose a valid login type.", "error")

    return render_template("login.html")


@app.route("/resident")
@login_required("resident")
def resident_dashboard():
    flat_number = session.get("flat_number")
    resident_guests = sort_guests_by_flat([
        guest
        for guest in guest_records
        if guest["flat_number"] == flat_number
    ])
    return render_template(
        "resident.html",
        guests=resident_guests,
        flat_number=flat_number,
        resident_name=session.get("display_name"),
        get_status=get_status,
    )


@app.route("/resident/add", methods=["GET", "POST"])
@login_required("resident")
def add_guest():
    global guest_id_counter

    flat_number = session.get("flat_number", "")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        visit_date = request.form.get("visit_date", "").strip()
        submitted_flat = request.form.get("flat_number", flat_number).strip().upper()

        if not name:
            flash("Guest name is required.", "error")
        elif not NAME_PATTERN.fullmatch(name):
            flash("Guest name must be 2 to 50 characters and contain only letters.", "error")
        elif not phone:
            flash("Phone number is required.", "error")
        elif not PHONE_PATTERN.fullmatch(phone):
            flash("Phone number must be exactly 10 digits.", "error")
        elif not submitted_flat:
            flash("Flat number is required.", "error")
        elif not visit_date:
            flash("Visit date is required.", "error")
        else:
            guest_records.append(
                {
                    "id": guest_id_counter,
                    "name": name,
                    "phone": phone,
                    "flat_number": submitted_flat,
                    "visit_date": visit_date,
                    "entry_time": None,
                    "exit_time": None,
                    "created_at": current_timestamp(),
                }
            )
            guest_id_counter += 1
            flash("Guest added successfully.", "success")
            return redirect(url_for("resident_dashboard"))

    return render_template("add_guest.html", flat_number=flat_number)


@app.post("/resident/delete/<int:guest_id>")
@login_required("resident")
def delete_guest(guest_id):
    flat_number = session.get("flat_number")
    guest = next(
        (
            guest
            for guest in guest_records
            if guest["id"] == guest_id and guest["flat_number"] == flat_number
        ),
        None,
    )

    if guest:
        guest_records.remove(guest)
        flash("Guest deleted.", "success")
    else:
        flash("Guest not found.", "error")

    return redirect(url_for("resident_dashboard"))


@app.route("/security")
@login_required("security")
def security_dashboard():
    selected_flat = request.args.get("flat_number", "").strip().upper()
    search_query = request.args.get("search", "").strip().lower()
    guests = sort_guests_by_flat(guest_records)
    flat_numbers = sorted({guest.get("flat_number", "") for guest in guest_records if guest.get("flat_number")})

    if selected_flat:
        guests = [
            guest for guest in guests if guest.get("flat_number", "").upper() == selected_flat
        ]

    if search_query:
        guests = [
            guest
            for guest in guests
            if search_query in guest.get("name", "").lower()
            or search_query in guest.get("flat_number", "").lower()
            or search_query in guest.get("phone", "").lower()
            or search_query in guest.get("visit_date", "").lower()
            or search_query in get_status(guest).lower()
        ]

    return render_template(
        "security.html",
        guests=guests,
        get_status=get_status,
        flat_numbers=flat_numbers,
        selected_flat=selected_flat,
        search_query=search_query,
    )


@app.post("/security/entry/<int:guest_id>")
@login_required("security")
def mark_entry(guest_id):
    guest = next((guest for guest in guest_records if guest["id"] == guest_id), None)

    if not guest:
        flash("Guest not found.", "error")
    elif guest.get("entry_time"):
        flash("Entry already recorded.", "error")
    else:
        guest["entry_time"] = current_timestamp()
        flash("Entry time recorded.", "success")

    return redirect(url_for("security_dashboard"))


@app.post("/security/exit/<int:guest_id>")
@login_required("security")
def mark_exit(guest_id):
    guest = next((guest for guest in guest_records if guest["id"] == guest_id), None)

    if not guest:
        flash("Guest not found.", "error")
    elif not guest.get("entry_time"):
        flash("Entry must be recorded before exit.", "error")
    elif guest.get("exit_time"):
        flash("Exit already recorded.", "error")
    else:
        guest["exit_time"] = current_timestamp()
        flash("Exit time recorded.", "success")

    return redirect(url_for("security_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(debug=True, host=host, port=port)
