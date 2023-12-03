from flask import Flask, render_template, request, redirect, url_for, make_response, flash, send_from_directory
import sys, os

MESSAGES = []
MESSAGE_NUMBERS = []
RECIEVED_MESSAGES = []

try:
    port = sys.argv[1]
except IndexError:
    port = '5000'

app = Flask(__name__)
app.secret_key = b'70e0f8490bdd09f98a6bb365477bec68'

@app.route('/', methods=['GET'])
def host():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def info():
    name = request.cookies.get(f'name_{port}', default=port, type=str)
    delay = request.cookies.get('delay', default='800', type=str)
    impulse = request.cookies.get('impulse', default='35', type=str)
    if len(MESSAGES) > 0:
        msg = MESSAGES.pop(0)
        RECIEVED_MESSAGES.append(msg)
        return {
            "ok": True,
            "message": msg
        }
    return {"ok": False}

@app.route('/send', methods=['GET', 'POST'])
def send():
    context = {
        "name": request.cookies.get(f'name_{port}', default=port, type=str),
        "delay": request.cookies.get('delay', default=800, type=int),
        "impulse": request.cookies.get('impulse', default=35, type=int),
    }
    if request.method == 'POST':
        print(request.form)
        message = []
        message.append(int(context['impulse']*0.75))
        message.append(context['delay']*2)

        #QN START
        qn = request.form.get('qn', default=None, type=int)
        if qn is None:
            context.update({'qn': 0})
            flash("No question number has picked", 'warning')
            flash("Question number has set to 0", 'info')
            return render_template('send.html', **context)
        context.update({'qn': qn+1})
        MESSAGE_NUMBERS.append(qn)
        message += [int(context['impulse']*0.97)]
        if qn == 0:
            message += [int(context['delay']/4), int(context['impulse']*0.97), int(context['delay']/4), int(context['impulse']*0.97), int(context['delay']*2)]
        elif qn % 2 == 0:
            message += [int(context['delay']/4), int(context['impulse']*0.97), int(context['delay']*2)]
        else:
            message += [int(context['delay']*2)]
        message += []
        #QN END
        letter_message = []
        letter = request.form.get('letter', default=None, type=str)
        if letter is None:
            flash("No letter picked", 'error')
            del context['qn']
            return render_template('send.html', **context)
        if letter == 'A':
            imps = [context['impulse']] * 1
            letter_message += imps
        elif letter == 'B':
            imps = [context['impulse']] * 2
            print(f"imps: {imps}")
            letter_message += imps
        elif letter == 'C':
            imps = [context['impulse']] * 3
            letter_message += imps
        elif letter == 'D':
            imps = [context['impulse']] * 4
            letter_message += imps
        elif letter == 'E':
            imps = [context['impulse']] * 5
            letter_message += imps

        msg = letter_message
        for i in range(1, len(msg)*2, 2):
            msg.insert(i, context['delay'])
        #msg = [val for sublist in zip(letter_message, [context['delay']] * (len(letter_message) - 1)) for val in sublist]
        print(f"msg: {msg}")
        message += msg
        MESSAGES.append(message)
        flash(f"Sent!", 'success')

        try:
            if len(RECIEVED_MESSAGES) > 0:
                msg = RECIEVED_MESSAGES.pop(0)
                if len(MESSAGE_NUMBERS) > 0 and msg:
                    rmn = MESSAGE_NUMBERS.pop(0)
                    flash(f"Reciever got #{rmn}", 'success')
        except:
            ...
        return render_template('send.html', **context)
    else:
        ...
        # return redirect(url_for('send'))
    return render_template('send.html', **context)

@app.route('/rename', methods=['GET', 'POST'])
def rename():
    name = request.cookies.get(f'name_{port}', default=port, type=str)
    resp = make_response(render_template('rename.html', name=name))
    if request.method == 'POST':
        resp = make_response(redirect(url_for('send')))
        resp.set_cookie(f'name_{port}', request.form.get(f'name', default=port, type=str))
    return resp

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    name = request.cookies.get(f'name_{port}', default=port, type=str)
    delay = request.cookies.get('delay', default='800', type=str)
    impulse = request.cookies.get('impulse', default='35', type=str)
    resp = make_response(render_template('settings.html', name=name, delay=delay, impulse=impulse))
    if request.method == 'POST':
        resp = make_response(redirect(url_for('send')))
        resp.set_cookie('delay', request.form.get('delay', default='800', type=str))
        resp.set_cookie('impulse', request.form.get('impulse', default='35', type=str))
    return resp

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(port))
