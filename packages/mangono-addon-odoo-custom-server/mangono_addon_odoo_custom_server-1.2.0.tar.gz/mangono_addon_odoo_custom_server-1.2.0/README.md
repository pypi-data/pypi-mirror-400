
# Server Command

Ce dépôt est séparé en 2 parties, à savoir une libraire et un module Odoo.

## Librairie : Lib Odoo cli

Permet d'ajouter des commandes au serveur afin d'adapter Odoo pour des démarrages particulier selon un contexte.

_Installation :_

Il faut se trouver dans le répertoire et faire `pip install .`

## Module : ndpserver

Ce module permet d'installer les nouvelles façons de démarrer Odoo. C'est un Module Odoo qui doit être présent dans le addons-path.

Automatiquement rajouté par notre image docker de Odoo (Dans les versions les plus récentes).

*Installation :*

Ne peut pas être installé, mais doit être présent dans les server wide modules pour utilisation.

*Test en local avec odoo V12*
 uv venv --python 3.8.19 --seed
uv pip install setuptools==58.0.1  # nécessaire pour pouvoir installer suds-jurko
uv pip install suds-jurko==0.6 --no-build-isolation
uv pip install lxml==5.1.0  # forcer le problème de lxml_clean
uv pip install ../../python/odoo/v12/odoo  # adapter le chemin vers odoo
uv pip install -r requirements.txt
uv pip install mangono-odoo-s3-filestore
python -m unittest discover

*test fonctionnel de lancement de odoo*
variables d'environnement déclarées en fichier .ENV, venv de ce projet avec `uv pip install .`, chemin de odoo-bin à
utiliser, paramètre=generic_server
