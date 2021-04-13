from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'Images'

    def ready(self):
        import Images.signals
