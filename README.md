# HTTP Server
By: Huseyn Gambarov

# Server-side
Server is able to serve following HTTP requests:
* GET
* POST
* HEAD  

Following error codes are generated:
* Error 404 - if the requested resource does not exist.
* Error 400 - if the request is formatted wrongly. It includes: request is serialized in the wrong way, request headers have wrong values.
* Error 503 - if the number of the simultaneously connected clients exceeds 100, server will respond with 503. 

# Execution
1. Create python virtual environment:
    * _python3 -m venv venv_
    * _source ./venv/bin/activate_
2. Install dependencies:
    * _pip install -r requirements.txt_

Run server:  
* _python3 server.py www_

Run client:
1. Client has multiple configurations. 
    * Mandatory parameters:
        *  server_ip - ip of the server
        * uri - resource that will be requested
        * method - method that will be used in the request
    * Optional parameters:
        * --data - should be specified if method is set to POST
        * -p - client will simulate partial request
        * -m - client will send multiple requests back to back

Run bad client to simulate Error 400:
1. It has following mandatory parameters:
    *  server_ip - ip of the server
    * uri - resource that will be requested
    * method - method that will be used in the request

# Notable files
* /backend/connection.py - has configuration of the connection class
* /utils/handlers.py - has all handlers that were used to handle requests and error, as well as intermediate processes
* /utils/logger.py - logger configuration that was used 
* client.py - python file to simulate client
* bad_client.py - python file to simulate bad request
* test.sh - python script to simulate multiple clients 

# Used dependencies
* colorama==0.4.6
* ply==3.11

# System versions
* Python 3.11.6
* Linux 6.5.0-21-generic x86_64
* "Ubuntu 23.10"

