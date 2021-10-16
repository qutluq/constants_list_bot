def is_constant(const):
    '''returns True if const is constant, False if it const is folder
    
    const is a dict with the following keys: 
    {'id': 'math',  'name': 'Mathematics',  'parent_id': '',  \
        'value': '',  'unit': '', 'unit_system': ''}
    '''

    return const['value'] != ''

def is_root_node(const):
    '''Returns True if const in the topmost level folder, False otherwise.
    
    const is a dict with the following keys: 
    {'id': 'math',  'name': 'Mathematics',  'parent_id': '',  \
        'value': '',  'unit': '', 'unit_system': ''}
    '''

    return const['parent_id'] == ''