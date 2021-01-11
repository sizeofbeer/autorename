import os
from apps import db, migrate, create_app
from apps.ocr.models import (
    ClientBaseConfigure,
    UserInfor,
    PicInfor,
    PdfInfor,
)


env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app('config.%sConfig' % env.capitalize())


@app.shell_context_processor
def make_shell_context():
    return dict(
        app=app,
        db=db,
        ClientConfig=ClientBaseConfigure,
        User=UserInfor,
        PicInfor=PicInfor,
        PdfInfor=PdfInfor,
        migrate=migrate,
    )