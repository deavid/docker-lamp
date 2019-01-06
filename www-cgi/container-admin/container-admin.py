import os
import os.path
import sys
import logging
import crypt
import yaml
import datetime
import dateutil.parser
from hmac import compare_digest
from flask import Flask, render_template, request, url_for, redirect, session
from wtforms import Form, StringField, PasswordField, validators
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(name)s:%(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

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


__containers_db, __containers_db_stamp = None, None


def get_containers():
    global __containers_db
    global __containers_db_stamp
    filename = os.path.join(curpath, "containers.yml")
    new_stamp = os.stat(filename).st_mtime
    if new_stamp != __containers_db_stamp:
        with open(filename, 'r') as stream:
            __containers_db = yaml.load(stream)
            __containers_db_stamp = new_stamp
    return __containers_db


@app.route("/")
def home():
    user = get_user() or {}
    return render_template('home.html', environ=repr(request.environ), **user)


@app.route("/login/", methods=['GET', 'POST'])
def login():
    user = get_user()
    if user:
        return redirect(url_for('admin'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        # token = form.token.data
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
            session.clear()
            session["email"] = email
            session["containers"] = user_db[email]["containers"]
            valid_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
            # Extra data for increased secuirity on later validation
            session["valid_until"] = valid_until.isoformat()
            session["user_agent"] = request.user_agent.string
            session["remote_addr"] = request.environ['REMOTE_ADDR']
            return redirect(url_for('admin'))
    return render_template('login.html', form=form)


def get_user():
    logger = logging.getLogger("auth")
    try:
        email = session["email"]
        containers = session["containers"]
        valid_until = session["valid_until"]
        user_agent = session["user_agent"]
        remote_addr = session["remote_addr"]
    except KeyError:
        logger.exception("Error retrieving session keys; probably old cookie")
        return None
    if user_agent != request.user_agent.string:
        logger.warn("User agent did not match: (cookie) %s != (request) %s", user_agent, request.user_agent.string)
        return None
    if remote_addr != request.environ['REMOTE_ADDR']:
        logger.warn("Request IP did not match: (cookie) %s != (request) %s", remote_addr, request.environ['REMOTE_ADDR'])
        return None
    valid_until = dateutil.parser.parse(valid_until)
    now = datetime.datetime.now(datetime.timezone.utc)
    # The following condition is "double-reversed" to ensure that errors from types, NaN, etc, get catched as well
    if not (valid_until > now):
        logger.info("Cookie expired: (cookie) %s >= (now) %s", valid_until, now)
        return None
    expire_in_min = (valid_until - now).total_seconds() // 60
    return {
        "email": email,
        "available_containers": containers,
        "expire_in_min": expire_in_min
    }


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route("/admin")
@app.route("/admin/<container>")
def admin(container=None):
    user = get_user()
    if user is None:
        return redirect(url_for('login'))
    if container is not None and container not in user["available_containers"]:
        return redirect(url_for('admin'))
    containers = get_containers()
    return render_template(
        'admin.html',
        active_container=container,
        containers=containers,
        **user
        )
