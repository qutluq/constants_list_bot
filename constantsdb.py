import pandas as pd
import numpy as np

class ConstantsDB:

    '''Class contains a tree of three levels. Topmost level contains two root nodes: math and phys.
    Second level contains subdivisions of math or phys. The third level contains leafs \
    which are values of constants.'''

    def __init__(self):

        self.db_df   = pd.read_csv('data/constants.csv', skiprows=5)
        # copying id into index to use it in searches
        # while keeping id as a column makes it easy to use it in data extraction
        self.db_df.index = self.db_df.id
        self.db_df = self.db_df.fillna(value='') # replace NaNs with empty string

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
        """Search constant by its name"""

        pass