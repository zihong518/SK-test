from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import DB_NAME, DB, DICT_COLLECTION, REVIEW_COLLECTION, ARTICLE_COLLECTION

app = Flask(__name__)


@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html')


@app.route('/dict')
def test():
    print(DICT_COLLECTION)
    return (DICT_COLLECTION)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
