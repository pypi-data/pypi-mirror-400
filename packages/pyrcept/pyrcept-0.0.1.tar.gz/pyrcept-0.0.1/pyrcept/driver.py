import sys
import time
from pathlib import Path
import pickle as pkl
from importlib.resources import files as imp_files
from importlib.metadata import version as get_version
from contextlib import contextmanager
import requests as rqs
from bottle import Bottle, route, run, static_file

version = get_version('pyrcept')
pkg_root = Path(imp_files('pyrcept'))
app = Bottle() # Explicit app instance



# Define a route for the home page
@app.route('/')
def home():
    return '<h1>Hello from Bottle!</h1><p>This page is being served by a Bottle server.</p>'

@app.route('/static/<filepath:path>')
def server_static(filepath):
    # Note that requests cannot escape (see parents) of root directory
    return static_file(filepath, root=str(pkg_root/'pyrcept'/'frontend'))



def host(host, port, storage=None): # TOOD: error if do this more than once
    if storage == None: # TODO: user-specific subdir
        if sys.platform == 'win32':
            storage = Path.home() / 'AppData/Roaming'
        elif sys.platform == 'linux':
            storage = Path.home() / '.local/share'
        elif sys.platform == 'darwin':
            storage = Path.home() / 'Library/Application Support'
        else:
            raise Exception('Unrecognised platform \'{}\', only win32, linux, and darwin are supported for default i.e. app data storage; provide a valid directory instead'.format(sys.platform))
    app.run(host=host, port=port)

class client_sesh():
    def __init__(self, url):
        self.url = url

    def log(self, **kwargs):
        # TODO: send to server, server records and relays for JS to update display

        

        try:
            # Send log via POST request
            rsp = rqs.post(self.url+'/log', data=kwargs)
            
            # Raise an exception for bad status codes (4xx or 5xx)
            rsp.raise_for_status()

            # # Get the JSON data from the response
            # data = response.json()
            
            # # Print the received data
            # print("Received data from server:")
            # print(json.dumps(data, indent=2))

        except rqs.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


@contextmanager
def connect(project, config, host, port):
    # TODO: need a identifier for config so it is run specific
    url = 'http://{host}:{port}/project'.format(host=host, port=port)
    
    try:
        yield client_sesh(url)
    finally:
        pass
