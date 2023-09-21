
from application import app

@app.get('/')
def index():
    return '<h1>Main menu<h1>'

if __name__ == '__main__':
    app.run()