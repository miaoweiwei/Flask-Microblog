from flask import Flask

app = Flask(__name__)
print("app.py服务启动了")


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    print("app.py服务启动了")
    app.run()
