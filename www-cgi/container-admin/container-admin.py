import os
import os.path
import sys
import crypt
import yaml
from hmac import compare_digest
from flask import Flask, render_template, request, url_for, redirect
from wtforms import Form, StringField, PasswordField, validators

curpath = os.path.abspath(os.path.dirname(sys.argv[0]))
app = Flask(__name__)


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
    return render_template('home.html')


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
            return redirect(url_for('login'))
    return render_template('login.html', form=form)
