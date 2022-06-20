from django.apps import AppConfig


class DynamicModelsConfig(AppConfig):
    name = 'dynamic_models'
    verbose_name = 'Dynamic Models'

    def ready(self) -> None:
        from notifications import schedular
        from notifications.emailSender import EmailSenderQuaterly
        print("Starting Task.")
        schedular.start()
        EmailSenderQuaterly()
