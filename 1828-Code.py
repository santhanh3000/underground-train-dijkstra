import tkinter as tk                        # Import the libraries we used
from tkinter import ttk
import openpyxl
import tkinter.messagebox as tm
import collections
from collections import namedtuple, deque

root = tk.Tk()                              # Create the base form of the UI
root.geometry("1000x500")                   # Set dimensions of the form
root.title("Journey App")                   # Set the title of the form
root.resizable(False, False)                # Disable maximize/minimize and resizability

style = ttk.Style(root)             
style.theme_use("clam")


header = tk.Label(root, text="Journey Select", width=18, font=("bold", 15)).place(x=0, y=5)                 # Add labels to the form

label_journeyStart = tk.Label(root, text= "From:" , width = 7, font = ("bold", 12)).place(x = 0, y = 45)    # Add labels to the form
label_journeyEnd = tk.Label(root, text="To:", width = 7, font = ("bold", 12)).place(x = 0, y = 100)         # Add labels to the form

searchButton = tk.Button(root, text="Search",font=("Calibri 12"), width = 15, bg='light blue', fg='black', command=lambda: searchButtonPressed()).place(x = 10, y = 200)        # Create a button that calls searchButtonPressed()

mapButton = tk.Button(root, text="Map",font=("Calibri 12"), width = 15, bg='light blue', fg='black').place(x = 10, y = 250) 

      
list0 = []
list1 = []

temp_file = open("stations.txt", "r")           # Open a file that contains the names of all the used stations
for line in temp_file:                          # Run through the file and populate list0
    list0.append(line.strip())
   
temp_file.close()                               # Close the opened file
        
list0.sort                                      # Sort list0 alphabetically
list1 = list(dict.fromkeys(list0))              # Create a dictionary with the above parsed list0
        
js = tk.StringVar() 
combo_journeyStart = ttk.Combobox(root, width = 27, textvariable = js) 
combo_journeyStart['values'] = list1
combo_journeyStart.place(x = 10, y = 75)
        
je = tk.StringVar() 
combo_journeyEnd = ttk.Combobox(root, width = 27, textvariable = je) 
combo_journeyEnd['values'] = list1
combo_journeyEnd.place(x = 10, y = 130) 


tree = ttk.Treeview(root)
tree.canvas = tk.Canvas(width=600, height=750, relief='sunken')

tree['columns'] = ("station", "line", "stationTime", "totalTime")           # Create a treeview with given colums 

tree.column('#0', stretch=False, minwidth=0, width=0)                       # Create columns for the treeview
tree.column('#1', stretch=False, minwidth=0, width=150)
tree.column('#2', stretch=False, minwidth=0, width=150)
tree.column('#3', stretch=False, minwidth=0, width=150)

tree.heading("station", text="Station")                                     
tree.heading("line", text="Line")
tree.heading("stationTime", text="Station Time(min)")
tree.heading("totalTime", text="Total Time(min)")
tree.place(x=250, y=20)

vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)            # Create a scrollbar
vsb.place(x=910, y=20, height=230)

tree.configure(yscrollcommand=vsb.set)

summary = tk.Text(root, width=81, heigh=13)
summary.place(x=251, y=260)
summary.config(relief="sunken")

scrollBar = ttk.Scrollbar(root, command=summary.yview)
scrollBar.place(x=910, y=260, height=214)
summary['yscrollcommand'] = scrollBar.set


global path, path_line, path_lines, total_time_list, summaryText            # Declate global variables

path = []               # Create lists
path_line = []          #
path_lines = []         #
stations= []            #
summaryText = []        #

total_time_list = []    #

book = openpyxl.load_workbook('London Underground data.xlsx')           # Open data workbook
sheet = book.active                 # Open the active sheet of above opened workbook

class Node(object):                 # Declare class Node
    def __init__(self, data=None, next=None, prev=None):
        self.data = data            # Access local variables and assign new values
        self.next = next
        self.prev = prev

class DoublyLinkedList(object):
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def append_item(self, data):
        new_item = Node(data, None, None)
        if self.head is None:       # if head = None then:
            self.head = new_item    #
            self.tail = self.head   #
        else:                       
            new_item.prev = self.tail
            self.tail.next = new_item
            self.tail = new_item

        self.count += 1             # Iterate count +1

    def print_foward(self):
        for node in self.iter():
            print(node)

    def iter(self):
        current = self.head
        while current:
            item_val = current.data
            current = current.next
            yield item_val

all_data = DoublyLinkedList()

for row in sheet.iter_rows(min_row=1, min_col=1, max_row=800, max_col=4):           # Parse rows in spreadsheet

    stations_row = []       # Declare list stations_row

    for cell in row:
        stations_row.append(cell.value)        # Append list stations_row with parsed data from the spreadsheet

    if stations_row[2] is not None:
        stations.append(stations_row)
        all_data.append_item(stations_row)

        reversed_stations_row = stations_row[:]
        element0 = reversed_stations_row[1]
        reversed_stations_row[1] = reversed_stations_row[2]
        reversed_stations_row[2] = element0

        stations.append(reversed_stations_row)
        all_data.append_item(reversed_stations_row)

inf = float('inf')
Edge = namedtuple('Edge', ['line', 'start', 'end', 'cost'])

# Dijkstra's algorithm

class Graph():          # Declare class Graph
    def __init__(self, edges):
        self.edges = [Edge(*edge) for edge in edges]
        self.vertices = {e.start for e in self.edges} | {e.end for e in self.edges}

    def dijkstra(self, source, dest):
        assert source in self.vertices
        dist = {vertex: inf for vertex in self.vertices}
        previous = {vertex: None for vertex in self.vertices}
        dist[source] = 0
        q = self.vertices.copy()
        neighbours = {vertex: set() for vertex in self.vertices}
        for line, start, end, cost in self.edges:
            neighbours[start].add((end, cost))

        while q:
            u = min(q, key=lambda vertex: dist[vertex])
            q.remove(u)
            if dist[u] == inf or u == dest:
                break
            for v, cost in neighbours[u]:
                alt = dist[u] + cost
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = u
        s, u = deque(), dest
        while previous[u]:
            s.appendleft(u)
            u = previous[u]
        s.appendleft(u)
        return s

graph = Graph(all_data.iter())

def searchButtonPressed():
    path.clear()                   # Clear lists
    path_lines.clear()
    total_time_list.clear()
    summaryText.clear()

    #journeyStartTxt = getattr(root, "combo_journeyStart")
    journeyStart = js.get()
    combo_journeyStart.delete(0,"end")
    
    #journeyEndTxt = getattr(root, "combo_journeyEnd")
    journeyEnd = je.get()
    combo_journeyEnd.delete(0,"end")
    
    if journeyStart != journeyEnd:          # Checks if the journey has ended
            pass
    else:
        tm.showerror("Incorrect Information", "You have entered the same station")
        
    try:            # Error checking commenses
        d = collections.deque(graph.dijkstra(journeyStart, journeyEnd))
        if d == None:
            pass
    
        while True:
            try:
                path.append(d.popleft())            # Append list if no errors are encountered
            except IndexError:
                break
            
        for i in range(len(path)):
            prev_station = ""
            for row in stations:                    # Parse stations 
                if i < len(path)-1:
                    if path[i] == row[1] and path[i + 1] == row[2] and row[1] is not prev_station:
                        path_line = [row[0], row[1], row[2], row[3]]
                        path_lines.append(path_line)
                        prev_station = row[1]

        total_time = 5
        for line in path_lines:
            for i in range(len(path)-1):
                for j in range(1, len(path)):
                    if path[i] == line[1] and path[j] == line[2]:
                        total_time = total_time + int(line[3] + 1)
                        total_time_list.append(total_time)
    
    except:
        tm.showerror("Incorrect Information", """Either:
    1. You have entered the incorrect station name
    2. Indentation present at the start or end where data entered""")
    
    display_route_end = [[x, z] for x, z in zip(total_time_list, path_lines)]
    
    records = tree.get_children()
    for element in records:
        tree.delete(element)
    
    for row in display_route_end:
        tree.insert('', 'end', text=str(), values=(row[2], row[1], row[4], row[0]))
    
    tree.insert('', 'end', text=str(), values=(path[-1], "End Journey", "", ""))
    

    # Start drawing path from station to station

    for i in range(len(path_lines)):
        summary_row = []
        
        current_line = path_lines[i][0]
        
        previous_line = ""
        if i > 0:
            previous_line = path_lines[i-1][0]
            
        next_line = ""
        if i < len(path_lines)-1:
            next_line = path_lines[i+1][0]
            
        if current_line is not previous_line:
            summary_row.append("{}".format(current_line))
            summary_row.append("from {}".format(path_lines[i][1]))
            
        if next_line is not current_line:
            summary_row.append("to {} - change to".format(path_lines[i][2]))
        
        if i < len(path_lines)-1:
            summaryText.append(summary_row)
        else:
            summary_row.pop()
            summary_row.append("to {}".format(path[-1]))
            summaryText.append(summary_row)

    summary.delete("1.0", 'end')

    for row in summaryText:
        for item in row:
            summary.insert("end", item)
            summary.insert("end", "\n")

    summary.insert("end", "Total travel time: ")
    summary.insert("end", total_time_list[-1])
    summary.insert("end", " minutes")

if __name__ == "__main__":
    root.mainloop()