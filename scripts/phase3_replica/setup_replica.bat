@echo off
TITLE Pipeline Complet CineExplorer - Replica Set + Migration

:: --- 0. POSITIONNEMENT DANS LE DOSSIER PROJET ---
echo [0/5] Deplacement vers le dossier du projet...
cd /d "C:\Users\adamf\Documents\cineexplorer\cineexplorer"

:: --- 1. PREPARATION DES DOSSIERS ---
echo [1/5] Nettoyage et creation des repertoires...
if not exist "data\mongo\db-1" mkdir "data\mongo\db-1"
if not exist "data\mongo\db-2" mkdir "data\mongo\db-2"
if not exist "data\mongo\db-3" mkdir "data\mongo\db-3"

:: --- 2. LANCEMENT MONGODB ---
echo [2/5] Lancement des instances MongoDB...
:: On utilise des chemins relatifs car on a fait le 'cd' au début
start "Mongo_27017" mongod --replSet rs0 --port 27017 --dbpath ./data/mongo/db-1 --bind_ip localhost
start "Mongo_27018" mongod --replSet rs0 --port 27018 --dbpath ./data/mongo/db-2 --bind_ip localhost
start "Mongo_27019" mongod --replSet rs0 --port 27019 --dbpath ./data/mongo/db-3 --bind_ip localhost

echo Attente de 10 secondes pour l'initialisation des serveurs...
timeout /t 10 /nobreak > nul

:: --- 3. INITIALISATION REPLICA SET ---
echo [3/5] Configuration du Replica Set rs0...
mongosh --port 27017 --eval "rs.initiate({_id:'rs0',members:[{_id:0,host:'localhost:27017'},{_id:1,host:'localhost:27018'},{_id:2,host:'localhost:27019'}]})"

echo Attente de 5 secondes pour l'election du Primary...
timeout /t 5 /nobreak > nul

:: --- 4. EXECUTION SCRIPTS SQLITE (PHASE 1) ---
echo [4/5] Preparation de SQLite...
"C:\Users\adamf\AppData\Local\Microsoft\WindowsApps\python3.11.exe" "scripts\phase1_sqlite\create_schema.py"
"C:\Users\adamf\AppData\Local\Microsoft\WindowsApps\python3.11.exe" "scripts\phase1_sqlite\import_data.py"

:: --- 5. EXECUTION MIGRATIONS MONGODB (PHASE 2) ---
echo [5/5] Migration vers le Replica Set MongoDB...
"C:\Users\adamf\AppData\Local\Microsoft\WindowsApps\python3.11.exe" "scripts\phase2_mongodb\migrate_flat.py"
"C:\Users\adamf\AppData\Local\Microsoft\WindowsApps\python3.11.exe" "scripts\phase2_mongodb\migrate_structured.py"

echo.
echo ======================================================
echo   PIPELINE TERMINE AVEC SUCCES !
echo ======================================================
pause