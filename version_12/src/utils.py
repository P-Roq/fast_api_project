import os
import sys
import re
from passlib.hash import bcrypt
from passlib.context import CryptContext

# Defining the hashing algorithm for the passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto',)

def hash_pw(password: str):
    return pwd_context.hash(password)

def validate_pw(user_input_password, stored_hashed_password):
    validation = bcrypt.verify(user_input_password, stored_hashed_password)
    return validation

def capitalize_names(input_string):
    input_string = re.sub('_', ' ', input_string)
    words = input_string.split()
    capitalized_words = [word.capitalize() for word in words]
    result = ' '.join(capitalized_words)
    return result


def get_parent_directory(depth: int, insert_path: bool) -> str:
    current_directory = os.getcwd()

    # Split the directory path into individual components
    components = current_directory.split(os.sep)
    
    total_components = len(components)

    if depth > total_components:
        raise Exception(f'The number of child folders to skip ({depth}) cannot be equal or superior to the total number of folders in the directory ({total_components}).')

    # Calculate the new path based on the specified depth
    new_path = os.sep.join(components[:-depth] if depth > 0 else components)

    if insert_path:
        sys.path.insert(0, new_path)

    if (total_components - depth) == 1:
        return '/'
    else:
        return new_path
    

