from .base import *

if os.environ.get("ENV_NAME") == 'Production':
    from .production import *
elif os.environ.get("ENV_NAME") == 'Staging':
    from .staging import *
elif os.environ.get("ENV_NAME") == 'Test':
    from .test import *
else:
    from .local import *
