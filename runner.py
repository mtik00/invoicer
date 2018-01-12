import os
from invoicer import app

debug = os.environ.get('FLASK_DEBUG') == '1'

app.run(debug=debug, host='0.0.0.0')
