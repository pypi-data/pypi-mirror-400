# Importer les modules

from datetime import datetime
import pandas as pd
from dateutil import relativedelta
from cnaclib.tools import SNMG

##########################################################################################################################################
#                                                       REGIME ASSURANCE CHOMAGE : SIMULATEUR
##########################################################################################################################################


class RACINDEMNITE:
    '''
    REGIME ASSURANCE CHOMAGE : SIMULATEUR

    Cette Classe en 'python' permet de réaliser des simulations pour le calculs des différents éléments liés au régime d'assurance chômage.
    Elle permet de :
    - Vérifier la condition d'admission relative à l'experience professionnelle;
    - Calculer la durée de prise en charge (DPC);
    - Calculer le montant de la Contribution d'Ouverture de Droits;
    - Récupérer le montant du SNMG en fonction de la date;
    - Calculer les montants d'indemnités en fonction des 04 périodes;
    - Calculer les montants de cotisations de sécurité sociale (part patronale & part salariale );

    Parameters
    ----------

    DateRecrutement : date, 
        C'est de la date de recrutement du salarié chez le dernier employeur.
        Elle doit être exprimé selon le format : dd/mm/yyyy.


    DateCompression : date,
        C'est la de compression du salarié chez le dernier employeur.
        Elle doit être exprimé selon le format : dd/mm/yyyy.

    
    SMM : float,
        C'est le Salaire Mensuel Moyen des 12 derniers mois.
        Il doit être exprimé en DA et concerne la moyenne des salaires soumis à cotisation de sécurité sociale des 12 derniers mois.

    
    Attributes
    ----------

    annee : int,
        C'est la durée d'experience en année;

    mois : int,
        C'est la durée d'experience en mois lorsque la période est inferieure à une année;
    
    jours : int,
        C'est la durée d'experience en jours lorsque la période est inferieure à un mois;

    '''

    def __init__(self, nb_contrats, smm):
        self.nb_contrats = nb_contrats
        self.smm = smm

        self.annee = 0
        self.mois = 0
        self.jours = 0

    def calculer_duree(self, contrats):
        """
        contrats : liste de tuples
        [(DateRecrutement, DateCompression), ...]
        """

        if len(contrats) != self.nb_contrats:
            raise ValueError("Le nombre de contrats ne correspond pas")

        total_annees = 0
        total_mois = 0
        total_jours = 0

        for date_debut, date_fin in contrats:
            d1 = datetime.strptime(date_fin, "%d/%m/%Y")
            d2 = datetime.strptime(date_debut, "%d/%m/%Y")

            delta = relativedelta.relativedelta(d1, d2)

            total_annees += delta.years
            total_mois += delta.months
            total_jours += delta.days

        # 🔄 Normalisation
        total_mois += total_jours // 30
        total_jours = total_jours % 30

        total_annees += total_mois // 12
        total_mois = total_mois % 12

        self.annee = total_annees
        self.mois = total_mois
        self.jours = total_jours
contrats = [
    ("01/01/2015", "31/12/2017"),
    ("01/02/2018", "31/01/2020"),
    ("15/03/2020", "05/04/2023")
]

duree = RACINDEMNITE(nb_contrats=3, smm=45000)
duree.calculer_duree(contrats)

print(duree.annee, duree.mois, duree.jours)
