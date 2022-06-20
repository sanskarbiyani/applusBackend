from sys import intern
from attr import field

from dynamic_models.models import FieldSchema
from .models import TrackTime
from datetime import datetime, timedelta
from django.apps import apps
import json
from django.db.models import Q
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

def getQuerySet(interval, field, notified, listModel, type, candidate):
    filter4 = {f'{type}': interval}
    require_datetime = datetime.now() + timedelta(**filter4) - timedelta(hours=5, minutes=30)
    print(f"Require Time: {require_datetime}")
    filter1 = {field:None}
    filter2 = {f'{field}__lte': require_datetime}
    filter3 = {f'{field}__gt': datetime.now() - timedelta(hours=5, minutes=30)}
    notifications = list(listModel.objects.filter(~Q(**filter1) & Q(**filter2) & Q(**filter3)).values(field, notified, candidate))
    return notifications

def filterAndSendMails(results, obj, field, notified, candidate):
    for result in results:
        send_emails(time=result[field], interviewers=result[notified], candidate=result[candidate])
        # if obj.last_email_sent == None:
        #     print("Sending the first email for the table.")
        #     newEmailSent = {
        #         candidate: datetime.now()
        #     }
        #     obj.last_email_sent = json.dumps(newEmailSent, default=str)
        #     obj.save()
        # elif candidate in obj.last_email_sent:
        #     # print(obj.last_email_sent)
        #     # obj[candidate] = datetime.now()
        #     # print(obj)
        #     # result.last_email_sent = json.dumps(obj, default=str)
        #     # result.save()
        #     send_emails(time=result[field], candidate=candidate, interviewers=result[notified])
        # else:
        #     newObj = json.loads(obj.last_email_sent)
        #     newObj[candidate] = datetime.now()
        #     obj.last_email_sent = json.dumps(newObj, default=str)
        #     obj.save()
        #     send_emails(time=result[field], candidate=candidate, interviewers=result[notified])


def EmailSenderQuaterly():
    print("Starting to send emails..")
    print(f"Current DateTime: {datetime.now()}")
    try:
        results = list(TrackTime.objects.all())
    except ObjectDoesNotExist:
        print("Object Does Not Exists.")
        return
    if not results or len(results) == 0:
        print("No Objects Found.")
        return
    for result in results:
        print("Results are: ");
        print(result.candidate_field_name.id);
        listModel = apps.get_model(app_label=str('ddmapp'), model_name=result.list_name.name)
        field_name = result.time_field_name.name.lower().replace(' ', '_')
        notified_name = result.interviewer_field_name.name.lower().replace(' ', '_')
        candidate_field = result.candidate_field_name.name.lower().replace(' ', '_')
        notifications = getQuerySet(interval=20 , type="minutes", field=field_name, notified=notified_name, listModel=listModel, candidate=candidate_field)
        filterAndSendMails(notifications, result, field_name, notified_name, candidate=candidate_field)
        # for notification in notifications:
        #     print(notification)
        
        


def send_emails(**kwargs):
    print(f"Og Time: {kwargs['time'].strftime('%H:%M:%S')}")
    time = kwargs["time"] + timedelta(hours=5, minutes=30)
    interviewers = kwargs['interviewers']
    candidate = kwargs['candidate']
    for interviewer in interviewers:
        # print(interviewer)
        # print(time.strftime("%H:%M:%S"))
        email_body = f'Hello {interviewer["user_name"]}, \nYou have an interview scheduled with { candidate } at {time.strftime("%H:%M:%S")}'
        print(email_body)
        send_mail(
            'Interview Scheduled',
            email_body,
            'Kshitija.Supekar.external@idiada.com',
            [interviewer['email']], # Can we wrong.
        )

# require_datetime = datetime.now() + timedelta(minutes=15) - timedelta(hours=5, minutes=30)
# print(f"Require Time: {require_datetime}")
# filter1 = {field_name:None}
# filter2 = {f'{field_name}__lte': require_datetime}
# filter3 = {f'{field_name}__gt': datetime.now() - timedelta(hours=5, minutes=30)}
# notifications = list(listModel.objects.filter(~Q(**filter1) & Q(**filter2) & Q(**filter3)).values(field_name, notified_name, 'candidate_name'))
# print(notifications)


# for notification in notifications:
#     candidate = notification['candidate_name']
#     print(f"For {candidate}")
#     if (result.last_email_sent == None):
#         obj = {
#             candidate: datetime.now()
#         }
#         print(obj)
#         result.last_email_sent = json.dumps(obj, default=str)
#         result.save()
#     obj = json.loads(result.last_email_sent)
#     # print(datetime.strptime(obj[candidate], "%Y-%m-%d %H:%M:%S.%f"))

#     if not candidate in obj:
#         obj[candidate] = datetime.now() - timedelta(hours=5, minutes=30)
#         print(obj)
#         result.last_email_sent = json.dumps(obj, default=str)
#         result.save()
#         send_emails(time=notification[field_name], candidate=candidate, interviewers=notification[notified_name])
#     print(type(obj[candidate]))
#     if datetime.strptime(obj[candidate], "%Y-%m-%d %H:%M:%S.%f") > previous_datetime:
#         print(f"Mail sent to {candidate} sent recently.")
#         continue
#     else:
#         obj[candidate] = datetime.now() - timedelta(hours=5, minutes=30)
#         print(obj)
#         result.last_email_sent = json.dumps(obj, default=str)
#         result.save()
#         send_emails(time=notification[field_name], candidate=candidate, interviewers=notification[notified_name])
    