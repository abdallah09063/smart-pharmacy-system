from app import create_app, db
import app.models

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)