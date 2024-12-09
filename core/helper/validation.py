
import pandas as pd
import json
from helper.helper import remove_characters, contain_all_key_words, df_to_JSON


def core_validation(cPath):
    """
    Applies duplicate check and hierachy clean up then saves back 
    to the initial file

    cPath = path to the initial files
    """  

    df = pd.read_json(cPath)

    df = initial_title_check(df)
    df = hierachy_clean_up(df)
    
    results = df_to_JSON(df)

    with open(cPath, 'w') as f:
        json.dump(results, f, indent=4)


# check that the whole search term is in the title
def initial_title_check(df):
    """
    Cleans up the titles returned from ebay

    df = dataframe
    """  

    df["clean-title"] = df["title"].str.lower() 
    df["clean-title"] = df["clean-title"].apply(lambda x: remove_characters(x))
    df["clean-model"] = df["model"].str.lower() 
    df["clean-model"] = df["clean-model"].apply(lambda x: remove_characters(x))

    df["valid"] = df.apply(lambda x: contain_all_key_words(x["clean-title"], \
                           x["clean-model"].lower()), axis=1)

    filtered_df = df[df["valid"] == True]
    
    return filtered_df


def hierachy_clean_up(df):
    """
    Cleans up duplicate id ebay records using hierachy


    df = dataframe  
    """  

    df_uniques    = df.drop_duplicates(['id'])
    df_duplicates = df[df.duplicated(['id'])]

    result_df = df_duplicates[df_duplicates["priority"] != 1]

    iCount = 1
    while len(result_df) > 0:
        iCount = iCount + 1
        
        #get remaining unique
        df_temp_unique  = result_df.drop_duplicates(['id'])
        df_uniques = pd.concat([df_uniques,df_temp_unique])
        
        # get duplicates and clean up this new list
        df_duplicates = result_df[result_df.duplicated(['id'])]
        result_df     = df_duplicates[df_duplicates["priority"] != iCount]

    return df_uniques


def pre_search_validation(oData):
    """
    Applies duplicate check and hierachy clean up then saves back 
    to the initial file

    oData = initial file data (this could just be the path) 
    """  

    df = pd.DataFrame(data=oData["items"])
    df = remove_duplicates(df)
    df = auto_generate_priority(df)

    oData["items"] = df_to_JSON(df)
    
    return oData


def remove_duplicates(df):
    """
    remove duplicate search terms


    df = dataframe
    """  

    df_uniques    = df.drop_duplicates(['model'])
    df_duplicates = df[df.duplicated(['model'])]

    if len(df_duplicates) > 0:
        aUniqueItem = list(set(df_duplicates['model'].tolist()))

        for model in aUniqueItem:

            df_uniques = pd.concat([df_uniques, df[df['model'] == model].iloc[0]])

    return df_uniques


def remove_common_items(aList1, aList2):
    """
    Remove common words in lists


    aList1  = list of words
    aList2  = list of words
    """  

   
   # Convert lists to sets to find the intersection (common elements)
    common_items = set(aList1) & set(aList2)
    
    # Remove the common items from both arrays
    aList1 = [item for item in aList1 if item not in common_items]
    aList2 = [item for item in aList2 if item not in common_items]
    
    return aList1, aList2

def find_partial_match(aInit, aCheck):
    """
    A more complex version of the subset check that we have but it handles 
    partial word matches too


    aInit   = load path
    aCheck  = save path
    """  

    if len(aCheck) > len(aInit):
        return False


    for cCheck in aCheck:
        for cInit in aInit:
            bHit = False
            if cCheck in cInit: 
                bHit = True
                aInit.remove(cInit)
        if not bHit:
            return False

    return True 

def check_priority(cString1, cString2):
    """
    Checks whether the priority should be incremented 


    cString1  = load path
    cString2  = save path
    """  

    aInit, aCheck = remove_common_items(cString1.split(" "),cString2.split(" "))
    if len(aCheck) == 0:
        return True 
    else:
        return find_partial_match(aInit, aCheck)


def auto_generate_priority(df):
    """
    Dynamically generates the priority based on search terms


    df = dataframe
    """  

    dfClone = df.copy(deep=True)

    for idx, row in df.iterrows():
        iPriority = 1
        for previous_idx in range(idx):
            
            if check_priority(row['model'], df.loc[previous_idx, 'model']) \
            and iPriority < df.loc[previous_idx, 'priority'] + 1:
                
                iPriority = df.loc[previous_idx, 'priority'] + 1
        dfClone.at[idx, 'priority'] = iPriority

    return dfClone