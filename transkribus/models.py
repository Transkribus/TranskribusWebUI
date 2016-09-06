from django.db import models

from django.contrib.auth.models import User as _User

from . import helpers


class User(_User):
    class Meta:
        proxy = True

    @classmethod
    def create(self, **data):
        return self.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_superuser=data['is_superuser'],
            # is_active=data['is_active']
        )

    def update(self, **data):
        helpers.update_changed(self, data, [
            'email', 'last_name', 'first_name', 'is_superuser'
        ])


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    gender = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    session_id = models.CharField(max_length=32) # NOTE: use this for API
    # ip = models.IPAddressField()


    @classmethod
    def create(self, **data):
        return self.objects.create(
            user=data['user'],
            gender=data['gender'],
            affiliation=data['affiliation'],
            session_id=data['session_id'],
        )

    def update(self, **data):
        helpers.update_changed(self, data, [
            'gender', 'affiliation', 'session_id',
        ])
