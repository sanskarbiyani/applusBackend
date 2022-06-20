from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .emailSender import EmailSenderQuaterly

def start():
    schedular = BackgroundScheduler()
    schedular.add_job(EmailSenderQuaterly, 'interval', minutes=20)
    schedular.start()