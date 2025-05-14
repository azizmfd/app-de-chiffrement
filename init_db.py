import sqlite3

mots = [
    "mot de passe", "email", "iban", "numéro de carte",
    "carte bancaire", "adresse", "login", "confidentiel",
    "secret", "nom complet", "sécurité sociale", "mdp"
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
