import re

from rest_framework import serializers


def validate_username(username_value):
    if not re.match(r'^[\w.@+-]+\Z', username_value):
        raise serializers.ValidationError(
            'Имя пользователя содержит недопустимые символы!')
