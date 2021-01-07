# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2020-06-16 10:29:52
File Name: form.py @v1.0
"""
from django import forms
from django.core.cache import cache
from .models import RedisValue


class AddCache(forms.ModelForm):

    # value_types = [
    #     ('User', 'User'),
    #     ('DeviceID', 'DeviceID'),
    #     ('SessionID', 'SessionID'),
    #     ('Bool', 'Bool'),
    #     ('DataFrame', 'DataFrame'),
    #     ('String', 'String'),
    #     ('XRS', 'XRS'),
    #     ('Unspecified', 'Unspecified'),
    # ]
    # key_types = [
    #     ('UserId', 'UserId'),
    #     ('DeviceID', 'DeviceID'),
    #     ('SessionID', 'SessionID'),
    #     ('XRS', 'XRS'),
    #     ('Unspecified', 'Unspecified'),
    # ]

    # key = forms.CharField(label='Cache key', required=True, max_length=100)
    # key_type = forms.ChoiceField(choices=key_types, initial='Unspecified')
    # timeout = forms.IntegerField(initial=3600)
    # value_type = forms.ChoiceField(choices=value_types, initial='Unspecified')
    # value = forms.CharField(label='Raw value', required=True)

    @staticmethod
    def get_count(cls):
        return len(cache.keys('*'))

    @classmethod
    def get_data(cls, request, start=None, stop=None):
        # get all data to display in change list page
        # return list of data.
        # data is dict format, key is fields defined above
        def get_type(k):
            if isinstance(k, tuple):
                return "XRS", "DataFrame"
            elif isinstance(k, (str, unicode)):
                if len(k) == 40:
                    return "Session", "UserName"
                else:
                    return "deviceID", "Bool"
            else:
                return type(k), type(cache.get(k))

        return [{"key": k, "value": cache.get(k), "key_type": get_type(k)[0], "value_type": get_type(k)[1], "ttl": cache.ttl(k), "timeout": 3600} for k in cache.keys('*')]

    @classmethod
    def get_data_by_pk(cls, request, pk):
        # change form view
        return cache.get(pk)

    @classmethod
    def create_data(cls, request, data):
        # create new data
        return cache.set(data['key'], data['value'], data['timeout'])

    @classmethod
    def update_data(cls, request, data):
        # update an exist data
        return cache.expire(data['key'], timeout=data['timeout'])

    @classmethod
    def delete_data(cls, request, data):
        return cache.delete(data['key'])

    @classmethod
    def save(cls, commit=True):
        print(888)
        return True

    def clean_key(self):
        value = self.cleaned_data.get("key")
        if False:
            raise ValidationError("Unsupported key.")
        return value

    def clean_key_type(self):
        value = self.cleaned_data.get("key")
        if value not in ['UserId', 'DeviceID', 'SessionID', 'XRS', 'Unspecified']:
            raise ValidationError("Unsupported key type.")
        return value

    def clean_timeout(self):
        value = self.cleaned_data.get("timeout")
        try:
            int(value)
        except:
            raise ValidationError("Unsupported value.")
        return value

    def clean_value_type(self):
        value = self.cleaned_data.get("value_type")
        return value

    def clean_value(self):
        value = self.cleaned_data.get("value")
        return value

    def clean_expires_at(self):
        value = self.cleaned_data.get("expires_at")
        return value

    def clean_ttl(self):
        value = self.cleaned_data.get("ttl")
        return value

    class Meta:
        model = RedisValue
        fields = "__all__"
        # fields = ['key_type', 'timeout', 'value_type']


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    # import pydoc
    # pydoc.doc(SomeClass)
