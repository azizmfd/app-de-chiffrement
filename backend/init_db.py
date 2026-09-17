import sqlite3

mots = [
    "mot de passe", "email", "iban", "numéro de carte",
    "carte bancaire", "adresse", "login", "confidentiel",
    "secret", "nom complet", "sécurité sociale", "motdepasse", "password", "clé_privée",
    "token", "jeton", "API_key", "access_token", "refresh_token", "identifiant",
    "username", "utilisateur", "user_id", "PIN", "code_PIN", "OTP",
    "mot_de_passe_à_usage_unique", "CVV", "CVV2", "numéro_de_compte", "BIC",
    "SWIFT", "numéro_de_téléphone", "téléphone_portable", "adresse_email",
    "adresse_physique", "adresse_domicile", "code_postal", "ville", "pays",
    "CNSS", "numéro_de_sécurité_sociale", "NSS", "numéro_fiscal", "numéro_de_tva",
    "matricule", "CIN", "numéro_de_cin", "passeport", "numéro_de_passeport",
    "permis_de_conduire", "numéro_permis", "dossier_médical", "diagnostic",
    "ordonnance", "prescription", "antécédents", "allergies", "traitement_en_cours",
    "résultat_de_test", "carte_vitale", "numéro_carte_vitale", "mutuelle",
    "assurance_maladie", "police_d’assurance", "sinistre", "DEA", "empreinte_digitale",
    "empreinte_vocale", "ADN", "données_biométriques", "photo_identité", "signature",
    "email_professionnel", "intranet", "VPN", "adresse_IP", "adresse_MAC",
    "géolocalisation", "coordonnées_GPS", "bookmark", "historique_navigateur",
    "cookies", "session_id", "numéro_de_série", "numéro_de_produit", "secret_key",
    "ssh_key", "certificat_SSL", "passphrase", "phrase_de_passe", "code_d’accès",
    "habilitation", "clearance", "niveau_secret", "top_secret", "privé", "interne",
    "réservé" ,  "nom", "prénom", "date_naissance", "lieu_naissance", "lieu_residence",
    "adresse_IP_privée", "adresse_MAC_appareil", "numéro_téléphone_fixe",
    "téléphone_professionnel", "email_secondaire", "mot_de_passe_wifi",
    "question_secrète", "réponse_secrète", "empreinte_retinale",
    "empreinte_palmaire", "dossier_patient", "antécédent_médical",
    "bilan_sanguin", "groupe_sanguin", "date_consultation",
    "diagnostic_principal", "traitement_prescrit", "allergène", "vaccin",
    "numéro_SSN_USA", "TIN (numéro_identification_fiscal)", "numéro_IMSI",
    "numéro_IMEI", "carte_sim", "code_PUK", "identifiant_APP",
    "cookie_de_session", "jeton_JWT", "empreinte_hash", "clé_HMAC",
    "mot_de_passe_root", "mot_de_passe_admin", "chaîne_connection_DB",
    "URI_API", "secret_OAuth", "certificat_numérique", "empreinte_SSL",
    "protocole_TLS", "journal_connexion", "historique_transactions",
    "relevé_opérations", "code_IBAN_international", "nom_titulaire_compte",
    "numéro_clé_SEPA", "mandat_SEPA"
]

conn = sqlite3.connect("mots_sensibles.db")
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS sensitive_words")
c.execute("CREATE TABLE sensitive_words (id INTEGER PRIMARY KEY, word TEXT UNIQUE)")

for mot in mots:
    try:
        c.execute("INSERT INTO sensitive_words (word) VALUES (?)", (mot.lower(),))
    except sqlite3.IntegrityError:
        pass

conn.commit()
conn.close()
print("✔️ Nouvelle base de mots sensibles créée avec succès.")
