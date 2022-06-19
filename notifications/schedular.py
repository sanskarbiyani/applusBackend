from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .emailSender import EmailSenderQuaterly

def start():
    schedular = BackgroundScheduler()
    schedular.add_job(EmailSenderQuaterly, 'interval', hours=1)
    schedular.start()