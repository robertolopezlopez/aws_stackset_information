from wsgiref.simple_server import make_server

import falcon

from config import load_config
from resources.ping import PingResource
from resources.status import StatusResource

# Load configuration
try:
    _ = load_config()
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)

app = falcon.App()

app.add_route('/ping', PingResource())
app.add_route('/status', StatusResource())

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()
