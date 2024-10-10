from flask import Flask, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessary for flash messages

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/show_message', methods=['POST'])
def show_message():
    flash("Hello World!")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
