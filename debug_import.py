import importlib, traceback
try:
    m = importlib.import_module('accounts.forms')
    print('OK', [n for n in dir(m) if 'Patient' in n or 'UserRegistration' in n])
except Exception:
    traceback.print_exc()
