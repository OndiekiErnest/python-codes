from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    IP = request.remote_addr
    return '<h1>Hello World!</h1> <p>Your Browser is {} and IP is {}</p>'.format(user_agent, IP)


if __name__ == "__main__":
    app.run(debug=True)
