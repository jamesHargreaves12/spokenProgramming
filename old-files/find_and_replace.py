import os

from tools.find_resource_in_project import get_path

log_result_files = os.listdir(get_path("results"))
# log_result_files = [x for x in log_result_files if x.startswith("results") and not x.endswith("logs")]
x = False
for filename in log_result_files:
    print(filename)
    with open(get_path("results/"+filename),"r") as file:
        text = file.read()
    text = text.replace("return","output")
    with open(get_path("results/"+filename),"w") as file:
        file.write(text)
