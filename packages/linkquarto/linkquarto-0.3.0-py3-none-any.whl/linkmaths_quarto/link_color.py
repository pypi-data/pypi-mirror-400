from importlib import resources
import io 

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score

import seaborn as sns
from bokeh.plotting import *
from bokeh.model import *
from bokeh.transform import *


def kpi(estimateur,X_train,X_test,y_train,y_test,nb_cv):
    """
    Cette fonction calcule les accuracy pour l'estimateur et les données
    passé en paramètre
    """
    score_cv_train= cross_val_score(estimator=estimateur,
                                X=X_train,
                                y=y_train,
                                cv=nb_cv)

    score_cv_test = cross_val_score(estimator=estimateur,
                                    X=X_test,
                                    y=y_test,
                                    cv=nb_cv)

    print("Moyenne du score obtenus")
    print("random forest : accuracy sur train {} +/- {}".format(np.round(score_cv_train.mean(),2),
                                                                np.round(score_cv_train.std(),2)))

    print("random forest : accuracy sur test  {} +/- {}".format(np.round(score_cv_test.mean(),2),
                                                                np.round(score_cv_test.std(),2)))




def mat_conf2(y_train, y_pred_train,y_test, y_pred_test,couleur):
    """
    Cette fonction affiche sous forme de graphique la matrice de confusion
    """
    
    figs, ax = plt.subplots(figsize=(12, 6), nrows=1, ncols=2)
    figs.tight_layout(pad=10)
    cf_matrix = confusion_matrix(y_train, y_pred_train,)
    group_names = ["VN","FP","FN","VN"]
    group_counts = ["{}".format(np.round(value,2)) for value in
                    cf_matrix.flatten()]
    group_percentages = ["{}%".format(100*np.round(value,2)) for value in
                        cf_matrix.flatten()/np.sum(cf_matrix)]
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
            zip(group_names,group_counts,group_percentages)]
    labels = np.asarray(labels).reshape(2,2)
    f1 = sns.heatmap(cf_matrix, annot=labels, fmt="", cmap=couleur,ax=ax[0])
    f1.set(xlabel="Prédiction",ylabel="Obsertation")
    f1.set_title("Matrice de confusion sur train")

    cf_matrix2 = confusion_matrix(y_test, y_pred_test)
    group_names2 = ["VN","FP","FN","VN"]
    group_counts2 = ["{}".format(np.round(value,2)) for value in
                    cf_matrix2.flatten()]
    group_percentages2 = ["{}%".format(100*np.round(value,2)) for value in
                        cf_matrix2.flatten()/np.sum(cf_matrix2)]
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
            zip(group_names2,group_counts2,group_percentages2)]
    labels = np.asarray(labels).reshape(2,2)
    f2 = sns.heatmap(cf_matrix2, annot=labels, fmt="", cmap=couleur,ax=ax[1])
    f2.set(xlabel="Prédiction",ylabel="Obsertation")
    f2.set_title("Matrice de confusion sur train")

def plot_auc(y_test, proba,indice,fig):
    """
    Cette fonction calcule et trace la courbe de l'auc

    """
    fpr, tpr, seuils = roc_curve(y_test, 
                            proba[:,1],
                            pos_label=1)

    roc_auc = auc(fpr,tpr)
    print("La valeur de l'AUC est de : {}".format(roc_auc))

    
    ax = fig.add_subplot(1,2,indice)
    ax.plot(fpr,
            tpr,
            linewidth=3,
            color="#00946D", 
            label = "(AUC = {})".format(np.round(roc_auc,2)))
    ax.set_xlabel("Taux de faux positifs", size=15)
    ax.set_ylabel("Taux de vrais positifs", size=15)
    ax.set_title("Courbe ROC", size = 20)
    ax.set_xlim(0,1)
    ax.set_ylim(0,1.05)
    ax.legend(loc="lower right")


def preprocessing_test(data):
    """
    Cette fonction reprend toute les transformation appliquées sur les données trains pour les répliquer 
    sur le jeu test.
    Nous procédons ainsi car l'objectif du notebook est de faire une étude détaillée en
     vue de la publié éventuellement sur le site
    """    

    # données manquantes
    col_cat = data.columns[data.dtypes=="object"]
    col_nums = data.columns[data.dtypes!="object"]

    data.loc[data.CryoSleep==True,col_nums.drop("Age")] = 0

    data.CryoSleep.fillna(data.CryoSleep.mode(),inplace=True)
    data.HomePlanet.fillna(data.HomePlanet.mode(),inplace=True)
    data.Cabin.fillna(data.Cabin.mode(),inplace=True)
    data.Destination.fillna(data.Destination.mode(),inplace=True)
    data.VIP.fillna(data.VIP.mode(),inplace=True)


    data.Age.fillna(data.Age.median(),inplace=True)
    data.RoomService.fillna(data.RoomService.median(),inplace=True,)
    data.FoodCourt.fillna(data.FoodCourt.median(),inplace=True)
    data.ShoppingMall.fillna(data.ShoppingMall.median(),inplace=True)
    data.Spa.fillna(data.Spa.median(),inplace=True)
    data.VRDeck.fillna(data.VRDeck.median(),inplace=True)

    # segmentation age

    data['tranche_age'] = pd.cut(x=data['Age'], 
                             bins=[0, 17, 32, 49, 79], 
                             labels=['enfant(<17)', 
                                     'jeune(17-31)', 
                                     'adulte(32-48)', 
                                     'sénior(49-79)'])

    # enrichissement                               
    data["Cabin_deck"] = data.Cabin.str.split("/",expand=True)[0]
    data["Cabin_num"] = data.Cabin.str.split("/",expand=True)[1]
    data["Cabin_side"] = data.Cabin.str.split("/",expand=True)[2]

    data["PassengerId_group"] = data.PassengerId.str.split("_",expand=True)[0]
    data["PassengerId_num"] = data.PassengerId.str.split("_",expand=True)[1]

    nb_pass_cabine = data.groupby(['Cabin_num'])['PassengerId'].count().reset_index().rename(columns={'PassengerId': 'nbpassager_par_cabine'})
    nb_passag_group = data.groupby(['PassengerId_group'])['PassengerId'].count().reset_index().rename(columns={'PassengerId': 'nb_passag_group'})


    data = pd.merge(data, nb_pass_cabine, on=['Cabin_num'],how='left')
    data = pd.merge(data, nb_passag_group, on=['PassengerId_group'],how='left')

    data.nbpassager_par_cabine.fillna(data.nbpassager_par_cabine.median(),inplace=True)
    data.nb_passag_group.fillna(data.nb_passag_group.median(),inplace=True)

    data.set_index("PassengerId", inplace=True)
    
    # dummies variables 
    data.drop(["Name","Cabin","Age",
            "Cabin_num","PassengerId_group"],
            axis=1,
            inplace=True)

    data = pd.get_dummies(data)

    scaler = StandardScaler()
    scaler.fit(data)
    data= pd.DataFrame(scaler.transform(data),columns=data.columns)

    return data





def rgb_to_hex(r, g, b):
    """
        Cette fonction convertie une combinaison RGB en code hexadécimal
        Params:
            r : red, intensité de rouge
            g : green, intensité de vert
            b : blue, intensité de bleu
        returns : une séquence hexadéciamle

        exemple : rgb_to_hex(255, 165, 1)
        résultat : "FFA51"
    """

    return "#0{:X}{:X}{:X}".format(int(r), 
                                int(g), 
                                int(b))


class Mise_enforme:
    """
    La classe regroupe l'ensemble des mise en formes indispensables 
    pour la production d'un document quarto
    """

    # création du constructeur

    def __init__(self) -> None:
        self.lkp_blue = rgb_to_hex(0, 34, 93)
        self.lkp_green = rgb_to_hex(0, 136, 81)
        self.lkp_magenta = rgb_to_hex(148, 0, 113)
        self.lkp_grey = rgb_to_hex(169, 169, 169).replace("0","")
        self.lkp_comp_blue = rgb_to_hex(0, 113, 148)
        self.lkp_light_blue = rgb_to_hex(35, 95, 221)
        self.lkp_light_green = rgb_to_hex(0, 227, 166)

   
