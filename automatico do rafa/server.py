import configparser
from flask import Flask, render_template, \
    request, redirect, url_for, flash, jsonify
from controllers import UserController
from core.webhooks import eduzz, braip, hotmart, kiwify

config = configparser.ConfigParser()
config.read('settings/config.ini', encoding="utf-8")

hook_status = config.get("webhook", "status")

if hook_status == "enable":
    hook = config.get("webhook", "engine")
    if hook == "eduzz":
        payment_hook = eduzz
    elif hook == "braip":
        payment_hook = braip
    elif hook == "hotmart":
        payment_hook = hotmart
    elif hook == "kiwify":
        payment_hook = kiwify

app = Flask(__name__)
users = UserController()

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
app.config['WTF_CSRF_CHECK_DEFAULT'] = False


@app.route("/")
@app.route("/index")
def index():
    data = users.read()
    if data:
        return render_template("index.html", datas=data)
    return jsonify({"result": False, "object": [], "message": "Nenhum usuário cadastrado!!!"})


@app.route("/api/v1/payment/hook", methods=['POST'])
def web_hook():
    response_dict = {k: v for k, v in request.form.items()}
    payment_hook.get_payment(response_dict, users)
    return jsonify({"result": True, "object": [], "message": "Operação realizada com sucesso!!!"})


@app.route("/delete_user/<string:uid>", methods=['GET'])
def delete_user(uid):
    users.delete(uid)
    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for("index"))


@app.route("/change_status_user", methods=['GET'])
def change_status_user():
    response_dict = request.args.to_dict()
    users.change_token_status(response_dict.get("uid"), response_dict.get("days"))
    flash('Operação realizada com sucesso!', 'success')
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
