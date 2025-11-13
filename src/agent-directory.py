from app import app, db
from app.models import Application


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Application': Application}
