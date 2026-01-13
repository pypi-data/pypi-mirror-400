"""
    Exceptions raised and handled
"""

class LiteBmcException(Exception):
    """
         Generic lbkit exception
    """
    def __init__(self, *args, **kwargs):
        super(LiteBmcException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(LiteBmcException, self).__str__()

class ArgException(Exception):
    """
         Generic Argument exception
    """
    def __init__(self, *args, **kwargs):
        super(ArgException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(ArgException, self).__str__()

class PackageConfigException(Exception):
    """
         Generic Argument exception
    """
    def __init__(self, *args, **kwargs):
        super(PackageConfigException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(PackageConfigException, self).__str__()

class RunCommandException(Exception):
    """
         Generic Argument exception
    """
    def __init__(self, *args, **kwargs):
        super(RunCommandException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(RunCommandException, self).__str__()

class NotFoundException(LiteBmcException):  # 404
    """
        404 error
    """

    def __init__(self, *args, **kwargs):
        super(NotFoundException, self).__init__(*args, **kwargs)

class XmlErrorException(LiteBmcException):  # 404
    """
        404 error
    """

    def __init__(self, *args, **kwargs):
        super(NotFoundException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(LiteBmcException, self).__str__()


class HttpRequestException(Exception):
    """
         Http request exception
    """
    def __init__(self, *args, **kwargs):
        super(HttpRequestException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(HttpRequestException, self).__str__()

class TestException(Exception):
    pass

class OdfValidateException(Exception):
    def __init__(self, *args, **kwargs):
        super(OdfValidateException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(OdfValidateException, self).__str__()

class DigestNotMatchError(OSError):
    """Raised when source and destination are the same file."""

class ExtractRootfsTarFileError(OSError):
    """Raised when extract rootfs.tar.gz failed."""

class PermissionFormatError(OSError):
    """permission.ini with format."""