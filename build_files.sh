 #!/bin/bash
 pip install -r requirements.txt
 python manage.py collectstatic --noinput
 python manage.py check --deploy
