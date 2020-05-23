from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        from api.jobs import job_expired_transaction
        job_expired_transaction.start()
