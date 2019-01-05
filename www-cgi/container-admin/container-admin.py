import os
import os.path
import sys
import crypt
import yaml
import datetime
from hmac import compare_digest
from flask import Flask, render_template, request, url_for, redirect, session
from wtforms import Form, StringField, PasswordField, validators

curpath = os.path.abspath(os.path.dirname(sys.argv[0]))
app = Flask(__name__)
# you can use "mkpasswd -m sha512crypt" and ramble a lot of random keystrokes.
# Any other random string will work too, as using /dev/urandom or python -c 'import os; print(os.urandom(32))'
# keep this secret! (we could use a docker volume to hide it and make it different in each machine)
app.secret_key = b'3nSuMjAMJzayoqUe0RZA8TvcrfFP9Aw5xzIw8rqhqOtEI47PJbeAz5Ciyccpm/q0954NIX22kIpX7FUIRvvP7rYYDg'


class LoginForm(Form):
    email = StringField(
        'Email Address',
        [validators.Length(min=6, max=35)],
        render_kw={"placeholder": "Your Email"}
        )
    token = StringField(
        'Token',
        [validators.Length(min=4, max=8)],
        render_kw={"placeholder": "Your Token from your mobile device"}
        )
    password = PasswordField(
        'Password',
        [validators.Length(min=6, max=35)],
        render_kw={"placeholder": "Your Password"}
        )


@app.route("/")
def hello():
    return render_template('home.html', environ=repr(request.environ))


@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        token = form.token.data
        password = form.password.data
        with open(os.path.join(curpath, "users.yml"), 'r') as stream:
            user_db = yaml.load(stream)
        if email not in user_db:
            # Stupid password to test against and waste the same CPU to prevent time attacks
            cryptedpasswd = "$5$6g1mugAfO$Gx6JnJPw6meK5ftNWGGrOpGamXwK/mc1vHlaeTEirf6"
            compare_digest(crypt.crypt("1231231231232", cryptedpasswd), cryptedpasswd)
            is_valid = False
        else:
            user = user_db[email]
            cryptedpasswd = user["password"]
            is_valid = compare_digest(crypt.crypt(password, cryptedpasswd), cryptedpasswd)
        if not is_valid:
            form.password.errors.append('The username or password is not valid')
        if is_valid:
            session["data"] = user_db[email]
            valid_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
            # Extra data for increased secuirity on later validation
            session["valid_until"] = valid_until.isoformat()
            session["user_agent"] = request.user_agent.string
            session["remote_addr"] = request.environ['REMOTE_ADDR']
            return redirect(url_for('admin'))
    return render_template('login.html', form=form)


@app.route("/admin")
def admin():
    return render_template('app.html', session=yaml.dump(session._get_current_object()))
