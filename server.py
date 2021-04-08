#########################################
# Niilo Liimatainen
# 16.03.2021
# Sources:
# 
#########################################
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import socketserver
import shortest_path_finder as spf
import time
import traceback
import json

# Creating threading version from the SimpleXMLRPCServer, which creates a new thread to handle each request.
class ThreadedSimpleXMLRPCServer (socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    pass

# Restricting requests to a certain path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)
 
# Creating the server
def start_server():
    try:
        server = ThreadedSimpleXMLRPCServer(("127.0.0.1", 8000), requestHandler=RequestHandler)

        print("Server is running!")

        def test():
            return 1

        def find_shortest_path(start_page, end_page):
            start = time.time()
            result = spf.breadth_first_search(start_page, end_page)
            if isinstance(result, int):
                return result
            end = time.time()
            run_time = round((end - start), 2)
            key = result.keys()[0]
            path = result[key]
            path_length = len(path) - 1

            json_data = json.dumps({"path": path, "time": run_time, "length": path_length})
            json_object = json.loads(json_data)
            return json_object

        server.register_function(test)
        server.register_function(find_shortest_path)
        server.serve_forever()
    except Exception:
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    start_server()