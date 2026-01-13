import os


def try_remove_files(paths):
    for path in paths:
        try:
            os.remove(path)
        except:
            pass
