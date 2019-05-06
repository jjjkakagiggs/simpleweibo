from threading import Thread

from flask import current_app,render_template
from flask_mail import Message
from simpleweibo.extensions import mail


def _send_async_mail(app,message):
    with app.app_context():
        mail.send(message)



def send_mail(to,subject,template,**kwargs):
    message = Message(current_app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject,recipients=[to])
    message.html = render_template(template, **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail,args=[app,message])
    thr.start()
    return thr