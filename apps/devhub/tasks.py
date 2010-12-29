import json
import logging
import os
import sys
import traceback

from django.conf import settings
from django.core.management import call_command
from celeryutils import task

from amo.decorators import write
from amo.utils import resize_image
from files.models import FileUpload, File, FileValidation
from applications.management.commands import dump_apps

log = logging.getLogger('z.devhub.task')


@task(queue='devhub')
@write
def validator(upload_id, **kw):
    log.info('VALIDATING: %s' % upload_id)
    upload = FileUpload.objects.get(pk=upload_id)
    try:
        result = _validator(upload.path)
        upload.validation = result
        upload.save()  # We want to hit the custom save().
    except:
        # Store the error with the FileUpload job, then raise
        # it for normal logging.
        tb = traceback.format_exception(*sys.exc_info())
        upload.update(task_error=''.join(tb))
        raise


@task(queue='devhub')
@write
def file_validator(file_id, **kw):
    log.info('VALIDATING file: %s' % file_id)
    file = File.objects.get(pk=file_id)
    # Unlike upload validation, let the validator
    # raise an exception if there is one.
    result = _validator(file.file_path)
    return FileValidation.from_json(file, result)


def _validator(file_path):

    from validate import validate

    # TODO(Kumar) remove this when validator is fixed, see bug 620503
    from validator.testcases import scripting
    scripting.SPIDERMONKEY_INSTALLATION = settings.SPIDERMONKEY
    import validator.constants
    validator.constants.SPIDERMONKEY_INSTALLATION = settings.SPIDERMONKEY

    apps = dump_apps.Command.JSON_PATH
    if not os.path.exists(apps):
        call_command('dump_apps')

    return validate(file_path, format='json',
                    # Continue validating each tier even if one has an error
                    determined=True,
                    approved_applications=apps,
                    spidermonkey=settings.SPIDERMONKEY)


@task(queue='images')
def resize_icon(src, dst, size, **kw):
    """Resizes addon icons."""
    log.info('[1@None] Resizing icon: %s' % dst)

    try:
        if isinstance(size, list):
            for s in size:
                resize_image(src, '%s-%s.png' % (dst, s), (s, s),
                             remove_src=False)
            os.remove(src)
        else:
            resize_image(src, dst, (size, size), remove_src=True)

    except Exception, e:
        log.error("Error saving addon icon: %s" % e)
