class MailSendFailure(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "MailSendFailure, {0} ".format(self.message)
        else:
            return "MailSendFailure attempts to send email failed"


class MissingAPIKey(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "MissingAPIKey, {0} ".format(self.message)
        else:
            return "MissingAPIKey a sendgrid API key must be provided to create an instance this class"


class MalformedConfiguration(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "MalformedConfiguration, {0} ".format(self.message)
        else:
            return "MalformedConfiguration supplied configuration is not valid or missing"
        

class BadSenderObject(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "BadSenderObject, {0} ".format(self.message)
        else:
            return 'BadSenderObject: sender parameter object must include "email" key' 