from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return {'hello': 'world'}


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
