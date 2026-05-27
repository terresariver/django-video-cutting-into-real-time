# Backend d'une application de decoupage videos en videos reels a temps parametrable

A complete video editing pipeline backend built with Django, Celery, and FFmpeg. Upload videos, process them asynchronously, and export in multiple formats.

Un systeme permettant d'effectuer differente modification video construit avec Django, celery et ffmpeg 

# Points cles

- **Point de terminaison Upload** (`/video/upload/`) - Enregistre la video dans la base de donnees et dans un dossier media
- **Point de terminaisin de traitement** (`/video/processing/`) -  Traitements ffmpeg asynchrone avec celery 
- **Point de terminaison d'export** (`/video/export/`) - telecharger les videos traitees au format choisi

# Operations supportees

| Operation | Action | Parametre |
|-----------|--------|------------|
| Decouper | `trim` | `debut`, `fin` (HH:MM:SS) | 
| Redimensionner | `resize` | `longueur`,`largeur` |
| Faire pivoter| `rotate` | `angle`|
| Recadrer| `crop` |  `longueur`,`largeur`,`x`,`y`| 
|generer un thumnail| `thumbnail` | `temps` (HH:MM:SS)|
|ajouter un watermark| `watermark` | `Echelle`,`x`,`y`|

# Formats des exports et qualite

**Formats:** MP4, WebM, AVI, MOV

**Qualite**
- **faible** - 500 kbps (kilo bits par seconde)
- **moyenne** - 1500 kbps 
- **haute** - 3000 kbps 

# Lancement

# 1:Installer les elements necessaires

# FFmpeg
telecharger ffmpeg sur le site officiel ,ajouter aux variables systeme #windows
sudo apt install ffmpeg  # Linux

# Redis
wsl install , redemarrer l'ordinateur, lancer Ubuntu sudo apt  updtate , sudo apt install redis-server #windows
sudo apt install redis-server #linux

# Librairies python
pip install django
pip install djangorestframework
pip install requests
pip install celery redis
pip install celery[redis] django-celery-results


# 2. Demarrer les services
```bash
# Terminal 1(Ubuntu): Lancer redis
sudo service redis-server start

# Terminal 2: Lancer Celery  dans le dossier du projet (prototype)
celery -A prototype worker --pool=solo --loglevel=info

# Terminal 3: Lancer Django dans le dossier du projet (prototype)
python manage.py runserver
```

# 3. Test 
naviguer aux addresses suivantes pour tester :
http://127.0.0.1:8000/prototype/test/process/ #upload et traitement 
http://127.0.0.1:8000/prototype/test/export/ #exportation

# Structure du projet

prototype/
├── api/
│   ├── models.py         # modele video
│   ├── views.py          # Upload, traitement, export
│   ├── tasks.py          # traitement de video en utilisant celery
│   ├── urls.py           
│   ├── serializers.py    # serializers video
│   └── templates/        #front end de test
|       ├── test_export.html    
|       └── test_process.html
├────── services/
|       ├── ffmpeg.py     #fonction ffmpeg
|       └── AI.py
|
├── prototype/
│   ├── settings.py      
│   ├── celery.py         # configuration Celery
│   └── ...
├── media/
│   └── videos/
│       ├── originals/    # videos uploadees
│       ├── traite/       # videos traites
│       └── exports/      # videos telechargees
├── README.md
├── FRONTEND_INTEGRATION.md
├── requirements.txt
└── manage.py





# modele video

class Video(models.Model):
    titre        # titre de la video
    original     #  video original
    traite       #  video traite
    status       # EN ATTENTE, EN COURS DE TRAITEMENT, TERMINE, ECHOUE
    date         # date d'upload



# Reponse http

- **201** - Video uploade avec succes
- **202** - Traitement/export commence
- **400** - Mauvaise requete 
- **404** - Video introuvable
- **500** - erreur serveur 
