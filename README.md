# Machine Learning Industrialization

## Installation

### Sur Mac/Linux :
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
uv run pytest
```

### Sur Windows:
```bash
scripts\setup.bat
uv run pytest
```

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

Vous avez fait "get_monthly_sales", et vous avez réfléchi à comment refactorer votre code.
**-1 point si non fait après 30 minutes**

**A rendre**: le code, avec un fichier app_csv.py où l'app fonctionne en enregistrant les données sur des CSV et app_sql.py où l'app enregistre sur une base de données sql lite, ainsi que vos fichieres de tests<br/>

Envoyer à foucheta@gmail.com avec l'objet "[ESGI][ML_INDUS]TP1"

