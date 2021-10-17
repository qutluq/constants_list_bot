def is_constant(const):
    '''returns True if const is constant, False if it const is folder
    
    const is a dict with the following keys: 
    {'id': 'math',  'name': 'Mathematics',  'parent_id': '',  \
        'value': '',  'unit': '', 'unit_system': ''}
    '''
    if const == None:
        return None

    return const['value'] != ''

def is_topmost_node(const):
    '''Returns True if const in the topmost level folder, False otherwise.
    
    const is a dict with the following keys: 
    {'id': 'math',  'name': 'Mathematics',  'parent_id': '',  \
        'value': '',  'unit': '', 'unit_system': ''}
    '''
    if const == None:
        return None

    return const['parent_id'] == ''

def get_menuitems_id(menu_items, item_name):
    '''return id of `item_name` string if it is present in menu_items list'''
    
    names = [item['name'].lower() for item in menu_items]
    ids   = [item['id'] for item in menu_items]
    
    try:
        idx = names.index(item_name.lower())
    except:
        return None
    
    return ids[idx]