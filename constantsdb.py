import pandas as pd
import numpy as np
from difflib import get_close_matches

class ConstantsDB:

    '''Class contains a tree of three levels. Topmost level contains two topmost nodes: math and phys.
    Second level contains subdivisions of math or phys. The third level contains leafs \
    which are values of constants.'''

    def __init__(self):

        self.db_df             = self.__load_database__()                    
        self.df_possible_names = self.__load_possible_names_df__()
        self.possible_names    = self.df_possible_names.name.to_list()
        self.db_df.drop(columns=['alternative_names'], inplace = True)
        
    def __load_database__(self):
        
        db_df   = pd.read_csv('data/constants.csv', skiprows=5)
        # copying id into index to use it in searches
        # while keeping id as a column makes it easy to use it in data extraction
        db_df.index = db_df.id
        db_df = db_df.fillna(value='') # replace NaNs with empty string
        return db_df

    def __load_possible_names_df__(self):

        df = self.db_df
        data = []
        columns = ['id', 'name']
        for id in df.id:
            name = df.loc[id,'name']
            data.append(dict(zip(columns,[id, name.strip().lower()])))
            
            alternative_names = df.loc[id,'alternative_names'].strip()
            if alternative_names == '':
                continue
            
            alternative_names = alternative_names.split(',')
            for name in alternative_names:
                data.append(dict(zip(columns,[id, name.strip().lower()])))
                    
        return pd.DataFrame(data)

    def get_item(self, id):
        
        id = id.strip()
        
        if np.any(self.db_df.id==id):
            df = self.db_df[self.db_df.id==id].head(1)
            return {col:df.loc[:,col].values[0] for col in df.columns}
        
        return None

    def get_children(self, parent_id):
        
        parent_id = parent_id.strip()

        if np.any(self.db_df.parent_id==parent_id):
            df = self.db_df[self.db_df.parent_id==parent_id]
            return [{col:df.loc[idx,col] for col in df.columns} for idx in df.index]
        
        return None
        
    def get_first_level_parents(self):
        
        df = self.db_df[self.db_df.parent_id == ''].sort_values('name')
        return [{col:df.loc[idx,col] for col in df.columns} for idx in df.index]

    def search(self, name):
        """Search constant by its name. The closest match is returned."""

        name = name.lower().strip()
        exact_names = get_close_matches(name, self.possible_names, n=1)
        if not exact_names:
            return None
        else:
            exact_name = exact_names[0]
            id = self.df_possible_names[self.df_possible_names['name'] == exact_name].index[0]        
            return self.df_possible_names.loc[id, 'id']
