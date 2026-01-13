# Example where Pyrcept is ran on the same machine as the job but hosted seprately via localhost
# Author: Thomas A. Scott

import pyrcept as pyr


if __name__ == '__main__':
    host, port = 'localhost', 8000
    project = 'examples/basic_intro'
    config = {
        'learning_rate': 0.02,
        "architecture": "CNN",
        "dataset": "CIFAR-100",
        "epochs": 10,
    }
    
    # Start a local Pyrcept server if not already present
    try:
        server = pyr.host(host, port)
    except AlreadyHosted:
        print('Using existing')
    
    with pyr.connect(project, config, host, port) as run:
        run.log(t=0.5, error=0.0)
