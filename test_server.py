from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
cal_id="certl@umass.edu"

if __name__ == '__main__':
    app.run('0.0.0.0',port=8088)
