import pandas as pd
import json
from helper.helper import df_to_JSON


def set_box_plot_data(cEbayFullPath, cSaveFullPath):
    """
    orders data for box plot

    cEbayFullPath  = load path
    cSaveFullPath  = save path
    """  


    df = pd.read_json(cEbayFullPath)

    aUniqueItem = list(set(df['model'].tolist()))
    aConditions = ["Pre-owned","Parts only","Opened – never used","Brand new",\
                   "Great condition","New (other)","Very Good - Refurbished",\
                   "Excellent - Refurbished"]
    oFinalData = {
        "datasets": {}
    }

    for item in aUniqueItem:
        dfResult = df[df["model"] == item]
        for condition in aConditions:
            dfResult2 = dfResult[dfResult["condition"] == condition]

            if len(dfResult2) > 2:

                oVal = { 
                    "name": condition,
                    "value":dfResult2["price"].tolist()
                    }
                cItemName = item.replace(" ","-")
                
                if not hasattr(oFinalData["datasets"], cItemName):
                    oFinalData["datasets"][cItemName] = []
                oFinalData["datasets"][cItemName].append(oVal)

    with open(cSaveFullPath, 'w') as json_file:
        json.dump(oFinalData, json_file, indent=4)



def set_statistics(cEbayFullPath,cSaveFullPath):
    """
    groups data by condition and provides some pretty standard metrics


    cEbayFullPath  = load path
    cSaveFullPath  = save path
    """  


    df = pd.read_json(cEbayFullPath)

    aStats       =  []
    df_unique    = df.drop_duplicates(['model'])["model"].tolist()
    fMinProfit   = 0.3

    for sModel in df_unique:
        df_model = df[df["model"] == sModel]
        aConditions  = df_model.drop_duplicates(['condition'])["condition"].tolist()

        for sCond in aConditions:
            df_condition = df_model[df_model["condition"] == sCond]
            if len(df_condition) > 2:

                oValues = df_condition["price"].describe()

                dIQR                 = (oValues["75%"] - oValues["25%"]) * 0.5

                df_condition         = df_condition[df_condition["price"] > oValues["25%"] - dIQR ]
                df_condition         = df_condition[df_condition["price"] < oValues["75%"] + dIQR] 
                oValues              = df_condition["price"].describe()
                if oValues["count"] > 2:
                    oValues["listPrice"] = round(oValues["mean"] / 0.8, 2)
                    oValues["minProfit"] = round(oValues["mean"] * fMinProfit,2)
                    oValues["buyPrice"]  = round(oValues["mean"] * (1 - fMinProfit),2)
                    oValues["condition"] = sCond
                    oValues["model"]     = sModel
                    aStats.append(oValues)

    df = pd.DataFrame(aStats)

    with open(cSaveFullPath, 'w') as json_file:
        json.dump(df_to_JSON(df), json_file, indent=4)