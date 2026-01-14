
"""
Module for saving and loading data to/from files in JSON format.
Provides functions to save, load, delete, check existence, list files, and clear files in a directory.
"""

from typing import List, Any
from json import loads, dumps
from os import remove, path, listdir
from sys import getsizeof

__all__ = ['storage']

class Storage:
    def __init__(self):
        pass

    def save(self, data: str,filename: str) -> None:
        """
        Save data to a file in JSON format.
        :param data: The data to save.
        :param filename: The name of the file to save the data to.
        """

        try:
            with open(filename, 'w') as f:
                f.write(dumps(data))
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")

    def load(self, filename: str):
        """
        Load data from a file in JSON format.
        :param filename: The name of the file to load the data from.
        :return: The loaded data.
        """
        
        try:
            with open(filename, 'r') as f:
                data = f.read()
                return loads(data)
        except Exception as e:
            print(f"Error loading data from {filename}: {e}")
            return None

    def delete(self, filename: str) -> None:
        """
        Delete a file.
        :param filename: The name of the file to delete.
        """

        try:
            remove(filename)
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists.
        :param filename: The name of the file to check.
        :return: True if the file exists, False otherwise.
        """

        return path.exists(filename)
    
    def list_files(self, directory: str) -> List[str]:
        """
        List all files in a directory.
        :param directory: The directory to list files from.
        :return: A list of file names in the directory.
        """

        try:
            return [f for f in listdir(directory) if path.isfile(path.join(directory, f))]
        except Exception as e:
            print(f"Error listing files in directory {directory}: {e}")
            return []

    def clear(self, directory: str) -> None:
        """
        Delete all files in a directory.
        :param directory: The directory to clear files from.
        """

        try:
            for f in self.list_files(directory):
                self.delete(path.join(directory, f))
        except Exception as e:
            print(f"Error clearing files in directory {directory}: {e}")

def sizeof(var: Any) -> int:
    if hasattr(var, '__iter__'):
        l = 0
        for i in var: l += getsizeof(i)
        return getsizeof(var) + l
    else:
        return getsizeof(var)

storage = Storage()

if __name__ == '__main__':
    print(sizeof(storage))
