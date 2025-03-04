import pandas as pd

# NOTA: Algunas de estas cosas ya existen en mejores formas de hacerlo, pero las descubrí en clase después.
#       Parece que redescubrí el hilo negro :S
#       No me arrepiento de haber hecho esto, lo más seguro es que no lo use más en adelante, pero lo dejo 
#       porque al final de cuentas fue mi esfuerzo

## Detectar outliers de una columna usndo Método del rango intercuartílico (IQR)
def detectOutliers (df, column):
    # Primero comprobamos que todo sea numerico
    for val in df[column]:
        if not isinstance(val, (int, float, complex)) or isinstance(val, bool):
            return []
        
    
    # obtenermos los quartiles inferior y superior
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    # Definir los límites inferior y superior
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identificar los outliers
    outliers = ((df[column] < lower_bound) | (df[column] > upper_bound)).tolist()
    if True in outliers:
        return [i for i,x in enumerate(outliers) if x==True] #outliers.count(True)
    return []

def analisisDF(df, minRate = 0.8):
    model_cols = df.columns.tolist()
    resultMap = {
        "duplicateCols": [],
        "similarCols": [],
        "containsCols": [],
        "formatInconsitenceCols": [],
        "tooManyNanCols": [],
        "proportionalCols": [],
        "outliersCols": [],
        "uniqueCols":[]
    }
    for col in model_cols:
        # tooManyNanCols
        alist = df[col].tolist()
        nanCount = sum(df[col].isnull().tolist())
        if nanCount / len(alist) > minRate:
            resultMap["tooManyNanCols"].append({"col":col,"rate":nanCount / len(alist)})
        
        # formatInconsitenceCols
        dataType = None
        for element in alist:
            if not dataType:
                dataType = type(element)
            if type(element) != dataType:
                resultMap["formatInconsitenceCols"].append({"col":col,"types":str(dataType)+"|"+str(type(element))})
                break
        
        # outliersCols
        outliers = detectOutliers(df,col)
        if len(outliers) > 0:
            resultMap["outliersCols"].append({"col":col,"outliersIndex":str(outliers)})

        # uniqueCols
        unCols = df[col].unique()
        uniqueRate = len(unCols)/len(df[col])
        if(uniqueRate <= 1-minRate):
            resultMap["uniqueCols"].append({"col":col,"unique rate":str(uniqueRate),"vals":df[col].value_counts().to_json(orient="index")})
        
        for col2compare in model_cols[model_cols.index(col)+1:]:
            if(col != col2compare):
                list1 = df[col].tolist()
                list2 = df[col2compare].tolist()
                
                # duplicateCols
                if(list1 == list2):
                    resultMap["duplicateCols"].append({"cols":col, "col2":col2compare})
                
                # similarCols
                count = 0
                count += sum(map(lambda x, y: 1 if str(x)==str(y) else 0 , list1, list2))
                if count / len(list1) > minRate:
                    resultMap["similarCols"].append({"cols":col, "col2":col2compare,"rate":count / len(list1)})
                
                # containsCols
                containsCount = 0
                containsCount += sum(map(lambda x, y: 1 if str(x).find(str(y)) != -1 or str(y).find(str(x)) != -1 else 0 , list1, list2))
                if containsCount / len(list1) > minRate:
                    resultMap["containsCols"].append({"cols":col, "col2":col2compare,"rate":containsCount / len(list1)})
                
                # proportionalCols
                proportion = None
                areAllProportion = False
                for i in range(len(list1)):
                    x = list1[i]
                    y = list2[i]
                    if isinstance(x, (int, float, complex)) and not isinstance(x, bool) and isinstance(y, (int, float, complex)) and not isinstance(y, bool):
                        if not proportion:
                            proportion = 0 if y == 0 else x /y
                            areAllProportion = True
                        if y == 0 or proportion != x / y:
                            areAllProportion = False
                            break
                if areAllProportion:
                    resultMap["proportionalCols"].append({"cols":col, "col2":col2compare, "proportion":proportion})
    return resultMap