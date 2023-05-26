from xml.etree import ElementTree
from xml.dom import minidom
import os


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_last_dir_path(path):
    # return path[::-1][:path[::-1].find('/')][::-1]
    return os.path.basename(os.path.normpath(path))


def find_file_extension(dir_path, extension):
    files = os.listdir(dir_path)
    for file in files:
        if file.endswith(extension):
            return os.path.join(dir_path, file)
    return None