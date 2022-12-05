# A number of helper functions for scraping utility website's outages.

import sqlite3, smtplib, ssl
from deep_translator import GoogleTranslator
from fuzzysearch import find_near_matches
from email.message import EmailMessage
from decouple import config


# TODO: change server to postgresql


# Checks if url is in db
def disruption_saved(url: str):
    """Returns True if disruption's URL found in db"""
    # connect to the db
    con = sqlite3.connect("utility_scraper.db")

    # establish cursor
    c = con.cursor()

    # get all disruptions with matching url
    matches = c.execute("SELECT * FROM disruptions WHERE url = ?", [url])

    # if no matches found, return False and closes the db
    if matches.fetchone() is None:
        con.close()
        return False

    # else returns True and closes db
    con.close()
    return True



def save_to_db(url: str, disruption_text: str):
    """Saves a disruption to the database"""
    con = sqlite3.connect("utility_scraper.db")
    c = con.cursor()    

    # enter into db
    c.execute("INSERT INTO disruptions VALUES (?, ?)", (url, disruption_text))

    # commit to db
    con.commit()

    # close the db
    con.close()



def translate_disruption(disruption_text):
    """Translates text piecemeal if over character limit, otherwise just translates"""
    translator = GoogleTranslator(source='auto', target='english')
    try:
        if len(disruption_text) > 2000:

            # Translation setup for Telasi
            if "ელ.მომარაგების" in disruption_text or "ელექტრო" in disruption_text:
                # Split disruption_text into paragraphs
                paragraphs = disruption_text.split("\n")
                # Create list to store translated paragraphs
                translated_paragraphs = []
                # Iterate over paragraphs
                for p in paragraphs:
                    # Split paragraphs into sentences
                    sentences = p.split(". ")
                    # Translated sentences
                    translated_sentences = translator.translate_batch(sentences)
                    # Join translated sentences together to form translated paragraph
                    translated_p = "".join(translated_sentences)
                    # Add translated paragraph to list
                    translated_paragraphs.append(translated_p)
                # Join translated paragraphs together to form translated disruption_text
                translated_disruption_text = "\n\n".join(translated_paragraphs)

            else:
                # Translation setup for GWP
                text = disruption_text.split(", ")
                chunks = [text[x:x+60] for x in range(0, len(text), 60)] # split list into sublists of 250 words each
                translated_disruption_text = ""
                for chunk in chunks:
                    joined = ", ".join(chunk)
                    
                    translated_disruption_text += (translator.translate(joined))

        else: 
            translated_disruption_text = translator.translate(disruption_text)

        return translated_disruption_text    
    except:
        print(disruption_text)

            

def scrape_and_save(disruption_urls: list, disruption_func ):
    """Scrapes disruption urls, translates them, and saves new disruptions to DB"""
    # Iterate over planned urls 
    for url in disruption_urls:
        # If URL is not found in db, scrape URL
        if not disruption_saved(url):
            print(url)
            # Iterate over all disruptions found at target URL
            for origin_text in disruption_func(url):
                
                # Translate text to English
                translated_text = translate_disruption(origin_text)

                # Find users affected by disruption
                affected_users = find_affected_users(translated_text)

                # Email affected users
                for user in affected_users:
                    email_affected_user(user)

                # Save translated disruption text to database
                save_to_db(url, translated_text)



class User:
    """A class to contain information """
    def __init__(self, name, email, street):
        self.name = name
        self.email = email
        # The full street name, e.g. Smith St.
        self.street = street
        # Just the name of the street itself, e.g. Smith
        self.streetname = " ".join(street.split(" ")[:-1])

        # To be assigned to user if disruption found
        self.disruption_text = ""

        # A template for generating email text
        self.email_text = "Hi {name},\n\nYour street has been included in a list of streets affected by a utility disruption in Tbilisi.\nPlease see the following announcement for more details:\n\n{disruption_text}"

    def generate_email_text(self):
        return self.email_text.format(name=self.name, disruption_text=self.disruption_text)



# Iterates over users in DB and emails them if the disruption affects them
def find_affected_users(disruption_text: str):
    """Iterates over users in DB, returns User objects of affected users."""
    # Connect to the user DB
    con = sqlite3.connect("utility_scraper.db")
    c = con.cursor()

    # Create User objects from users in DB
    affected_users = []
    for u in c.execute("SELECT * FROM users"):
        # Users are stored in db as (name, email, street, suburb)
        user = User(u[0], u[1], u[2])
        # Use fuzzysearch to find matches to streetname in disruption
        disruption_streets = disruption_text.split(": ")[-1]

        if find_near_matches(user.streetname, disruption_text, max_l_dist=2):
            # Add disruption text to User object
            user.disruption_text = disruption_text
            # Add User to affected user list
            affected_users.append(user)

    # Disconnect from the database
    con.close()
    
    # Return a list of affected users
    return affected_users



def email_affected_user(affected_user: User):
    # define settings
    port = 465
    email_sender = config('EMAIL_USER', default='')
    email_password = config('EMAIL_PW', default='')

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        # Login to the server
        server.login(email_sender, email_password)

        # Generate email message
        message = EmailMessage()
        message.set_content(affected_user.generate_email_text())
        message["subject"] = "Your street has a utility disruption!"
        message["from"] = email_sender
        message["to"] = affected_user.email

        # Send email
        server.send_message(message)
        # Cut server connection
        server.close()
    

if __name__ == "__main__":
    for user in find_affected_users("saburtalo ikaltos kucha"):
        print(user.email)
        email_affected_user(user)
