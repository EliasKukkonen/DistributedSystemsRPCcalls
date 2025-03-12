# AI DECLARATION:
#Used ChatGPT 4o, o1, for debugging and problem resolving
import random
import xmlrpc.client
from datetime import datetime
import testThreading

# List of server endpoints
SERVERS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002"
]

def get_server_proxy():
    #Choosing random server and returning proxy ojbect for making RPC calls.
    #Distributing the load between servers.
    server_address = random.choice(SERVERS)
    return xmlrpc.client.ServerProxy(server_address, allow_none=True)

def main():
    while True:
        #Prompts
        print("\nWhat do you want to do?")
        print("1) Add note (topic, text, timestamp)")
        print("2) Get notes for a topic")
        print("3) Fetch Wikipedia link and append")
        print("4) Test the multithreading.")
        print("0) Exit")
        choice = input("Your choice: ")
        if choice == "1":
            #Gathering inputs
            topic = input("Enter topic: ")
            note_title = input("Enter note title: ")
            text = input("Enter note text: ")
            timestamp = datetime.now().isoformat()
            proxy = get_server_proxy()
            #Adding whole data to the XML
            response = proxy.add_note(topic, note_title, text, timestamp)
            print("Response:", response)
        elif choice == "2":
            #Fetch and display all notes under the topic
            topic = input("Enter topic to fetch notes: ")
            proxy = get_server_proxy() 
            notes = proxy.GetNotes(topic) #Fetching itself
            print("Notes:", notes)
        elif choice == "3":
            #Requesting a link to the wikipedia, and appending to a note
            topic = input("Enter Wikipedia topic: ")
            proxy = get_server_proxy()
            result = proxy.FetchFromWikipedia(topic) #Fetching from wikipedia
            if isinstance(result, dict) and 'wikipedia_link' in result: #If suceess appending
                print(f"Wikipedia link for '{topic}': {result['wikipedia_link']}")
            else:
                print("No article found or error occurred.")
        elif choice=="4":
            #Testing the multithreading, via multiple calls
            print("Testing multithreading")
            testThreading.main()
        elif choice == "0":
            #Exiting the loop
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
