from src import app

@app.route('/')
def hello():
    return "hello"