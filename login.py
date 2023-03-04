import mysql.connector
import random
import string
import smtplib
from email.mime.text import MIMEText
import getpass

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='login_system',
            user='root',
            password='1234',
            autocommit=True
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Ongelma MYsql:n kanssa: {e}")
        exit(1)

def generate_verification_code(length):
    kirjaimet_ja_numerot = string.ascii_letters + string.digits
    return ''.join(random.choice(kirjaimet_ja_numerot) for i in range(length))

def send_verification_email(to_email, verification_code):
    lähettäjä = 'jepsteri04@gmail.com'
    password = 'nsbcymivkmlnoalq'

    message = MIMEText(f'Koodisi on: {verification_code}')
    message['Subject'] = 'Kirjautuminen - Varmennekoodi'
    message['From'] = lähettäjä
    message['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(lähettäjä, password)
        server.sendmail(lähettäjä, to_email, message.as_string())

def register():
    email = input("Syötä sähköposti: ")
    salasana = getpass.getpass("Syötä salasana: ")

    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        values = (email,)
        cursor.execute(query, values)
        käyttäjä = cursor.fetchone()
        if käyttäjä is not None:
            print("Error: Email address already registered. Please try again with a different email address.")
            return
        else:
            query = "INSERT INTO users (email, password) VALUES (%s, %s)"
            values = (email, salasana)
            cursor.execute(query, values)
            connection.commit()
            print("Käyttäjä rekisteröidytty!")

            # Send verification email
            verification_code = generate_verification_code(6)
            send_verification_email(email, verification_code)
            print("Koodi lähetetty sähköpostiisi.")
            user_verification_code = input("Syötä koodi: ")
            if user_verification_code == verification_code:
                print("Sähköposti varmennettu onnistuneesti!")
            else:
                print("Koodi on väärä. Yritä uudelleen.")
    except mysql.connector.Error as e:
        print(f"Ongelma rekisteröitymisessä: {e}")
        connection.rollback()
    finally:
        cursor.fetchall() 
        cursor.close()
        connection.close()

def login():
    email = input("Syötä sähköposti: ")
    salasana = getpass.getpass("Syötä salasana: ")

    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        values = (email,)
        cursor.execute(query, values)
        käyttäjä = cursor.fetchone()
        if käyttäjä is not None and salasana == käyttäjä[2]:
            print("Login successful!")
        else:
            print("Väärä sähköposti tai salasana.")
    except mysql.connector.Error as e:
        print(f"Virhe kirjautumisessa: {e}")
    finally:
        cursor.fetchall()  # Fetch any remaining rows
        cursor.close()
        connection.close()

# Main code
while True:
    print("1. Kirjaudu")
    print("2. Rekisteröidy")
    print("3. Poistu")

    valinta = input("Syötä numero: ")

    if valinta == '1':
        login()
    elif valinta == '2':
        register()
    elif valinta == '3':
        break
    else:
        print("Virheellinen valinta. Yritä uudelleen!")