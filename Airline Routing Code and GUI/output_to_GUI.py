# Here is the structure for the code
# 1. The original files are alt_data.dat and output_file2.txt. These are processed to produce the original grid, with the buttons
# 2. When a button is clicked, the resulting point on the grid changes to a bad_weather coordinate.
# 3. This is reflected in alt_data_edits.dat. Further, the outputs of running this file on Ampl are reflected within output_file3.txt
# 4. All subsequent edits will be made to these file, and these files alone. alt_data.dat and output_file2.txt are not to be touched.

import numpy as np
import tkinter as tk

import os
import argparse
import subprocess
from subprocess import Popen, PIPE

win_ht, win_wd = 1000, 1400
map_window = tk.Tk(screenName="Map", baseName="Map", className="Map")
map_window.title("Map")
Canvas = tk.Canvas(map_window, bg='cyan', height=win_ht, width=win_wd)

def loadFile(filepath):
    file = open(filepath, 'r')
    text = file.read()
    return text

def processConnected(text):
    connected = []
    text = text[text.find('\n')+1:text.find(';')-1]
    text = text.split('\n')
    for i, sentence in enumerate(text):
        j = 1
        sentence = sentence[sentence.find(' ')+1:]
        for word in sentence:
            if word == '1':
                connected.append((i+1, j))
            if word != ' ':
                j += 1
    return connected

def processCityCoordinates(text):
    city_coordinates = {}
    city_coordinates_list = []
    text = text[text.find('\n')+1:text.find(';')]
    text = text.split('\n')
    for i, sentence in enumerate(text):
        sentence = sentence[sentence.find(' ')+1:]
        city_coordinates[i+1] = (int(sentence[0:sentence.find(' ')]), int(sentence[sentence.find(' ')+1:]))
        city_coordinates_list.append(city_coordinates[i+1])
    return city_coordinates, city_coordinates_list

def processBadWeather(text):
    bad_weather = []
    text = text[text.find('\n')+1:text.find(';')]
    text = text.split('\n')
    for i, sentence in enumerate(text):
        j = 1
        sentence = sentence[sentence.find(' ')+1:]
        for word in sentence:
            if word == '1':
                bad_weather.append((i+1, j))
            if word != ' ':
                j += 1
    return bad_weather

def processSubOutputTitle(sub_output):
    first_line = sub_output[0:sub_output.find('\n')]
    m = int(first_line[first_line.find('[')+1:first_line.find(',')])
    
    first_line = first_line[first_line.find(',')+1:]
    n = int(first_line[:first_line.find(',')])
    
    first_line = first_line[first_line.find('*')+2:]
    i = int(first_line[:first_line.find(',')])
    return m, n, i

def processSubOutput(sub_output):
    pairs_tj = []
    sentences = sub_output.split('\n')
    for t, sentence in enumerate(sentences):
        sentence = sentence[sentence.find(' '):]
        f = 0
        while (sentence[f] == ' '):
            f += 1
        sentence = sentence[f:]
        j = 1
        for word in sentence:
            if word == '1':
                pairs_tj.append((t+1, j))
            if word != ' ':
                j += 1
    return pairs_tj

def processWaypointsTime(waypoints_time, T):
    waypoints = {}
    for time in range(1, T+1):
        for element in waypoints_time:
            m, n, t = element
            if (t == time):
                if ((m, n) in waypoints):
                    waypoints[(m, n)].append(waypoints_time[element][0])
                else:
                    waypoints[(m, n)] = waypoints_time[element]
    return waypoints

def combine_funcs(*funcs):
    def inner_combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return inner_combined_func

def reconfigurePath(count, x, y):
    
    def editFiles():
        if count == 1:
            path = r'C:\Users\Gaurav\ME308\alt_data.dat'
            file = open(path, 'r')
            text = file.read()
            file.close()
        elif count != 1:
            path = path = r'C:\Users\Gaurav\ME308\alt_data_edits.dat'
            file = open(path, 'r')
            text = file.read()
            file.close()
        
        path = r'C:\Users\Gaurav\ME308\alt_data_edits.dat'
        file_new = open(path, 'w')
        text_new = text
        
        for i in range(x):
            if (i == 0):
                start = text_new.find("bad_weather")
                index = text_new.index('\n', start) + 1
            else:
                index = text_new.index('\n', index) + 1
        index += 3
        for j in range(1, y):
            index += 2
        text_new = text_new[:index] + str(1) + text_new[index+1:]
        file_new.write(text_new)
        file_new.close()
    
    def runCommands():
        pathToamplExe = r'C:\Users\Gaurav\ME308\ampl.mswin64/ampl'
        pathToRunFile = r'C:\Users\Gaurav\ME308\run_file.run'

        process = Popen([pathToamplExe, pathToRunFile], stdin=PIPE, stdout=PIPE)
        # for line in process.stdout:
        #     print(line, end="")
        # Close the current Program
        # Run the program again, this time with the newer paths and count supplied
        pathToPythonScript = r'C:\Users\Gaurav\ME308\output_to_GUI.py'
        rerunProcess = Popen(['python.exe', pathToPythonScript, r'--datafile_name=C:\Users\Gaurav\ME308\alt_data_edits.dat', r'--outputfile_name=C:\Users\Gaurav\ME308\ampl.mswin64\amplide\plugins\output_file3.txt', r'--count=2'])
    
    editFiles()
    # t1 = open(r'C:\Users\Gaurav\ME308\ampl.mswin64\amplide\plugins\output_file2.txt', 'r').read()
    runCommands()
    # t2 = open(r'C:\Users\Gaurav\ME308\ampl.mswin64\amplide\plugins\output_file2.txt', 'r').read()
    # print(t1 == t2)

def messageFn():
    print("Reprocessing path...")

# Outputs from the below function would be used to build the GUI and should be as follows:
# 1. Number of latitudes and longitudes
# 2. Number of cities, and their coordinates
# 3. Cities which are connected
# 4. Points at which the weather is bad
# 5. Paths between connecting cities
# 6. Maximum time T
def processText(text, connected, mode):
    if (mode == 'output'):
        waypoints_time = {}
        
        output = text[8:]
        output = output.split('\n\n')[:-1]
        output[-1] = output[-1][:-2]
        
        for sub_output in output:
            m, n, i = processSubOutputTitle(sub_output)
            if (m, n) not in connected:
                continue
            sub_output = sub_output[sub_output.find('\n')+1:]
            sub_output = sub_output[sub_output.find('\n')+1:]
            pairs_tj = processSubOutput(sub_output)
            if (len(pairs_tj) != 0):
                for element in pairs_tj:
                    t, j = element[0], element[1]
                    waypoints_time[(m, n, t)] = [(i, j)]
        return waypoints_time
            
    elif (mode == 'data'):
        N = int(text[text.find(':')+3:text.find(';')])
        text = text[text.find(';')+1:]
        
        T = int(text[text.find(':')+3:text.find(';')])
        text = text[text.find(';')+1:]        
        
        latitudes = int(text[text.find(':')+3:text.find(';')]) + 2
        text = text[text.find(';')+1:]
        
        longitudes = int(text[text.find(':')+3:text.find(';')]) + 2
        text = text[text.find(';')+3:]
        
        connected = processConnected(text)
        text = text[text.find(';')+3:]
        
        city_coordinates, city_coordinates_list = processCityCoordinates(text)
        text = text[text.find(';')+3:]
        
        bad_weather = processBadWeather(text)
        return N, T, latitudes, longitudes, connected, city_coordinates, city_coordinates_list, bad_weather

def buildGUI(N, T, latitudes, longitudes, connected, city_coordinates, city_coordinates_list, bad_weather, waypoints, waypoints_time, count):
    try:
        latspace, longspace = win_ht // (latitudes+1), win_wd // (longitudes+1)
        for i in range(1, latitudes+1):
            coordinates = longspace, latspace * i, longspace * longitudes, latspace * i
            line = Canvas.create_line(coordinates, fill='green', width=3)
        for i in range(1, longitudes+1):
            coordinates = longspace * i, latspace, longspace * i, latspace * latitudes
            line = Canvas.create_line(coordinates, fill='green', width=3)
        for i in city_coordinates:
            x, y = city_coordinates[i]
            x, y = y * longspace, x * latspace
            oval = Canvas.create_oval(x-8, y-8, x+8, y+8, fill='red')
            Canvas.create_text(x+13, y+13, text=str(i), font='Arial 12')
        for element in bad_weather:
            x, y = element
            x, y = y * longspace, x * latspace
            rectangle = Canvas.create_rectangle(x-8, y-8, x+8, y+8, fill='black')
        
        for i in range(1, latitudes+1):
            for j in range(1, longitudes+1):
                if (i, j) not in city_coordinates_list and (i, j) not in bad_weather:
                    if (i == 1 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=1* latspace - 12)
                    if (i == 1 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 1, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=1* latspace - 12)
                    if (i == 2 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=2* latspace - 12)
                    if (i == 2 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 2, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=2* latspace - 12)
                    if (i == 3 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=3* latspace - 12)
                    if (i == 3 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 3, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=3* latspace - 12)
                    if (i == 4 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=4* latspace - 12)
                    if (i == 4 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 4, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=4* latspace - 12)
                    if (i == 5 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=5* latspace - 12)
                    if (i == 5 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 5, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=5* latspace - 12)
                    if (i == 6 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=6* latspace - 12)
                    if (i == 6 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 6, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=6* latspace - 12)
                    if (i == 7 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=7* latspace - 12)
                    if (i == 7 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 7, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=7* latspace - 12)
                    if (i == 8 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=8* latspace - 12)
                    if (i == 8 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 8, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=8* latspace - 12)
                    if (i == 9 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=9* latspace - 12)
                    if (i == 9 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 9, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=9* latspace - 12)
                    if (i == 10 and j == 1):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 1), lambda:messageFn()))
                        button.place(x=1* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 2):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 2), lambda:messageFn()))
                        button.place(x=2* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 3):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 3), lambda:messageFn()))
                        button.place(x=3* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 4):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 4), lambda:messageFn()))
                        button.place(x=4* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 5):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 5), lambda:messageFn()))
                        button.place(x=5* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 6):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 6), lambda:messageFn()))
                        button.place(x=6* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 7):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 7), lambda:messageFn()))
                        button.place(x=7* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 8):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 8), lambda:messageFn()))
                        button.place(x=8* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 9):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 9), lambda:messageFn()))
                        button.place(x=9* longspace - 4, y=10* latspace - 12)
                    if (i == 10 and j == 10):
                        button = tk.Button(Canvas, height=0, width=0, command=combine_funcs(lambda: reconfigurePath(count, 10, 10), lambda:messageFn()))
                        button.place(x=10* longspace - 4, y=10* latspace - 12)
        
        for element in waypoints:
            path = waypoints[element]
            for i, coordinate in enumerate(path):
                if (i > 0 and i < len(path) - 1):
                    x, y = coordinate
                    if ((x, y) not in city_coordinates_list and (x, y) not in bad_weather):
                        marker = True
                    else:
                        marker = False
                    x, y = y * longspace, x * latspace
                    if marker:
                        oval = Canvas.create_oval(x-8, y-8, x+8, y+8, fill='blue')
                    if (i < len(path) - 2):
                        x1, y1 = path[i+1][1] * longspace, path[i+1][0] * latspace
                        if (x == x1):
                            if (y < y1):
                                coordinates = x, y+8, x1, y1-8
                            else:
                                coordinates = x, y-8, x1, y1+8
                        elif (y == y1):
                            if (x < x1):
                                coordinates = x+8, y, x1-8, y1
                            else:
                                coordinates = x-8, y, x1+8, y1
                        line = Canvas.create_line(coordinates, fill='blue', width=2, arrow=tk.LAST)
                    elif (i == len(path) - 2):
                        x1, y1 = path[i+1][1] * longspace, path[i+1][0] * latspace
                        if (x == x1):
                            if (y < y1):
                                coordinates = x, y, x1, y1-8
                            else:
                                coordinates = x, y, x1, y1+8
                        elif (y == y1):
                            if (x < x1):
                                coordinates = x, y, x1-8, y1
                            else:
                                coordinates = x, y, x1+8, y1
                        line = Canvas.create_line(coordinates, fill='blue', width=2, arrow=tk.LAST)
                elif (i == 0):
                    x, y = coordinate
                    x, y = y * longspace, x * latspace
                    x1, y1 = path[i+1][1] * longspace, path[i+1][0] * latspace
                    if (x == x1):
                        if (y < y1):
                            coordinates = x, y+8, x1, y1-8
                        else:
                            coordinates = x, y-8, x1, y1+8
                    elif (y == y1):
                        if (x < x1):
                            coordinates = x+8, y, x1-8, y1
                        else:
                            coordinates = x-8, y, x1+8, y1
                    line = Canvas.create_line(coordinates, fill='blue', width=2, arrow=tk.LAST)
    except Exception as e:
        print('Infeasible Solution')

def main(filepath, datapath, count):
    text = loadFile(filepath)
    data = loadFile(datapath)
    N, T, latitudes, longitudes, connected, city_coordinates, city_coordinates_list, bad_weather = processText(data, connected=None, mode='data')
    waypoints_time = processText(text, connected, mode='output')
    waypoints = processWaypointsTime(waypoints_time, T)
    buildGUI(N, T, latitudes, longitudes, connected, city_coordinates, city_coordinates_list, bad_weather, waypoints, waypoints_time, count)

parser = argparse.ArgumentParser()
parser.add_argument("--datafile_name", default=r'C:\Users\Gaurav\ME308\alt_data.dat')
parser.add_argument("--outputfile_name", default=r'C:\Users\Gaurav\ME308\ampl.mswin64\amplide\plugins\output_file2.txt')
parser.add_argument('-c', '--count', default='1')

args = parser.parse_args()
datapath = args.datafile_name
filepath = args.outputfile_name
count = int(args.count)

if count == 1:
    file = open(r'C:\Users\Gaurav\ME308\ampl.mswin64\amplide\plugins\output_file2.txt', 'r')
    text = file.read()
    edits_file = open(r'C:\Users\Gaurav\ME308\ampl.mswin64\amplide\plugins\output_file3.txt', 'w')
    edits_file.write(text)
    file.close()
    edits_file.close()
    
    file = open(r'C:\Users\Gaurav\ME308\alt_data.dat', 'r')
    text = file.read()
    edits_file = open(r'C:\Users\Gaurav\ME308\alt_data_edits.dat', 'w')
    edits_file.write(text)
    file.close()
    edits_file.close()

main(filepath, datapath, count)
Canvas.pack()
map_window.mainloop()