# AI DECLARATION:
#Used ChatGPT 4o, o1, for debugging and problem resolving
import threading
import xmlrpc.client
from datetime import datetime

def send_request(topic, note_title, note_text):
    
    print(f"[{threading.current_thread().name}] Starting request for {topic}") #Indicating that thread is staring
    try:
        #XML-RPC client for the server (port 3000)
        server = xmlrpc.client.ServerProxy("http://localhost:3000", allow_none=True)
        timestamp = datetime.now().isoformat()
        #Add note request
        response = server.add_note(topic, note_title, note_text, timestamp)
        print(f"[{threading.current_thread().name}] Finished request for {topic}: {response}") #Response from server
    except Exception as error:
        print(f"[{threading.current_thread().name}] Error during request for {topic}: {error}")
        

def main():
    threads = []
   #10 threads to simulate
    for i in range(10):
        topic = f"Topic{i}"
        note_title = f"Note Title {i}"
        note_text = f"Note text {i}"
        print(f"Main thread: Launching thread for {topic}")

        #New thread for each request
        t = threading.Thread(target=send_request, args=(topic, note_title, note_text))
        threads.append(t)
        t.start()

    #Wait for all threads to finnish
    for t in threads:
        t.join()

    print("All requests completed.")


if __name__ == '__main__':
    main()
