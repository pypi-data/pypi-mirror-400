from flask import Flask, Response, Request, send_file, jsonify, request
from monolit_local_app.funces import *
from typing import Callable

server = Flask(__name__)
path_to_build_ = None
path_to_index_ = None
process_request_ = None
process_path_ = None
communication_path_ = None

@server.route("/")
def send_index() -> tuple[Response | str, int]:
    """This fuction sends main index.html file"""

    try:
        return send_file(path_to_index_), 200
    except Exception as e:
        return e.__str__(), 404

@server.route("/<path:path>")
def send_static(path: str) -> tuple[Response | str, int]:
    """This function sends all requested static files"""

    if path == communication_path_:
        return process_request_()
    
    path = process_path_(path) if isinstance(process_path_(path), str) else path

    try:
        return send_file(sum_paths(path_to_build_, path)), 200
    except Exception as e:
        return e.__str__(), 404

def run(
    path_to_build: str | None,
    path_to_index: str | None,
    path_to_static: str | None,
    process_request: Callable[[Request], Response] | None = None,
    process_path: Callable[[str], str] | None = None,
    communication_path: str | None = "process",
    host: str | None = "localhost",
    port: int | None = 3000,
    debug: bool | None = False,
    preprocessing: bool | None = True
):
    """
    This function hosts your JavaScript project at the URL you specify.
    
    Args:
        path_to_build: Absolute path to build-folder
        path_to_index: Absolute path to file index.html
        path_to_static: Absolute path to static-folder
        process_request: Method for requests client
        process_path: Method for additional processing client`s requested paths
        host: Url-address
        port: Number of port
        debug: Operating mode
        preprocessing: Preprocessing for the build folder. This is a new, experimental feature, but it's necessary to resolve naming conflicts. If you use standard project builders, everything will most likely work fine. However, if unexpected errors occur, we recommend consulting the official documentation
    """

    global path_to_build_, path_to_index_, communication_path_, process_request_, process_path_
 
    path_to_build_ = path_to_build
    path_to_index_ = path_to_index
    communication_path_ = communication_path

    process_path_ = process_path if process_path != None else lambda path: path
    process_request__ = process_request if process_request != None else lambda request: jsonify({})

    @server.route("/" + communication_path_, methods=["POST"])
    def wrapper():
        """This function for requests client"""

        if request.method == "POST":
            if request.is_json:
                try:
                    return process_request__(request)
                except Exception as e:
                    print(f"[SERVER] Can not process JSON: {e}")
                    return jsonify({"error": "Can not process JSON"}), 400
            else:
                print(f"[SERVER] Request must be in JSON format")
                return jsonify({"error": "Request must be in JSON format"}), 415
        else:
            print(f"[SERVER] Method '{request.method}' not support")
            return jsonify({"error": f"Method '{request.method}' not support"}), 405
        
    process_request_ = wrapper

    if preprocessing:
        preprocess_index(path_to_index_, path_to_static)

    server.run(host, port, debug)


class LocalServer:
    """
    This class helps start local-server<br>
    Make your application class inherit from this class
    """

    def __init__(
        self,
        path_to_build: str | None,
        path_to_index: str | None,
        path_to_static: str | None,
        communication_path: str | None = "process",
        host: str | None = "localhost",
        port: int | None = 3000,
        debug: bool | None = False,
        preprocessing: bool | None = True
    ):
        """
        Initializes all properties
        
        Args:
            path_to_build: Absolute path to build-folder
            path_to_index: Absolute path to file index.html
            path_to_static: Absolute path to static-folder
            process_request: Method for requests client
            host: Url-address
            port: Number of port
            debug: Operating mode
            preprocessing: Preprocessing for the build folder. This is a new, experimental feature, but it's necessary to resolve naming conflicts. If you use standard project builders, everything will most likely work fine. However, if unexpected errors occur, we recommend consulting the official documentation
        """

        self.path_to_build: str | None = path_to_build
        self.path_to_index: str | None = path_to_index
        self.path_to_static: str | None = path_to_static
        self.communication_path: str | None = communication_path
        self.host: str | None = host
        self.port: int | None = port
        self.debug: bool | None = debug
        self.preprocessing: bool | None = preprocessing

    def process_request(self, request: Request) -> Response:
        """
        <h2>For inheritance!</h2><br>
        This method should receive a <code>request</code> from the client and respond to it
        
        Args:
            request: client's request in json format

        Returns:
            Responce: answer on client-request
        """
    
    def process_path(self, path: str) -> str:
        """
        <h2>For inheritance!</h2><br>
        This method should receive a <code>path-to-file</code> from the client and process this path

        Args:
            path: client's path to some file

        Returns:
            str: alternative or same path
        """

    def __call__(self):
        """This function hosts your JavaScript project at the URL you specify. It is analog function run"""

        run(
            self.path_to_build,
            self.path_to_index,
            self.path_to_static,
            self.process_request,
            self.process_path,
            self.communication_path,
            self.host,
            self.port,
            self.debug,
            self.preprocessing
        )