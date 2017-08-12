from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
import os
from dao import DbConnect
from searchform import SearchForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
bootstrap = Bootstrap(app)


#Route - the association between a URL and function that handles it
@app.route('/')
def index():
    form = SearchForm()
    db = DbConnect()
    form.org.choices = db.get_orgs()
    return render_template('index.html', form=form)


@app.route('/get_server_data',  methods=['GET','POST'])
def get_server_data():
    form = request.form
    print(form["start_date"])
    db = DbConnect()
    result = db.search_db(form)
    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
