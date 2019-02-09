# -*- coding: utf-8 -*-
"""models_python.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BfMX0MzENL8swrw0XnRMuTJwgvwL-CqZ
"""

import pandas as pd
import numpy as np
import keras

#import xgboost

from sklearn.model_selection import train_test_split

from keras.optimizers import Adam

from keras.models import Model

from keras.layers import Activation, Dense, Dropout



from keras.models import Sequential

from keras.wrappers.scikit_learn import KerasRegressor

from sklearn.model_selection import cross_val_score

from sklearn.model_selection import KFold

from sklearn.preprocessing import MinMaxScaler

from sklearn.pipeline import Pipeline

import keras.backend as K

data = pd.read_csv('Modelar_UH2019.txt', sep = '|', encoding = 'utf-8')

data.drop(['HY_id', 'HY_cod_postal', 'HY_descripcion', 'HY_distribucion'], axis = 1, inplace = True)


df = pd.concat([data,pd.get_dummies(data['HY_provincia'], prefix='HY_provincia', drop_first = True)],axis=1)

# now drop the original 'country' column (you don't need it anymore)
df.drop(['HY_provincia'],axis=1, inplace=True)

df = pd.concat([df, pd.get_dummies(df['HY_tipo'], prefix = 'HY_tipo', drop_first = True)], axis = 1)

df.drop(['HY_tipo'], axis = 1, inplace = True)

for columna in df.columns:
    
    if (np.sum(df[columna].isnull()) / df.shape[0]) > 0.3 :
        
        print('la columna ' + str(columna) + ' tiene más de 30% de NAs')
        
        df.drop(columna, axis = 1, inplace = True)
        
    elif (np.sum(df[columna].isnull()) / df.shape[0]) > 0.1:
        
        print('la columna ' + str(columna) + ' tiene más de 10% de NAs')
        
    else:
        
        next
        

df_no_na = df.dropna(axis = 0)

df_no_na.shape
#(5036, 98)

df_no_na['HY_metros_utiles'] = np.log1p(df_no_na['HY_metros_utiles'])

df_no_na['HY_metros_totales'] = np.log1p(df_no_na['HY_metros_totales'])

df_no_na['TARGET'] = np.log1p(df_no_na['TARGET'])

X = np.array(df_no_na.drop('TARGET', axis = 1))

Y = np.array(df_no_na['TARGET']).reshape((5036, 1))

''' No funciona, en Keras no hay medianas

def median_absolute_error(y_true, y_pred):
    
    return K.median(K.abs(y_true-y_pred))

''' 

def GammaTeamEstimator(dropout = 0.2):
  
  
  #Model Creation
  
  model = Sequential()
  
  #first hidden layer
  model.add(Dense(40, input_dim=97, kernel_initializer='normal', activation='relu'))
  
  model.add(Dropout(dropout))
  
  #second hidden layer
  model.add(Dense(20, kernel_initializer = 'normal', activation = 'relu'))
  
  model.add(Dropout(dropout))
  
  #Third hidden layer
  model.add(Dense(10, kernel_initializer = 'normal', activation = 'relu'))
  
  model.add(Dropout(dropout/2))
  
  #Fourth hidden layer (output neuron)
  model.add(Dense(1, kernel_initializer = 'normal'))
  
  #Compile Model. 
  model.compile(loss = "mae",
               optimizer = 'adam')
  
  return model


np.random.seed(1)
estimators = []
estimators.append(('standardize', MinMaxScaler()))
estimators.append(('mlp', KerasRegressor(build_fn=GammaTeamEstimator, epochs=60, batch_size=12, verbose=1)))
pipeline = Pipeline(estimators)
kfold = KFold(n_splits=10, random_state=7)
results = cross_val_score(pipeline, X, Y, cv=kfold)
print("Wider: %.2f (%.2f) Median Absolute Error" % (results.mean(), results.std()))

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2, random_state=7)


model = GammaTeamEstimator()

model.fit(X_train, y_train, epochs = 60, batch_size = 12, verbose = 2)

predicted_y = model.predict(X_test)

def median_absolute_error(y_true, y_pred):
    
    return np.median(np.abs(y_true - y_pred))


median_absolute_error(y_test, predicted_y) #en teoría en el test nos equivocamos sólo en 0.48... pero hay que pasar estos resultados a exp

y_test1 = np.exp(y_test) - 1

y_pred1 = np.exp(predicted_y) -1

median_absolute_error(y_test1, y_pred1) #pero no... aún estamos lejos de conseguir un modelo decente;
#se equivoca muchísimo en términos de segundos... en logsegundos no está mal, pero...

def model2(dropout = 0.2, output_size = 1):
    
    model = Sequential()

    model.add(Dense(80, kernel_initializer = "normal", activation = "relu"))
    
    model.add(Dropout(dropout))
    
    model.add(Dense(40, kernel_initializer = "normal", activation = "relu"))
    
    model.add(Dropout(dropout))
    
    model.add(Dense(20, kernel_initializer = "normal", activation = "relu"))
    
    model.add(Dropout(dropout))
    
    model.add(Dense(10, kernel_initializer = "normal", activation = "relu"))
    
    model.add(Dropout(dropout))
    
    model.add(Dense(output_size))
    
    model.add(Activation("linear"))
    
    model.compile(loss = "mae", 
                  optimizer = "adam")
    
    return model


model2 = model2()

model2.fit(X_train, y_train, epochs = 50, batch_size = 5, verbose = 2)

predicted = np.exp(model2.predict(X_test)) -1 

median_absolute_error(y_test1, predicted) #malísimo de momento...


scaler = MinMaxScaler()

scaled_df = scaler.fit_transform(df_no_na)

scaled_df = pd.DataFrame(scaled_df, columns = df.columns)

X = np.array(scaled_df.drop('TARGET', axis = 1))

Y = np.array(scaled_df['TARGET']).reshape((5036, 1))

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2, random_state=7)


model2.fit(X_train, y_train, epochs = 50, batch_size = 8, verbose = 2)

predicted = model2.predict(X_test)




'''
## XG Boost

xgb = xgboost.XGBRegressor(colsample_bytree=0.4,
                 gamma=0,                 
                 learning_rate=0.07,
                 max_depth=3,
                 min_child_weight=1.5,
                 n_estimators=10000,                                                                    
                 reg_alpha=0.75,
                 reg_lambda=0.45,
                 subsample=0.6,
                 seed=42) 

X_train, y_train, X_test, y_test = train_test_split(X, Y, test_size = 0.2, random_state = 7)

'''

'''
xgb.fit(train_dataset[every_column_except_y],train_dataset['SalePrice'])

OrderedDict(sorted(model.booster().get_fscore().items(), key=lambda t: t[1], reverse=True))
'''