from flask import Flask, render_template, redirect, request, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
import smtplib
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

my_mail = 'kashipawar1806@gmail.com'
password = "zzkpnekqpnzvdnic"

#contact from data
class ContactForm(FlaskForm):
    name = StringField(label="name", validators=[])
    contact = StringField(label="Contact Number")
    age = StringField(label="Age")
    gender = StringField(label="Gender")
    address = StringField(label="Address")
    submit = SubmitField(label="Submit Form")

app = Flask(__name__)
app.secret_key = "Your Secret Key"
# database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#initializing login manager
login_manager = LoginManager()
login_manager.init_app(app)

#to get return object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#class for database table
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    package = db.Column(db.String(250), nullable=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")

@app.route('/contact', methods=['POST','GET'])
def book_appointment():
    contact_form = ContactForm()

    if request.method == 'POST':
        #getting data from contact form
        name = request.form['name'].title()
        contact = request.form['contact']
        age = request.form['age']
        gender = request.form['gender'].title()
        address = request.form['address'].title()

        #code for sending mails
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=my_mail, password=password)
                connection.sendmail(
                from_addr=my_mail,
                to_addrs=my_mail,
                msg=f"Subject:{name} wants to book appointment.\n\nName: {name}, {age}, {gender}\nContact:{contact}\nAddress: {address}"
                        )
        print(name, address, gender, age, contact)
        new_appointment = Appointment(
            name=name,
            age=age,
            gender=gender,
            contact=contact,
            address=address
        )
        db.session.add(new_appointment)
        db.session.commit()
        return render_template("notify.html")
    return render_template("contact.html", form=contact_form)

@app.route('/register', methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("This email already exist!!! try log in.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password=password,
                                                 method='pbkdf2:sha256',
                                                 salt_length=8
                                                 )
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # checking if email exist or not in database
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email does not exist! please try again.")
            return redirect(url_for('login'))

        # checkinng for password
        elif not check_password_hash(user.password, password):
            flash("Incorrect password!! try again.")
            return redirect(url_for('login'))

        else:
            login_user(user)
            all_data = db.session.query(Appointment).all()
            return render_template("appointments.html", data=all_data)
    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route("/logout")
def logout():
    logout_user()
    return render_template("login.html")



@login_required
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    print("id: ",  id)
    all_data = db.session.query(Appointment).all()
    show = True

    if request.method == "POST":
        update_data = Appointment.query.get(id)
        update_data.package = request.form['update_package'].title()
        db.session.commit()
        show = False
        return render_template("appointments.html", data=all_data, show=show)
    return render_template("appointments.html", data=all_data, show=show,  uid=id)


@app.route('/delete')
@login_required
def delete():
    id = int(request.args.get('id'))
    print(id)
    appointment_data = db.session.query(Appointment).filter_by(id=id).first()
    print(appointment_data)
    db.session.delete(appointment_data)
    db.session.commit()
    all_data = db.session.query(Appointment).all()
    show = False
    return render_template("appointments.html", data=all_data, show=show,)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    all_data = db.session.query(Appointment).all()
    if request.method == "POST":
        name = request.form["search"].title()
        search = db.session.query(Appointment).filter_by(name=name)
        return render_template("appointments.html", data=search)
    return render_template("appointments.html",  data=all_data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
