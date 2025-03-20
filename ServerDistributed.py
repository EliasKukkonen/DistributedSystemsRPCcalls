# AI DECLARATION:
#Used ChatGPT 4o, o1, for debugging and problem resolving
import os
import sys
import xml.etree.ElementTree as ET
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import requests
from datetime import datetime
import threading
from xmlrpc.client import Fault

XML_FILE = 'XMLNOTERecording.xml' #Storing notes locally
lock = threading.RLock()  # Lock to synchronize access to the XML file, reentrant lock allows the same thread
#acquire it multiple times without deadlocking.


def GetTree():
    with lock:
        try:
            if not os.path.exists(XML_FILE):
                # Create a new XML file with a root element #data"
                root = ET.Element('data')
                tree = ET.ElementTree(root)
                tree.write(XML_FILE)
            return ET.parse(XML_FILE)
        except Exception as error:
            print(f"Error in GetTree: {error}")
            raise Fault(1, f"Error in GetTree: {error}")

def writeToFile(tree):
    with lock:
        try:
            #Saving the XML tree back to the file
            tree.write(XML_FILE)
        except Exception as error:
            print(f"Error in writeToFile: {error}")
            raise Fault(1, f"Error in writeToFile: {error}")
            

class RequestHandler(SimpleXMLRPCRequestHandler):
    #Restrict RPC paths to /RPRC2 (security reasons) 
    rpc_paths = ('/RPC2',)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    #XML-RPC server, which handles each request as a separate thread
    pass

class Notebook:
    def AddNote(self, topic, note_title, text, timestamp):
        try:
            with lock:
            #Retrieve the tree
                tree = GetTree()
                root = tree.getroot()
                #Look for topic element
                topicElement = root.find(f"./topic[@name='{topic}']")
                if topicElement is None:
                    topicElement = ET.SubElement(root, 'topic', {'name': topic})
                # Create a note element with attribute "name´"
                noteElement = ET.SubElement(topicElement, 'note', {'name': note_title})
                # Add a "text" child for note content
                textElement = ET.SubElement(noteElement, 'text')
                textElement.text = text
                # Add a "timestamp" child
                timestampElement = ET.SubElement(noteElement, 'timestamp')
                timestampElement.text = timestamp
                # Save the tree
                writeToFile(tree)
            return f"Note added under topic '{topic}'."
        except Exception as error:
            print(f"Error in AddNote: {e}")
            raise Fault(1, f"Error in AddNote: {e}")
            

    def GetNotes(self, topic):
        try:
            with lock:
                #Retrieve XML tree and find the topic
                tree = GetTree()
                root = tree.getroot()
                topicElement = root.find(f"./topic[@name='{topic}']")
                if topicElement is None:
                    return "No notes"
                notes = []
                #ITerate through elements to find a note and collect all data
                for note in topicElement.findall('note'):
                    notes.append({
                        'note_title': note.get('name'),
                        'text': note.find('text').text if note.find('text') is not None else "",
                        'timestamp': note.find('timestamp').text if note.find('timestamp') is not None else ""
                    })
                # Also include all Wikipedia Notes
                for wiki in topicElement.findall('wikipedia_note'):
                    notes.append({
                        'timestamp': wiki.get('timestamp'),
                        'text': f"Wikipedia: {wiki.text}"
                    })
            return notes
        except Exception as error:
            print(f"Error in GetNotes: {error}")
            raise Fault(1, f"Error in GetNotes: {error}")
            

    def AppendWikipediaNote(self, topic, wikipedia_link):
        try:
            with lock:
                #Retrieve XML tree and find the topic
                tree = GetTree()
                root = tree.getroot()
                topicElement = root.find(f"./topic[@name='{topic}']")
                if topicElement is None:
                    topicElement = ET.SubElement(root, 'topic', {'name': topic})
                # Create a new element for the wikipedia
                wikiElement = ET.SubElement(topicElement, 'wikipedia_note')
                wikiElement.set('timestamp', datetime.now().isoformat())
                wikiElement.text = wikipedia_link
                # Save changes
                writeToFile(tree)
            print(f"Wikipedia link appended under topic '{topic}': {wikipedia_link}")
        except Exception as error:
            print(f"Error in AppendWikipediaNote: {error}")
            raise Fault(1, f"Error in AppendWikipediaNote: {error}")
            

    def FetchFromWikipedia(self, topic):
        try:
            #Set up request parameters for the Wikipedia API
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'opensearch',
                'search': topic,
                'limit': 1,
                'namespace': 0,
                'format': 'json'
            }
            response = requests.get(url, params=params)
            data = response.json()
            #Find link, append it a as a note and return link to the user
            if len(data) >= 4 and data[3]:
                wikipedia_link = data[3][0]
                self.AppendWikipediaNote(topic, wikipedia_link)
                print(f"Fetched Wikipedia link for topic '{topic}': {wikipedia_link}")
                return {"topic": topic, "wikipedia_link": wikipedia_link}
            else:
                return "No article found"
        except Exception as error:
            print(f"Error in FetchFromWikipedia: {error}")
            raise Fault(1, f"Error in FetchFromWikipedia: {error}")
            

def main():
    # Allow port specification via command-line argument; default is 3000, others 3001, 3002.
    port = 3000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 3000.")
    #Create XML-RPC server (threaded)
    server = ThreadedXMLRPCServer(("localhost", port), requestHandler=RequestHandler, allow_none=True)
    server.register_instance(Notebook())
    print(f"Server is running on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server is shutting down.")

if __name__ == '__main__':
    main()
