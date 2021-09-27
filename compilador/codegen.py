import logging


_logger = logging.getLogger(__name__)


def base(op, arg1='', arg2='', res=''):
    code = f'{op};{arg1};{arg2};{res}'
    _logger.debug(code)
    return code


def alme(arg1, res):
    return base('ALME', arg1, res=res)


def read(res):
    return base('read', res=res)


def write(arg1):
    return base('write', arg1)


def goto(arg1):
    return base('goto', arg1)


def jf(arg1, arg2):
    return base('JF', arg1, arg2)


def uminus(arg1, res):
    return base('uminus', arg1, res=res)


def para():
    return base('PARA')
