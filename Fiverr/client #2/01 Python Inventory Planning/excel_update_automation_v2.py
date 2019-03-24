import pandas as pd
import xlwings as xl
import os
import numpy as np
import time

os.chdir('')

###################################################################################
# data import
###################################################################################

# read in the allocation tool
Allocation_tool = pd.ExcelFile('Allocation tool.xlsx')
# 1. 
# read in the Requirements_FPC file : this serves as the raw input
Requirements_FPC = pd.read_excel(Allocation_tool, 'Requirements_FPC')
Requirements_FPC.columns = Requirements_FPC.iloc[1]# set the columns names
Requirements_FPC = Requirements_FPC.drop([0,1]).reset_index().iloc[:,1:]# drop the headers

# Requirements_FPC['Material'].nunique()# Out[23]: 1252
# read in the Requirements explosion
Requirements_explosion = pd.read_excel(Allocation_tool, 'Requirements explosion')
Requirements_explosion.columns = Requirements_explosion.iloc[1][0:3].append(Requirements_explosion.iloc[0][3:])
Requirements_explosion = Requirements_explosion.drop([0,1]).reset_index().iloc[:,1:]
#Requirements_explosion['Component number'].nunique()# Out[29]: 7545
#Requirements_explosion['Parent (Rearranged)'].nunique()# Out[30]: 5156
# aggregate requirements explosion to child
#Requirements_Child = pd.pivot_table(Requirements_explosion, values = Requirements_explosion.columns[3:], index = ['Component number'], aggfunc = np.sum, fill_value = 0)
#start = time.time()
Requirements_Child = Requirements_explosion.groupby(['Component number']).sum()
Requirements_Child = Requirements_Child.drop(columns = ['Parent (Rearranged)','Average of Quantity/Item'])
Requirements_Child['Component number'] = Requirements_Child.index
#end = time.time()
#print(end - start)
Requirements = pd.read_excel(Allocation_tool, 'Requirements')
Requirements.columns = Requirements.iloc[1]
Requirements = Requirements.drop([0,1]).reset_index().iloc[:,1:]
#Requirements.iloc[:,1:][Requirements.iloc[:,1:] != 0] = 0
Requirements = Requirements.fillna(0)
Requirements['Row Labels'] = Requirements['Row Labels'].astype("object")

for i in range(1,15,1):
    for column in Requirements.columns[1:]:
        #filter out the active column as a temporary df
        #inner join Requirements with requirements_FPC and filter out all cases where join did not happen
        #for these cases perform a join with requirements_child
        #append the results and assign back to requirements df
        df = Requirements[column]
    #    Requirements_FPC['Material'] = Requirements_FPC['Material'].astype('int64')
        df = pd.merge(Requirements[['Row Labels',column]],
                      Requirements_FPC[['Material',column]],
                      how='left',
                      left_on = 'Row Labels',
                      right_on = 'Material')[['Row Labels',str(column) + '_y']]
        Requirements_Child['Component number'] = Requirements_Child['Component number'].astype("object")
        df = pd.merge(df,
                      Requirements_Child[['Component number',column]],
                      how = 'left',
                      left_on = 'Row Labels',
                      right_on = 'Component number')    
        df['result'] = df[str(column) + '_y'].fillna(df[column])
        Requirements[column] = df['result']
        del df
        print(column)
    
    #2.
    
    Production = pd.read_excel(Allocation_tool, 'Production')
    Production.columns = Production.iloc[1]
    Production = Production.drop([0,1]).reset_index().iloc[:,1:]
    #Production.iloc[:,1:][Production.iloc[:,1:] != 0] = 0
    
    MOQ_Rounding_Stock = pd.read_excel(Allocation_tool, 'MOQ_Rounding_Stock')
    MOQ_Rounding_Stock.columns = ['Row Labels','MOQ','Rounding value','SS','PDT in Weeks (Rounded)','Total Active Inventory']
    MOQ_Rounding_Stock = MOQ_Rounding_Stock.drop([0]).reset_index().iloc[:,1:]
    
    
    Inventory = pd.read_excel(Allocation_tool, 'Inventory')
    Inventory.columns = Inventory.iloc[3]
    Inventory = Inventory.drop([0,1,2,3]).reset_index().iloc[:,1:]
    
    SafetyStock = pd.read_excel(Allocation_tool, 'SS')
    SafetyStock.columns = Production.columns
    SafetyStock = SafetyStock.drop([0,1]).reset_index().iloc[:,1:]
    
    def production(df):    
        if (df['SafetyStock'] - (df['Inventory'] + df['Requirements'])) <= 0:        
            return 0        
        elif (df['SafetyStock'] - (df['Inventory'] + df['Requirements'])) <= df['MOQ']:        
            return df['MOQ']    
        elif df['Rounding value'] > 0:        
            return round((df['SafetyStock'] - (df['Inventory'] + df['Requirements'])) / df['Rounding value'],0) * df['Rounding value']
        else:
            return (df['SafetyStock'] - (df['Inventory'] + df['Requirements']))
        
    for column in Production.columns[1:]:
        # define temporary df to store all values in column    
        df = Production[['Row Labels',column]]
        df = pd.merge(df,
                   Inventory[['Row Labels',column]],
                   how = 'left',
                   left_on = 'Row Labels',
                   right_on = 'Row Labels')
    #    Requirements['Row Labels'] = Requirements['Row Labels'].astype("object")
        df = pd.merge(df,
                   Requirements[['Row Labels',column]],
                   how = 'left',
                   left_on = 'Row Labels',
                   right_on = 'Row Labels')
        df = pd.merge(df,
                   SafetyStock[['Row Labels',column]],
                   how = 'left',
                   left_on = 'Row Labels',
                   right_on = 'Row Labels')
        df = pd.merge(df,
                   MOQ_Rounding_Stock,
                   how = 'left',
                   left_on = 'Row Labels',
                   right_on = 'Row Labels')
        df.columns = ['Row Labels','Production','Inventory','Requirements','SafetyStock','MOQ','Rounding value','SS','PDT in Weeks (Rounded)','Total Active Inventory']
        Production[column] = df.apply(production, axis = 1)   
        print(column)
    
    #3. 
    def explosion(df):
        global column
        if df['PDT in Weeks (Rounded)'] + column > 52:
            column_production = round(df['PDT in Weeks (Rounded)'] + column,4) - 52 + 0.001
        else:
            column_production = round(df['PDT in Weeks (Rounded)'] + column,4)
        return column_production
    
    def production_offset(df):        
        global Production
        column_production = df['column_production']
        try:
            df = pd.DataFrame.join(pd.DataFrame.transpose(df.to_frame()),
                                   Production[['Row Labels',column_production]],
                                   how = 'left',
                                   lsuffix = 'Parent (Rearranged)',
                                   rsuffix = 'Row Labels')
            production_offset = df[column_production]
        except Exception as e:
            # print(e)
            production_offset = 0
        
        return production_offset
    
    for column in Requirements_explosion.columns[3:]:
        df = Requirements_explosion.loc[:,['Component number','Parent (Rearranged)','Average of Quantity/Item',column]]
        df = pd.merge(df,
               MOQ_Rounding_Stock[['Row Labels','PDT in Weeks (Rounded)']],
               how = 'left',
               left_on = 'Component number',
               right_on = 'Row Labels')
        df = df.drop(columns = 'Row Labels')
        df.columns = ['Component number','Parent (Rearranged)','Average of Quantity/Item','Requirements_explosion','PDT in Weeks (Rounded)']
        df = df.fillna(0)
        df['column_production'] = df.apply(explosion, axis = 1)    
        df['production_offset'] = df.apply(production_offset, axis = 1)    
        Requirements_explosion[column] = df['production_offset']
        print(column)
        Requirements_explosion[column] = Requirements_explosion[column]*Requirements_explosion['Average of Quantity/Item']
        
    Requirements_Child = Requirements_explosion.groupby(['Component number']).sum()
    Requirements_Child = Requirements_Child.drop(columns = ['Parent (Rearranged)','Average of Quantity/Item'])
    Requirements_Child['Component number'] = Requirements_Child.index

    print('Ran {} iteration'.format(i))

Requirements_explosion.to_csv('Requirements explosion.csv')
Requirements_Child.to_csv('Requirements_Child.csv')
Requirements.to_csv('Requirements.csv')
Production.to_csv('Production.csv') 
