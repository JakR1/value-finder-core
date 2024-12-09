
import requests
from bs4 import BeautifulSoup
import json
from helper.helper import format_price, format_shipping, get_id, valid_float, \
                          is_valid_soup
import math


def get_ebay_sold_list_data(cSearch, iPriority):
    """
    Returns a list of ebay sold objects

    cSearch   = String used for search
    iPriority = Priority of the search
    """

    results = []
    results = generic_ebay_search(cSearch, bSold=True, iPriority=iPriority)

    return results

#This could be more thought full or cleaner
def generate_search_string(cSearch,
    cSortType ="Bestmatch", cCondition = "", bSold=False,
    iPage=1):
    """
    Returns the URL for ebay dependant on the input conditions

    cSearch    = String that we are searching with
    cSortType  = "Bestmatch","Ending soonest" or "lowest Price" 
    cCondition = "parts" or "" which is everything else
    bSold      = This decides if you are getting current listings or sold ones
    iPage      = This is the page of results you want returning
    """

    if bSold:
        cSoldVal =  "&LH_Sold=1&LH_Complete=1"
    else:
        cSoldVal = ""

    if iPage == 1:
        cPage = ""
    else:
        cPage = "&_pgn=" + str(iPage)

    if cCondition == "parts":
        cCondition = "&LH_ItemCondition=7000"
    else:
        cCondition = "&LH_ItemCondition=1000%7C1500%7C2010%7C2020%7C2030%7C3000"

    if  cSortType == "Bestmatch":
        cSortType = "&_sop=12"
    elif cSortType == "Ending soonest":
        cSortType = "&_sop=1"
    else:
        cSortType = "&_sop=15" 


    cURL = f"https://www.ebay.co.uk/sch/i.html?" + \
           f"_nkw={cSearch.replace(' ', '+')}" + \
           f"&_sacat=0{cSortType}&rt=nc{cCondition}{cSoldVal}&_ipg=240{cPage}"

    return cURL


def get_page_soup(cURL):
    """
    Returns the soup object

    cURL = site url for the soup object
    """

    oResponse = requests.get(cURL)
    oSoup     = BeautifulSoup(oResponse.content, 'html.parser')
    return oSoup

def get_max_pages(oSoup):
    """
    Returns int that is the number of results we can possibly get
    from search results

    oSoup = soup object ebay search results
    """

    cString = oSoup.find('h1', class_='srp-controls__count-heading').get_text()

    if "+" in cString:
        cString = cString.split("+ results for")[0] 
    elif "results" in cString:
        cString = cString.split(" results for")[0] 
    else:
        cString = cString.split(" result for")[0] 

    return int(cString.replace(",",""))



def get_data_from_page(cSearch, oSoup, iPriority):
    """
    Returns the sorted item data from the Soup object

    cSearch   = the search term used to get this result
    oSoup     = soup object ebay search results
    iPriority = the priority of the search terms
    """
    aResults = []
    oListings = oSoup.find_all('li', class_='s-item')

    for oItem in oListings:

        oTitle     = oItem.find('div', class_='s-item__title')
        oPrice     = oItem.find('span', class_='s-item__price')
        oShipping  = oItem.find('span', class_='s-item__shipping')
        oCondition = oItem.find('div', class_='s-item__subtitle')
        oTime      = oItem.find('span', class_='s-item__time')
        bOffer     = oItem.find('span', class_='s-item__formatBestOfferEnabled')
        bBuyItNow  = oItem.find('span', class_='s-item__formatBuyItNow')

        cTime     = oTime.get_text() if oTime else 'N/A'
        bBuyItNow = True if bBuyItNow else False
        bOffer    = True if bOffer    else False
        if bOffer:
           bBuyItNow = True 


        oImageBlock = is_valid_soup(oItem.find('div', class_='s-item__image'))

        if oImageBlock == "invalid":
            cLink     =  "invalid"
            cId       =  "invalid"
        else:
            cLink     = is_valid_soup(oImageBlock.find('a'))
            cLink     = cLink.get('href')
            cId       = get_id(cLink)

        if "invalid" == is_valid_soup(oShipping):
            cShipping = ""
        else:
            cShipping  = format_shipping(oShipping.get_text())
        cPrice     = format_price(oPrice.get_text())
        if valid_float(cPrice) and valid_float(cShipping) and oTitle: 
            dPrice = round(float(cPrice) + float(cShipping), 2)       
            
            aResults.append({
                'id': cId,
                'link': cLink,
                'title': oTitle.get_text(),
                'price': dPrice,
                'time': cTime,
                'buyItNow': bBuyItNow,
                'offer': bOffer,
                'condition': valid_condition(oCondition.get_text() \
                                             if oCondition else 'N/A'),
                'model': cSearch,
                'items': [],
                'priority': iPriority
            })

    return aResults

def generic_ebay_search(cSearch, 
    cSortType ="Bestmatch", cCondition = "", bSold=False, iPage=1, 
    iPriority=1):
    """
    This is a natural extension of generate_search_string where you can get data
    from multiple pages

    cSearch    = String that we are searching with
    cSortType  = "Bestmatch","Ending soonest" or "lowest Price" 
    cCondition = "parts" or "" which is everything else
    bSold      = This decides if you are getting current listings or sold ones
    iPage      = This is the page of results you want returning
    """

    aResults = []
    iMaxResults = 0
    iTotalPages = 0

    cURL  = generate_search_string(cSearch, cSortType, cCondition, bSold, iPage)
    
    oSoup = get_page_soup(cURL)
    iMaxResults = get_max_pages(oSoup)

    if iPage == "all":
        if iMaxResults % 240  > 0:
            iTotalPages = math.floor(iMaxResults / 240) + 1
        else:
            iTotalPages = math.floor(iMaxResults / 240)
        
    aResults = get_data_from_page(cSearch, oSoup, iPriority)

    if iPage == "all":
        for iPageNum in range(iTotalPages):
            
            if iPageNum > 1:
                cURL     = generate_search_string(cSearch, cSortType, \
                                                  cCondition, bSold, iPageNum)
                oSoup    = get_page_soup(cURL)
                aResults = aResults + get_data_from_page(cSearch, oSoup, \
                                                         iPriority) 
    
    return aResults


def generate_search_term_list(oData,cSearchTerms):
    """
    Generates the list of search terms for the ebay 

    oData         = The list of initial data
    cSearchTerms  = String that we are searching with 
    """
    aSearchTermsList = []
    for oItem in oData["items"]:
        if cSearchTerms == "":
            aSearchTermsList.append({"model":oItem["model"],
                                    "priority":oItem["priority"]}) 
        else:
            aSearchTermsList.append({"model": cSearchTerms + " " \
                                     + oItem["model"],
                                     "priority":oItem["priority"]})
            
    return aSearchTermsList

def create_historical_sales_JSON(oData,cSearchTerms,cEbayFullPath):
    
    """
    Gets historical sales and save to a JSON 

    oData         = The list of initial data
    cSearchTerms  = String that we are searching with
    sEbayFullPath = save path

    """

    aResults = []
    aSearchTermsList = generate_search_term_list(oData,cSearchTerms)
    aResults = update_historic_sales(aSearchTermsList)

    with open(cEbayFullPath, 'w') as json_file:
        json.dump(aResults, json_file, indent=4)




def update_historic_sales(aSearchTerms):
    """
    Gets historical sales and save to a JSON 

    aSearchTerms  = The list of initial data
    """  

    aResults = []
    for oModel in aSearchTerms:
    
        aResults = aResults + get_ebay_sold_list_data(oModel["model"], \
                                                      oModel["priority"])

    return aResults



def valid_condition(cCondition):
    """
    Cleans up the conditions and sets any that are custom to Pre-owned

    cCondition  = conditions
    """  


    aConditions = ["Pre-owned", "Parts only", "Opened – never used", \
                   "Brand new", "Great condition", "New (other)", \
                   "Very Good - Refurbished", "Excellent - Refurbished"]
   
    if cCondition in aConditions:
        return cCondition
    else:
        return "Pre-owned"


