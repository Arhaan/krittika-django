from django.core.exceptions import ValidationError


def validate_timings(form):
    if form.endTime:
        if form.startTime >= form.endTime:
            return False
        else:
            return True
    else:
        return True


def validate_file_size(value):
    filesize = value.size

    if filesize > 10485760:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value
