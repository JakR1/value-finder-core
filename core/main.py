import json

from helper.helper     import get_JSON, create_path
from helper.pricedata  import create_historical_sales_JSON
from helper.validation import core_validation, pre_search_validation
from helper.stats      import set_box_plot_data, set_statistics

bPreCheck        = True
bFreshData       = True
bApplyCleanUp    = True
bPriceAnalysis   = True
cEbayPath        = "./ebay-results/"
cInitialFilePath = "./initial-file/"
cStatFolder      = "./stats/"
cInitialFileName = "demo-file.json" 
cSaveDataPath    = "./boxplot/"
cSaveFileName    = "demo-file.json"

#checks if path exists and if it doesn't then it creates it

oData        = get_JSON(cInitialFilePath + cInitialFileName)
cSearchTerms = oData["coresearchterms"]
cFullPath    = cEbayPath 

aPathList = [cEbayPath, cInitialFilePath, cStatFolder, cSaveDataPath]

for cPath in aPathList:
    create_path(cPath)


if bPreCheck:

    oData = pre_search_validation(oData)
    with open(cInitialFilePath + cInitialFileName, 'w') as json_file:
        json.dump(oData, json_file, indent=4)


if bFreshData:

    cEbayFullPath = f"{cEbayPath + cInitialFileName.replace('.', '-ebay.')}"
    create_historical_sales_JSON(oData, cSearchTerms, cEbayFullPath)


if bApplyCleanUp:

    #keyword check for data
    cPath = cEbayPath + cInitialFileName.replace('.', '-ebay.')
    core_validation(cPath)


#Additional logic 
if bPriceAnalysis:

    cEbayFullPath = f"{cEbayPath + cInitialFileName.replace('.', '-ebay.')}"
    cSaveFullPath = cSaveDataPath + cSaveFileName

    set_box_plot_data(cEbayFullPath, cSaveFullPath)
    set_statistics(cEbayFullPath, cStatFolder + cSaveFileName)

