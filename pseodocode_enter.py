from tkinter import Tk,Text,Message, Button,Frame
import os

base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"
file_map = {}

current_dir = 0
to_go_files = []
current_file_name = ""

for i in range(1,17):
    dir = base_dir+str(i)
    trans_files = os.listdir(dir+"/transcripts")
    file_map[i] = trans_files


def set_up_next_example():
    global current_dir
    global to_go_files
    global base_dir
    global current_file_name
    if len(to_go_files) == 0:
        current_dir += 1
        to_go_files = file_map[current_dir]
    current_file_name = to_go_files.pop(0).strip(".txt")
    trans_filepath = base_dir + str(current_dir) + "/transcripts/"+current_file_name+".txt"
    with open(trans_filepath,'r') as datafile:
        transcript_lable['text'] = datafile.read()
    pseudo_filepath= base_dir + str(current_dir) + "/pseudocode/"+current_file_name+".txt"
    if os.path.isfile(pseudo_filepath):
        pseudo_textfield.delete('1.0', 'end')
        with open(pseudo_filepath, 'r') as datafile:
            pseudo_textfield.insert("end",datafile.read())
    else:
        pseudo_textfield.delete('1.0', 'end')

    print(current_file_name)


def save_pseudocode():
    global current_dir
    global base_dir
    global current_file_name
    pseudo_filepath= base_dir + str(current_dir) + "/pseudocode/"+current_file_name+".txt"
    with open(pseudo_filepath, 'w+') as datafile:
        datafile.write(pseudo_textfield.get("1.0","end"))


def next_callback():
    save_pseudocode()
    if current_dir == 16 and len(to_go_files) == 0:
        transcript_lable['text'] = "Finished"
    else:
        set_up_next_example()


root = Tk()
root.geometry("550x900")
root.resizable(0,0)
root.configure(background='black')
b = Button(root, text="Next", command=next_callback)
b.pack()
transcript_lable = Message(root, text="Text", width=500)
transcript_lable.configure(background='black',foreground='white')
transcript_lable.pack()
pseudo_textfield = Text(root)
pseudo_textfield.pack()
b = Button(root, text="Next", command=next_callback)
b.pack()
set_up_next_example()
root.mainloop()
