import requests
from flask import Flask, request, redirect, render_template as rd, make_response

from DataBase import DB
from GetLang import get_country
from NickDecoder import decode
from Cookie import *

app = Flask(__name__)

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = '832106045924966410'
CLIENT_SECRET = 'SECRET'
REDIRECT_URI = 'http://itsokay.ru:29793/con'


@app.route("/")
def index():
    db = DB()
    coded_nick = request.args.get("connection")

    if not coded_nick or coded_nick[-1] not in "abcdefghij":
        return rd("WrongLink.html")

    for s in coded_nick:
        if s not in "abcdefghijklmnopqrstuvwxyz1234567890_":
            return rd("WrongLink.html")

    nick = decode(coded_nick)
    db_user = db.select("minecraft", f"nick == '{nick}'")
    if not db_user:
        if db.select("moders", f"nick == '{nick}'"):
            return redirect("https://discord.com/api/oauth2/authorize?client_id=832106045924966410&redirect_uri=http%3A%2F%2Fitsokay.ru%3A29793%2Fcon&response_type=code&scope=identify&state=" + coded_nick)
        return rd("invalidPlayer.html")
    elif db_user["member"] and not db_user["new_ip"]:
        return rd("NotNeedAcceptation.html")
    elif request.cookies.get("con") and db_user["con"] and decode_cookie(db_user["con"]) == request.cookies.get("con")[0:-2]:
        db.update("minecraft", f"nick == '{nick}'", ip=request.environ['REMOTE_ADDR'], new_ip=None)
        return redirect("/log?connection=" + coded_nick)
    db.close()
    return redirect("https://discord.com/api/oauth2/authorize?client_id=832106045924966410&redirect_uri=http%3A%2F%2Fitsokay.ru%3A29793%2Fcon&response_type=code&scope=identify&state=" + coded_nick)


@app.route("/con")
def con():
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': request.args.get("code"),
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    token_json = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    token_json.raise_for_status()

    header = {'Content-Type': 'application/x-www-form-urlencoded',
              "Authorization": "Bearer " + token_json.json()["access_token"]}

    user_json = requests.get('%s/oauth2/@me' % API_ENDPOINT, headers=header)
    user_json.raise_for_status()
    user_id = user_json.json()['user']['id']

    coded_nick = request.args.get("state")
    nick = decode(coded_nick)
    ip = request.environ['REMOTE_ADDR']

    db = DB()
    if db.select("moders", f"nick == '{nick}'"):
        if db.select("minecraft", f"member == {user_id}", "moder")["moder"]:
            db.update("moders", f"nick == '{nick}'", join_accept=1, last_join=user_id)
            return redirect("/log?connection=" + coded_nick)
        else:
            return rd("BlockJoin.html")

    db_user = db.select("minecraft", f"nick == '{nick}'")
    db_ds = db.select("minecraft", f"member == {user_id}")
    if db_ds:
        if db_ds["nick"] != db_user["nick"]:
            return rd("AlreadyHaveDS.html")

    if str(db_user["member"]) == user_id:
        db.update("minecraft", f"nick == '{nick}'", ip=ip, new_ip=None)
        return redirect("/log?connection=" + coded_nick)

    db.update("minecraft", f"nick == '{nick}'", member=user_id, language=get_country(ip))
    db.close()

    return rd("RegistrationFinally.html", connection=coded_nick)


@app.route("/ds")
def discord():
    return redirect("https://discord.gg/kNjJTEwsbS")


@app.route("/donate")
def donate():
    return redirect("https://www.donationalerts.com/r/dendrivevlad")


@app.route("/log", methods=["POST", "GET"])
def log():
    try:
        coded_nick = request.args.get("connection")
        nick = decode(coded_nick)
    except:
        return rd("WrongLink.html")

    db = DB()

    if db.select("moders", f"nick == '{nick}'"):
        return rd("ModeratorConnected.html")

    ds = '' if db.select("minecraft", f"nick == '{nick}'", "on_ds")["on_ds"] else '<iframe class="ds" src="https://discord.com/widget?id=831144485319868417&theme=dark" width="350" height="500" allowtransparency="true" frameborder="0" sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"></iframe>'
    if request.method == "POST":
        res = ""
        match request.form["cookie"]:
            case "on":
                res = make_response(rd("Successful.html", cookie="off", check="✓", button_color="green", ds=ds, connection=coded_nick))
                cookie = create_cookie()
                res.set_cookie("con", cookie[0], 9999999999)
                db.update("minecraft", f"nick == '{nick}'", con=cookie[-1])
            case "off":
                res = make_response(rd("Successful.html", cookie="on", check="🔲", button_color="gray", ds=ds, connection=coded_nick))
                res.set_cookie("con", "", 0)
                db.update("minecraft", f"nick == '{nick}'", con=None)
        db.close()
        return res
    db.close()
    if request.cookies.get("con"):
        return rd("Successful.html", cookie="off", check="✓", button_color="green", ds=ds, connection=coded_nick)
    else:
        return rd("Successful.html", cookie="on", check="🔲", button_color="gray", ds=ds, connection=coded_nick)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=29793)
