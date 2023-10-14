from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from __init__ import create_app, db
from models import names, event_scan, event

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('login.html')

@main.route('/info', methods=['GET', 'POST'])
@login_required
def Info():
    try:
        with current_app.app_context():
            events = event_scan.query.all()
        return render_template('info.html', events=events)
    except Exception as e:
        # Handle the exception, log it, or return an error response.
        return str(e), 500

@main.route('/event-scanner', methods=['GET', 'POST'])
@login_required
def eventValidation():
    try:
        if request.is_json:
            result = request.args.get('scan')
            with current_app.app_context():
                guest = db.session.query(names).filter_by(uid=result).first()
                if guest is None:
                    alert = "No Record found!"
                else:
                    if guest.flag == '0':
                        alert = "Welcome"
                        new_scan = event_scan(code=guest.code)
                        db.session.add(new_scan)
                        db.session.query(names).filter_by(uid=result).update({"flag": 1})
                    else:
                        alert = "PASS Expired! - (Day)"
                db.session.commit()
            return jsonify({"alert": alert})
        return render_template('events.html')
    except Exception as e:
        # Handle the exception, log it, or return an error response.
        db.session.rollback()
        return str(e), 500
@main.route('/gate-2', methods=['GET', 'POST'])
@login_required
def eventVerification():
    try:
        if request.is_json:
            result = request.args.get('scan')
            with current_app.app_context():
                guest = db.session.query(names).filter_by(uid=result).first()
                if guest is None:
                    alert = "No Record!"
                else:
                    if guest.flag == "2":
                        alert = "Already Verified!"
                    if guest.flag == "1":
                        db.session.query(names).filter_by(uid=result).update({"flag": 2})
                        alert = "Verified!"
                    else:
                        alert = "Invalid or First Scan Remaining!"    
                db.session.commit()
            return jsonify({"alert": alert})
        return render_template('events-gate2.html')
    except Exception as e:
        # Handle the exception, log it, or return an error response.
        db.session.rollback()
        return str(e), 500
@main.route('/event', methods=['GET', 'POST'])
@login_required
def Event():
    try:
        if request.method == 'GET':
            return render_template('event-gen.html')
        else:
            evName = request.form.get('name')
            date = request.form.get('date')
            time = request.form.get('time')
            with current_app.app_context():
                new_event = event(name=evName, event_date=date, event_time=time)
                db.session.add(new_event)
                db.session.query(names).filter_by(flag='1').update({"flag": 0})
                db.session.query(names).filter_by(flag='2').update({"flag": 0})
                db.session.commit()
            return render_template("event-gen.html")
    except Exception as e:
        # Handle the exception, log it, or return an error response.
        db.session.rollback()  # Rollback the transaction in case of an error
        return str(e), 500

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
