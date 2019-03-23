import os

project_location = "/Users/james_hargreaves/PycharmProjects/spokenProgramming/"


def get_path(path_in_project):
    path_in_project = path_in_project.lstrip('/')
    return os.path.join(project_location,path_in_project)


if __name__ == "__main__":
    print(get_path("data/values.txt"))
    print(get_path("/data/values.txt"))
