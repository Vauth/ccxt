from flask import Flask, render_template, request, jsonify
from helper.checker import Stripe

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_card', methods=['POST'])
def check_card():
    card_number = request.json['card_number']
    check = Stripe.Checker(card_number)

    if "didn't confirmed" in check: is_valid = True; is_charged = False
    elif "confirmed" in check: is_valid = True; is_charged = True
    else: is_valid = False; is_charged = False

    return jsonify({
        'answer': card_number + ": " + check['response'] if type(check) == dict else check,
        'valid': is_valid, 'charged': is_charged, 'authed': True
    })

if __name__ == '__main__':
    app.run(debug=True)

