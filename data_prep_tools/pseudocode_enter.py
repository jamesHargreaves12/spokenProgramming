from tkinter import Tk,Text,Message, Button
import os
from pseudocode_lang_1 import pseudo_yacc
from data_prep_tools.constants import base_dir_2

file_map = {}

current_dir = 0
to_go_files = []
current_file_name = ""
initial_pseudocode = ""

for i in range(1,17):
    dir = base_dir+str(i)
    trans_files = os.listdir(dir+"/transcripts")
    file_map[i] = trans_files


def set_up_next_example():
    global current_dir
    global to_go_files
    global base_dir
    global current_file_name
    global initial_pseudocode
    if len(to_go_files) == 0:
        current_dir += 1
        print("")
        print(current_dir)
        to_go_files = file_map[current_dir]
    current_file_name = to_go_files.pop(0).strip(".txt")
    trans_filepath = base_dir + str(current_dir) + "/transcripts/"+current_file_name+".txt"
    with open(trans_filepath,'r') as datafile:
        transcript_lable['text'] = datafile.read().strip('\n') + '\n'
    pseudo_filepath= base_dir + str(current_dir) + "/pseudocode/"+current_file_name+".txt"
    if os.path.isfile(pseudo_filepath):
        pseudo_textfield.delete('1.0', 'end')
        with open(pseudo_filepath, 'r') as datafile:
            initial_pseudocode = datafile.read()
            pseudo_textfield.insert("end",initial_pseudocode)
    else:
        pseudo_textfield.delete('1.0', 'end')
    if pseudo_textfield.winfo_rooty() + pseudo_textfield.winfo_height() > root.winfo_height()-bottom_next.winfo_height():
        pseudo_textfield.config(height=15)
    else:
        pseudo_textfield.config(height=20)
    print(current_file_name)


def save_pseudocode():
    global current_dir
    global base_dir
    global current_file_name
    global initial_pseudocode
    pseudo_filepath= base_dir + str(current_dir) + "/pseudocode/"+current_file_name+".txt"
    current_pseudocode = pseudo_textfield.get("1.0", "end").strip('\n')
    if not (current_pseudocode == initial_pseudocode):
        print("Changed")
        with open(pseudo_filepath, 'w+') as datafile:
                datafile.write(current_pseudocode)


def next_callback():
    parser_ouput = pseudo_yacc.get_errors(pseudo_textfield.get("1.0","end"))
    if parser_ouput:
        error_label["text"] = ""
        for err in parser_ouput:
            error_label["text"] += err + "\n"
    else:
        error_label["text"] = ""
        save_pseudocode()
        if current_dir == 16 and len(to_go_files) == 0:
            transcript_lable['text'] = "Finished"
        else:
            set_up_next_example()


root = Tk()
root.geometry("1300x900")
root.resizable(0,0)
root.configure(background='black')
b = Button(root, text="Next", command=next_callback)
b.pack()
transcript_lable = Message(root, text="Text", width=1200, font=("Courier", 24))
transcript_lable.configure(background='black',foreground='white')
transcript_lable.pack()
pseudo_textfield = Text(root, font=("Courier", 24), width=70, height=20)
pseudo_textfield.pack()
bottom_next = Button(root, text="Next", command=next_callback)
bottom_next.pack()
error_label = Message(root, text="", width=1200, font=("Courier", 16))
error_label.configure(background='black',foreground='red')
error_label.pack()
set_up_next_example()
root.mainloop()
