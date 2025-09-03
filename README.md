# Machine Learning Industrialization

## Installation

### Sur Mac/Linux :
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
uv run pytest
```

### Sur Windows:

#### WSL (recommandé) -> Utilisez l'installation Mac/Linux

#### Windows terminal

```bash
scripts\setup.bat
uv run pytest
```

### PyCharm

Si vous avez PyCharm, cliquez droit sur le dossier "src/" -> "Mark directory as" -> "Sources Root"

## TD1: Industrialization de la pipeline data


### Objectifs

Nous allons créer un data pipeline industrialisée. <br/>
Nous travaillons pour un vendeur de légumes, qui récupère les ventes hebdomadaires par une source externe. Nous nous intéressons, pour notre modèle, aux ventes mensuelles.

Nous allons créer une API avec les entry points:
- /post_sales/: reçoit une request POST avec data: une liste de dictionnaire {"year_week": ..., "vegetable": ...., "sales": ....} <br/>
Cette entrée est idempotente. On stockera ces données dans la table bronze
- /get_raw_sales/: renvoie les données brutes que nous avons reçues
- /get_monthly_sales/: renvoie les données cleanées (nom du légume standardisé. Cet entry point a l'option "remove_outliers". Si "remove_outliers=False", entraîne le modèle sur toutes les données. Si "remove_outliers=True", entraîne sur le modèle sur les données safe, qui n'ont pas été tagguées comme "unsafe" par nos algorithmes d'outlier detection.

### Point de départ

Je fournis le code app.py, une app Flask basique avec les entry points /post_sales/, /get_weekly_sales/. <br/>
Pour l'instant, /get_weekly_sales/ retourne une réponse fixe. <br/>
C'est pour tester que l'API est en place.<br/>
Vous modifierez le code pour qu'il fonctionne vraiment.

Je fournis aussi le code example_client.py, qui va ping post_sales/.

Enfin, je fournis [un CSV sur ce lien](https://drive.google.com/file/d/1WJPZQEijYsfTga6il8Ls3pgjdsGhCrq0/view?usp=sharing) avec des ventes weekly de 2020 à 2023. Les noms des légumes peuvent être en anglais, français ou espagnol. Il peut y avoir une faute d'orthographe. Dans la base cleaned, ils doivent être en anglais, sans faute d'orthographe.

### Etapes 

1. Créer le code pour "get_raw_sales" qui retourne les données ingérées. Validez le code avec le test d'intégration ```uv run pytest```

2. Modifier le "test_post_sales" pour qu'il teste l'idempotence. <br/>
i.e. Vous envoyez 2 fois la même données, et il ne la compte pas en double.

3. Rendez post_sales idempotent

4. Créer un test "get_monthly_sales", ressemblant à ceci
```python
def test_get_monthly_sales():
    # We send weekly sales
    client.post("post_sales", json=[
        {year_week: 202001, vegetable: tomato, sales: 100},
        {year_week: 202002, vegetable: tomato, sales: 100},
        {year_week: 202006, vegetable: tomato, sales: 100},
        {year_week: 202010, vegetable: carrot, sales: 50},
    ])

    response = client.get("get_monthly_sales")
    # We recovered right monthly data
    assert response.json == [
      {year_month: 202001, vegetable: tomato, sales: 200},
      {year_month: 202002, vegetable: tomato, sales: 100},
      {year_month: 202003, vegetable: carrot, sales: 50},
    ]
```

4. Gérer les edge-cases des monthly sales. <br/>
Pour une semaine avec n jours sur un mois et 7-n jours sur le mois suivant, on considère que (n / 7)% des ventes étaient sur le mois précédent et ((7 - n) / 7)% sont sur le mois suivant.<br/>
Il est **fortement** suggéré de créer le test unitaire avec les cas problématiques (donnée en entrée, ce qu'on attend en sortie). <br/>
Ce test a plus sa place dans tests/unit/... que dans tests/test_integration.py<br/>
Dans les tests d'intégration, on vérifie que les composants se parlent bien entre eux. Ce sont des tests haut niveau<br/>
Dans les tests unitaires, on s'assure du bon fonctionnement d'une brique. C'est là où on rentre dans le détail du fonctionnement, des edge-cases.

5. Il est temps de réfléchir à la maintenabilité du code<br/>
app.py doit juste déclarer les entry points, et appeler les bons "services" (où on mettra la logique). <br/>
Vous pouvez déclarer un service "data" (services/data.py), qui enregistre la donnée, retourne les ventes weekly et les ventes monthly. <br/>
**Utilisez le fait que le code soit testé pour refactorer !**:
- Commitez le code qui marche
- Refactorez comme il vous semble bon
- Runnez les tests pour vérifier que ça marche
- Commitez

**Attention:** Ne perdez pas 30 minutes à refactorer. "Premature optimisation is the root of all evil".<br/>
Regardez votre code, et faites le refactoring qui vous semble adapter maintenant, sans faire de plan sur la comète.

6. Vous allez créer le code "tag_outlier" qui ajoute is_outlier=True si la vente est supérieure à la moyenne plus 5 fois l'écart-type. <br/>
Commencer par créer le test.<br/>
Faites le code.<br/>
Faut-il prendre moyenne globale ou légume par légume ? Pourquoi ?

7. Changer le modèle pour ne plus écrire dans un CSV, mais dans une table SQL Lite.<br/>
Si vous avez bien travaillé, le changement isolé et n'impacte pas les entry points ni la pipeline.<br/>
Si le changement semble compliqué:
- Réfléchissez à ce que vous pouvez refactorer
- Pensez au modèle MVC (Model, View, Controller).
  - View est app.py, les entry points de l'utilisateur
  - Model est là où sont stockées les données. Idéalement, c'est seulement ce bout qui change, pour passer de "stocker dans CSV" à "stocker dans SQL"
  - Controller est les services, ceux qui vont prendre "arguments de l'utilisateur" -> "exercer l'action" (que ce soit écrire des données ou retourner des données)

8. Ajouter un entry point "/init_database" pour créer la database ou la vider. <br/>

9. Utiliser le package "locust" pour faire un test de charge sur votre API.

Je testerai votre code en le faisant tourner dans un container, en appelant post_sales et les différents get_sales sur mes données. <br/>
Si vous êtes allés jusqu'au tables SQL, j'utiliserai "/init_database" pour ré-initialiser la base quand j'en aurais besoin.

Je testerai votre pipeline en la faisant tourner dans un Docker. Votre pipeline doit supporter:
- Ne pas inscrire des données où des champs sont faux (pas de vegetable)
- post_sales est bien idempotent pour une (year_month,vegetable)
- Inscrire toutes les données valables d'une liste. Si la liste contient des données "A: valide", "B: valide", "C: non valide", "D: valide", je dois retrouver dans la base les données A, B, et D.
- Tagger comme "outlier" les ventes à 5 écart-types de leur référence.
- Votre API doit supporter 1000 requêtes par seconde (500 post, 250 get_raw_data, 250 get_monthly_data).
- Vos tests d'intégration doivent couvrir les cas mentionnés ici.

## !! Timeline !! (**Points en moins si non respectée**)

### Après 30 minutes

La commande "uv run pytest" tourne sur votre machine. <br/>
L'entry point "post_sales" écrit vraiment les données. <br/>
L'entry point "get_weekly_sales" lit vraiment les données.<br/>
**-1 point si non fait après 30 minutes**<br/>
**0 au TD si non fait après 1 heure**

### Après 1 heure

Vous avez fait "get_monthly_sales", et vous avez réfléchi à comment refactorer votre code. <br/>
**-1 point si non fait après 1 heure**

## Mon evaluation

Dans tests/test_td1_prof.py, vous avez un exemple des tests que je ferai pour évaluer votre code.
Je ferai un
```bash
python src/app.py
```
Pour lancer votre application, et
```bash
pytest tests/test_td1_prof.py
```
Pour faire des requêtes sur votre API et vérifier qu'elle fonctionne bien comme attendu. <br/>
Assurez-vous que votre application marche bien avec mon fichier de test.

## A rendre

Le code, avec un fichier app_csv.py où l'app fonctionne en enregistrant les données sur des CSV et app_sql.py où l'app enregistre sur une base de données sql lite, ainsi que vos fichieres de tests<br/>

Envoyer à foucheta@gmail.com avec l'objet "[ESGI][ML_INDUS]TP1"


## TD2: Iteration sur un modèle

Dans ce TD, nous allons voir un problème d'apprentissage supervisé, sur lequel on va rajouter des sources de données et des features au fur et à mesure. <br/>
Nous voulons faire du code industrialisé, où nous pouvons itérer rapidement. <br/>
Il est fortement conseillé:
- De faire les étapes une par une, de "jouer le jeu" d'un projet qui évolue au cour du temps
- Pour chaque étape, de coder une solution, puis voir les refactos intéressantes. Attention: une erreur serait de se perdre en cherchant la perfection. 
- De faire du code modulaire, avec:
  - Un module téléchargeant les données (un data catalogue)
  - Un module construisant les features. Chaque "feature" a son module
  - Un module générant le model. Tous les modèles ont les méthodes ".fit(X, y)", ".predict"

Vous avez le fichier de test tests/test_model.py avec les tests que je ferai. <br/>
Les tests appellent, dans main.py, la fonction "make_predictions(config: dict) -> df_pred: pd.Dataframe"


Télécharger [le dataset](https://drive.google.com/file/d/1OFDGVqlmx-5-hE3Bnn-996LGpumScwOV/view?usp=sharing). <br/>
Il s'agît de ventes mensuelles d'une industrie fictive.

1) Coder un modèle "SameMonthLastYearSales", predisant, pour les ventes de item N pour un mois, les mêmes ventes qu'il a faites l'année dernière au même mois (pour août 2024 les mêmes ventes que l'item N a eu en août 2023)

2) Coder un modèle auto-regressif.
Les données ont été générées comme une combinaison des ventes le même mois l'année dernière, des ventes moyennes sur l'année dernière, et des ventes du même mois l'année dernière fois la croissance du quarter Q-5 au quarter Q-1

$$sales(M) = a * sales(M-12) + b * sales(M-1:M-12) / 12 + c * sales(M-12) \frac{sales(M-1:M-3)}{sales(M-13:M-15)}$$

Coder le "build_feature" qui va générer ces différentes features autoregressive. <br/>
Utiliser le modèle sklearn Ridge()

3) Ajouter les données marketing.

Les mois où il y a eu des dépenses marketing, cela a impacté les ventes.

Les données ont été générées ainsi

$$ sales(M) = ...past\, model... * (1 + marketing\_spend * d) $$

4) Ajouter les données de prix

Les clients, des grossistes, sont prévenus en avance d'un changement de prix. <br/>
Si le prix va augmenter le mois suivant M+1, ils commandent plus que d'habitude au mois M, et moins au mois M+1. <br/<
A l'inverse, si le prix va baisser, ils commandent moins au mois M et plus à M+1.

5) Ajouter les données de stock

Certains mois, l'industriel a eu des ruptures de stocks et donc a vendu moins que ce qu'il aurait pu. Le mois suivant, il a plus vendu car les clients ont racheté ce qu'ils devaient pour leur consommation. <br/>

stock.csv contient les "refill" de stock quotidien. On suppose que le stock initial était 0. <br/>
Il y a rupture de stock si le stock est 0 à la fin du mois. <br/>
En ayant identifié les ruptures de stock, vous pouvez décider de ne pas entraîner sur les mois où les ruptures de stocks ont eu un effet (le mois de la rupture et le mois suivant). <br/>

On sait en avance les refill de stocks qu'on aura. <br/>
Donc, on peut améliorer nos prédictions de cette façon:

$$ pred\_processed(item_i, month_M) = \min(stock(item_i, month_M), pred(item_i, month_M)) $$

6) Ajouter les objectifs des commerciaux.

Les commerciaux ont des objectifs de vente à l'année. L'année fiscal se terminant en juin, c'est ce mois, et le mois suivant, qui sont impactés. <br/>
Si l'item a déjà fait son objectif, où est loin de le faire (resterait 20% des ventes à faire), il n'y a pas d'impact. <br/>
Sinon, l'équipe commercial va faire tout son possible pour arriver à l'objectif, demandant à leurs clients de sur-acheter en juin. Du coup, il y a un sous-achat en juillet compensant la sur-vente de juin.

Intégrer les données des objectifs à votre pipeline de prédiction.

7) Faire un modèle custom

La génération des données a été faite ainsi. J'ai généré des données autoregressées ainsi:

$$sales\_v1(M) = a * sales(M-12) + b * sales(M-1:M-12) / 12 + c * sales(M-12) \frac{sales(M-1:M-3)}{sales(M-13:M-15)}$$

Ca fait, j'ai rajouté les effets:

$$ sales\_v2(M)  = sales\_v1(M) * (1 + d * marketing ) * (1 + e * price\_change) $$

J'ai ensuite ajouté, au hasard sur certains mois, des contraintes "objectifs commerciaux", puis des contraintes de stock.

Vous pouvez faire votre propre modèle qui reprend ces équations, avec les paramètres a, b, c....,e, et utilser scipy.optimize pour trouver les paramètres idéaux.

### Après 30 minutes

Les tests "test_model_prev_month" & "test_model_same_month_last_year"
**-1 point si non fait après 30 minutes**<br/>
**0 au TD si non fait après 1 heure**

### Après 1 heure

Vous avez fait l'auto-regressive model.<br/>
Le test "test_autoregressive_model" passe. <br/>
**-1 point si non fait après 1 heure**

## A rendre

Votre code src/. 
