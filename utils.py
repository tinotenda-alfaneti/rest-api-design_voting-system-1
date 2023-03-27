import json

def write_to_file(filename, data):
    '''Write data to file'''
    with open(filename, 'w') as f:
        f.write(json.dumps(data, indent=2))


def data_to_json(filename):
     '''Turn data in file to json'''
     with open(filename, 'r') as f:
        data = f.read()
        return json.loads(data)

def read_to_create(filename, data):
    '''Read a file for creating a user. The file can be empty'''
    wasEmpty = False
    with open(filename, 'r') as f:
        file_data = f.read()
    if not file_data:
        wasEmpty = True
        return ([data], wasEmpty)
    else:
        return (json.loads(file_data), wasEmpty)
    
def id_checker(filename, id, id_name):
    '''check if id exists in file'''
    with open(filename, 'r') as f:
        voters_data = f.read()
        if not voters_data:
            return False
        records = json.loads(voters_data)
        for r in records:
            if r[id_name] == id:
                return True
        return False
