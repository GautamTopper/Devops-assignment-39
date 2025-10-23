from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "citytickets-secretkey"

events = [
    {"id": 1, "name": "Coldplay Live", "venue": "Mumbai Arena", "time": "7:30 PM", "price": 1200},
    {"id": 2, "name": "Arijit Singh Concert", "venue": "Delhi Dome", "time": "8:00 PM", "price": 950},
    {"id": 3, "name": "Stand-up Night", "venue": "Chennai Club", "time": "6:00 PM", "price": 500}
]

reservations = []

@app.route('/')
def home():
    return render_template("home.html", events=events)

@app.route('/reserve/<int:event_id>', methods=['GET', 'POST'])
def reserve(event_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        flash("Event not found!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        user = request.form.get("user")
        email = request.form.get("email")
        seats = request.form.get("seats")
        date = request.form.get("date")

        if not all([user, email, seats, date]):
            flash("All fields are required!", "danger")
            return redirect(url_for("reserve", event_id=event_id))

        try:
            seats = int(seats)
            if seats <= 0 or seats > 6:
                raise ValueError
        except ValueError:
            flash("Seats must be between 1 and 6", "danger")
            return redirect(url_for("reserve", event_id=event_id))

        total = seats * event["price"]
        ref_code = f"CT-{uuid.uuid4().hex[:8].upper()}"
        booking = {
            "ref": ref_code,
            "user": user,
            "email": email,
            "event": event["name"],
            "venue": event["venue"],
            "date": date,
            "time": event["time"],
            "seats": seats,
            "total": total
        }
        reservations.append(booking)
        return render_template("confirmation.html", booking=booking)

    return render_template("reserve.html", event=event)

@app.route('/reservations')
def view_reservations():
    return render_template("reservations.html", reservations=reservations)

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/health')
def health():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
