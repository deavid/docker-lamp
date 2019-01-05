from flask import Flask, render_template, request, url_for, redirect
from wtforms import Form, StringField, PasswordField, validators
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
        return redirect(url_for('login'))
    return render_template('login.html', form=form)
