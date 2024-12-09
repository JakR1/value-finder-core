import json
from os import path, makedirs

def bulk_replace(cString, aList, cReplace):
    """ 
    Replace many different characters in a string.

    cString  = The string that is having characters replaced
    aList    = A list of characters that will be replaced
    cReplace = What the character will be replaced with

    """ 

    for cRemove in aList:
        cString = cString.replace(cRemove, cReplace)

    return cString


def remove_additional_white_space(cString):
    """    
    Replaces multiple spaces with a single space

    cString  = The string that is having spaces removed
    """ 
    cPreString = ""
    while len(cPreString) != len(cString): 
        cPreString = cString
        cString = bulk_replace(cString,["  "]," ")
    
    #I think that I might need a strip left and right 
    #to be sure we have a clean string after this function

    return cString


def remove_characters(cString):
    """
    Replaces the list of characters below from a string.
    The list is what I found to work best for the search and validation 

    cString  = The string that is having characters removed
    """ 

    aRemove = [",","*","(",")","[","]","...",":"]
    aReplace = ["+","- ",". ","& ","w/ ","– ","-","–"]

    cString = bulk_replace(cString,aRemove,"")
    cString = bulk_replace(cString,aReplace," ")

    cString = remove_additional_white_space(cString)
    return cString

#Checks that the title has all words in the search term
def contain_all_key_words(cString1, cString2):
    """
    Checks if cString1 contains all the words of cString2
    returns True or False  

    cString1 = larger number of words
    cString2 = smaller number of words
    """

    aWords1 = set(cString1.lower().split())
    aWords2 = set(cString2.lower().split())

    return aWords1.issubset(aWords2)


def format_shipping(cShipping):
    """
    Returns the shipping price as a string


    cShipping = string returned from ebays shipping value
    """

    #Note this will fall over if it isn't run on the english site
    if len(cShipping.split("Free")) > 1 or "£" not in  cShipping:
        cShipping = "0"
    else:
        cShipping = cShipping.split("£")[1].split(" ")[0]
    
    return cShipping


def format_price(cPrice):
    """
    Returns the price as a string

    
    cPrice = string returned from ebays price value
    """

    if len(cPrice.split("£")) == 1:
        return "FAILED"
    
    return cPrice.split("£")[1].replace(",","")


def get_id(cLink):
    """
    Returns the id of the ebay item

    
    sLink = string returned from ebays URL for the item
    """

    cId =  cLink.split("itm/")[1].split("?")[0] 
    
    return cId

# This seems pretty dumb and I'm not sure why I need to do it this way.
# there should be something built in for this
def df_to_JSON(df):
    """
    This changes a dataframe to JSON format 
    
    df = dataframe
    """

    aResults = "[" + df.to_json(orient='records', lines=True).replace("}","},") \
            + "]"
    aResults = aResults.replace("},\n]","}\n]") 
    return  json.loads(aResults)


def valid_float(cString):
    """
    returns if the cString is a valid float
    
    cString = generic string
    """

    try:
        float(cString)
        return True
    except ValueError:
        return False


def is_valid_soup(oHtml):
    """
    returns if the oHtml is a valid beautifulsoup object

    oHtml = object returned from beautifulsoup
    """

    if oHtml != None:
        return oHtml
    else:
        return "invalid"


def create_path(cPath):
    """
    Creates file path if it doesn't exist already exist

    sPath = file path
    """

    bExist = path.exists(cPath)
    if not bExist:
        makedirs(cPath)


def get_JSON(sFileName):
    """
    Returns object from JSON file

    sFileName = file path and file name
    """

    with open(sFileName, 'r') as file:
        # Load the JSON data
        oData = json.load(file)
    return oData