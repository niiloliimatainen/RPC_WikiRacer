#########################################
# Niilo Liimatainen
# 29.03.2021
# Sources:
# https://docs.python.org/3/library/socketserver.html#socketserver.ThreadingMixIn
# https://docs.python.org/3/library/xmlrpc.server.html#simplexmlrpcserver-example
#########################################
import xmlrpc.client
import datetime
import json

def main():
    # Connecting to the server
    try:
        # Proxy instance allows us to use methods from the server
        proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8000")
        # Test to see if the server is available
        proxy.test()
        
        print("\nYou can use this program to race through Wikipedia!")
        while True:
            print("1) Find the shortest path between two Wikipedia pages")
            print("0) Exit")
            user_input = input("Your choice: ") 
            
            if not user_input.isdigit():
                print("Choice must be a number!\n")
                continue
            choice = int(user_input)

            if choice == 1:
                start_page = input("Give a starting page: ")
                end_page = input("Give an ending page: ")
                print("Searching...")
                print_results(proxy.find_shortest_path(start_page, end_page), start_page, end_page)
                print()

            elif choice == 0:
                print("Thank you!")
                break
            
            else:
                print("Invalid choice!\n")
    
    except Exception:
        print("Server is unavailable, try again later!")


# Helper function to print the results
def print_results(json_object, start_page, end_page):
    if json_object == 0:
        print("Error happened, try again later!")
    
    elif json_object == -1:
        print("Invalid starting page or ending page!")
    
    else:
        path = json_object["path"]
        result = ""
        degree = 0

        if len(path) > 0:
            for page in path:
                if not degree:
                    result += f"{page}"
                else:
                    result += f" -> ({degree}){page} "
                degree += 1

            print(f"\nThe shortest path between '{start_page}' and '{end_page}':")
            print(f"{result}")
            print(f"Path was {json_object['length']} degrees long and it was found in {json_object['time']} seconds!")
        else:
            print(f"There was no path between '{start_page}' and '{end_page}'!")


if __name__ == "__main__":
    main()


