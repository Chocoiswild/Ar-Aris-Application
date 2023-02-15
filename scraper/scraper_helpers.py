# Helper functions for the Ar Aris scraper.

import  smtplib, ssl, psycopg2
from deep_translator import GoogleTranslator
from fuzzysearch import find_near_matches
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from magtifun_oop import MagtiFun
import hashlib
import re
from itsdangerous.url_safe import URLSafeSerializer


class Disruption:
    """ A class for containing all information relating to a disruption"""
    def __init__(self, text_ge, announcement_ge, utility, url):
        self.text_ge = text_ge
        self.announcement_ge = announcement_ge
        self.url = url
        self.utility = utility

        self.hash = ""
        self.text_en = ""
        self.announcement_en = ""
        self.time = ""

    def process(self):
        """Translates disruption, announcement, and extracts times"""
        translate_disruption(self)
        self.time = extract_times(self.text_en)


class User:
    """A class for creating User objects"""
    def __init__(self, id, name, email, street, district, phone=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        # The full street name, e.g. Smith St.
        self.street = street
        self.district = district
        # Just the name of the street itself, e.g. Smith, not Smith st.
        self.streetname = " ".join(street.split(" ")[:-1])

        # Templates for generating email and text message content
        self.email_subject = "{utility} outage {disruption_time}: {announcement}"
        self.email_text_html = """
<html>
    <body>
        <p>Hi {name},<br><br>
           <b>{street}</b> has been included in a list of streets affected by a utility disruption in Tbilisi.
           Please see the following announcement for more details:<br><br>
           {disruption_text}<br><br>
           If you believe you have recieved this email in error, or your street is not included in this disruption, please reply to this email.<br><br>
           <a href="{unsubscribe_link}">Unsubscribe</a> if you no longer wish to recieve disruption notifications.        
        </p>
    </body>
</html>
"""
        self.email_text_plaintext = """
Hi {name},

{street} has been included in a list of streets affected by a utility disruption in Tbilisi.
Please see the following announcement for more details:

{disruption_text}

If you believe you have recieved this email in error, or your street is not included in this disruption, please reply to this email.

Head on over to the following link if you no longer wish to recieve disruption notifications:
{unsubscribe_link}
"""
        self.text_message = "{utility} outage on {street} {disruption_time}:\n{announcement}\nMore info: {url}"


    def generate_confirmation_token(self):
        s = URLSafeSerializer(config('ITSDANGEROUS', default=""), salt='unsubscribe')

        return str(s.dumps(self.id))
    
    def generate_email_text(self, disruption: Disruption):
        unsubscribe_link = 'https://www.araris.ge/unsubscribe/{token}'                                            
        self.unsubscribe_url = unsubscribe_link.format(token=self.generate_confirmation_token())

        # Adjust disruption text for html
        disruption_text_html = d.text_en.replace("\n", "<br>")
        self.email_subject = self.email_subject.format(
                                    utility=disruption.utility,
                                    announcement=disruption.announcement_en,
                                    disruption_time=disruption.time
                                    )
        self.email_text_html = self.email_text_html.format(
                                    name=self.name, 
                                    street=self.street,
                                    disruption_text=disruption_text_html,
                                    unsubscribe_link=self.unsubscribe_url
                                    )
        self.email_text_plaintext = self.email_text_plaintext.format(
                                    name=self.name, 
                                    street=self.street,
                                    disruption_text=disruption.text_en,
                                    unsubscribe_link=self.unsubscribe_url
                                    )

    def generate_text_message(self, disruption: Disruption):
        self.text_message = self.text_message.format(
                                                    utility=disruption.utility, 
                                                    street=self.street, 
                                                    disruption_time=disruption.time, 
                                                    announcement=disruption.announcement_en, 
                                                    url=disruption.url
                                                  )

    def generate_communications(self, disruption: Disruption):
        """Populates email and text message content"""

        self.generate_email_text(disruption)
        self.generate_text_message(disruption)
        


class Database():
    """Connects and handles the various SQL queries"""
    def __init__(self):
        # connect to DB
        try:
            self.con = psycopg2.connect(
                host=config('PGHOST', default=''),
                database=config('PGDATABASE', default=''),
                user=config('PGUSER', default=''),
                password=config('PGPASSWORD', default=''),
                port=config('PGPORT', default=''),
                )
        except(Exception, psycopg2.DatabaseError) as error:
            print('failed to connect to database')
            print(error)

    def fetch(self, query, parameters):
        """Returns the results of a database query"""
        with self.con.cursor() as c:
            c.execute(query, (parameters))
            return c.fetchall()

    def save(self, query, parameters):
        """ Saves information to a database """
        with self.con.cursor() as c:
            c.execute(query, (parameters))
        self.con.commit()
    
    def close_connection(self):
        """Kills the connection to the database,
        use when Database object no longer needed"""
        self.con.close()



def text_user(user: User):
    """Texts a disruption notification to a user"""
    m = MagtiFun(username=config('M_USER', default=''),
                              password=config('M_PW', default=''))
    print(f"texting {user.name}")
    if m.login():
        print("Authentication successful")

        m.get_balance()
        print("balance:", m.balance)

        if m.send_messages(user.phone, user.text_message):
            print("All messages sent successfully")
        else:
            print("Some messages could not be sent. Check the log for more details")
            print(m.log_file)

    else:
        print("Authentication unsuccessful")



def extract_times(disruption_text: str):
    """Extracts and returns the disruption's times, if possible. 
        Otherwise, returns NULL"""
    # Bar a few rare outliers, all dates and times in disruption texts
    # can be found with the following patterns
    p1 = "from\s(?P<time_from>\d{1,2}:\d{2}\s(a|p)\.m\.)\sto\s(?P<time_to>\d{1,2}:\d{2}\s(a|p)\.m\.)"
    p2 = "from\s\d{2}\/\d{2}\s(?P<time_from>\d{2}:\d{2})\sto\s\d{2}\/\d{2}\s(?P<time_to>\d{2}:\d{2})"
    p3 = "from\s(?P<time_from>\d{2}:\d{2})\sto\s(?P<time_to>\d{2}:\d{2})"
    p4 = "\d{2}\.\d{2}\.\d{4}\.?\s(?P<time_to>\d{1,2}:\d{2}\s(a|p)\.m\.)"
    p5 = "from\s(?P<time_from>\d{2}:\d{2})\son\s[A-Z][a-z]{3,8}\s\d{1,2}\sto\s(?P<time_to>\d{2}:\d{2})\son\s[A-Z][a-z]{3,8}\s\d{1,2}"

    # Patterns cannot be joined and searched all at once, 
    # due to the usage of named groups e.g. (?P<time_to>) in each pattern
    # If workaround is found, use below:
        # search_patterns = '(' + ')|('.join([p1, p2, p3, p4, p5]) + ')'

    # Check all patterns for matches within text
    for p in [p1, p2, p3, p4, p5]:
        matched = False
        match =  re.search(p, disruption_text)
        if match:
            matched = True
            if "time_from" not in p:
                times = f"until {match.group('time_to')}"
            else:
                times = f"from {match.group('time_from')} to {match.group('time_to')}"

            return times
        # If there are no matches found, it's an outlier
    if not matched:
        times = ""
    return times



def get_users(database: Database):
    """Retrieves a list of all users from the DB"""
    sql = "SELECT * FROM users"
    db_users = database.fetch(sql, ())
    return [User(u[0], u[1], u[2], u[3], u[4], u[5]) for u in db_users]



def get_urls(database: Database):
    """Retrieves and returns a list of dictionaries of URLS 
        and the hashes of the disruptions found at each URL """
    sql = "SELECT url, hash FROM urls"
    urls = []
    results = database.fetch(sql, ())
    # Create dict objects, add them to list
    for u in results:
        url = u[0]
        hash = u[1]
        urls.append({'url': url, 'hash': hash})
    return urls



def get_disruption_hashes(database: Database, url: str):
    """Gets all disruption hashes from the database's disruptions table
        which match the given url"""
    hashes = []
    sql = "SELECT hash FROM disruptions WHERE url LIKE (%s)"
    hash_tuples = database.fetch(sql, (url,))
    # hashes tuples are returned as (hash,)
    for h in hash_tuples:
        hashes.append(h[0])
    return hashes        



def save_disruption(database: Database, disruption: Disruption):
    """Saves a disruption to the POSTGRESQL database"""
    print("saving new disruption to db")
    sql = "INSERT INTO disruptions (url, text, hash) VALUES (%s, %s, %s)"
    database.save(sql, (disruption.url, disruption.text_en, disruption.hash))



def save_url(database: Database, url: str, hash: str, url_exists: bool):
    """Saves a url and the hash of its disruptions to the database"""
    # if the url exists, replace the hash with the new one.
    if url_exists:
        print("updating hash")
        sql = "UPDATE urls SET hash=(%s) WHERE url like (%s)"
    # Otherwise create a new DB entry
    else:
        print("saving url to db")
        sql = "INSERT INTO urls (hash, url) VALUES (%s, %s)"
    database.save(sql, (hash, url))



def translate_disruption(disruption: Disruption):
    """Translates given disruption's annoucement and text to English"""
    print("translating disruption")
    # Initiate the translator object here so it's done just once
    translator = GoogleTranslator(source='auto', target='english')
    # Translator can only handle so many characters at once. 
    if len(disruption.text_ge) > 2000:
        # Telasi and GWP's texts are formatted differently, 
        # so they need to be broken up in different ways for translation.
        # For Telasi
        if "ელ.მომარაგების" in disruption.text_ge or "ელექტრო" in disruption.text_ge:
            # Telasi texts are often long, so break into paragraphs
            # and then translate sentences within paragraphs.
            paragraphs = disruption.text_ge.split("\n")
            translated_paragraphs = []
            for p in paragraphs:
                # Then into sentences, then translate
                sentences = p.split(". ")
                translated_sentences = translator.translate_batch(sentences)
                translated_p = "".join(translated_sentences)
                translated_paragraphs.append(translated_p)
            # Text is joined together at end
            translated_disruption_text = "\n\n".join(translated_paragraphs)

        else:
            # For GWP
            text = disruption.text_ge.split(", ")
            # GWP texts are not as long, and their formatting allows a text to
            # be split into groups of 60 words which are translated.
            chunks = [text[x:x+60] for x in range(0, len(text), 60)] 
            translated_disruption_text = ""
            for chunk in chunks:
                joined = ", ".join(chunk)
                translated_disruption_text += (translator.translate(joined))
    # If the text is short enough it's translated in one go.
    else: 
        translated_disruption_text = translator.translate(disruption.text_ge)

    disruption.text_en  = translated_disruption_text
    disruption.announcement_en = translator.translate(disruption.announcement_ge)



def generate_hash(string: str):
    """A simple function to generate and return hashes from strings"""
    bytestring = bytes(string, 'utf-8')
    m = hashlib.sha256()
    m.update(bytestring)
    
    return m.hexdigest()



def find_affected_users(disruption: Disruption, users: list):
    """Iterates over users in DB, returns User objects of affected users."""
    print('finding affected users')
    affected_users = []
    for u in users:
        user_affected = False
        # Users are stored in db as (name, email, street, district, phone)
        # user = User(u[1], u[2], u[3], u[4], u[5])
        # Use fuzzysearch to find matches to district 
        # and streetname in disruption
        # Filter by district due to duplicate street names
        if find_near_matches(u.district, disruption.text_en, max_l_dist=1):
            # Tbilisi streetnames are a mess, and they're not 
            # always written in full in disruptions
            street_parts = u.streetname.split(" ")
            # If the street has two names (e.g. Ivane Machabeli), 
            # it is known by second name.
            # Filtering by district should avoid any complications 
            # filtering like this may turn up
            if len(street_parts) == 2:
                if find_near_matches(street_parts[1], disruption.text_en, 
                                     max_l_dist=1):
                    user_affected = True
            # Any other streetname can be searched in full
            elif find_near_matches(u.streetname, disruption.text_en, 
                                   max_l_dist=1):
                    user_affected = True

        # if user is affected, set disruption text to User object
        if user_affected == True:
            print(f"User affected: {u.name}")
            u.generate_communications(disruption)
            # Add User to affected user list
            affected_users.append(u)

    return affected_users



def email_affected_user(user: User):
    """ Emails the disruption notification to affected users """
    print(f"emailing {user.name}")
    # define settings
    port = 465
    sender_email = config('EMAIL_USER', default='')
    sender_password = config('EMAIL_PW', default='')

    context = ssl.create_default_context()
    # Generate email message
    message = MIMEMultipart('alternative')
    message["subject"] = user.email_subject
    message["from"] = sender_email
    message["to"] = user.email
    # Use MIME multipart for those that only recieve plaintext emails
    mime1 = MIMEText(user.email_text_plaintext, "plain")
    mime2 = MIMEText(user.email_text_html, "html")
    message.attach(mime1)
    message.attach(mime2)
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        # Login to the server
        server.login(sender_email, sender_password)
        # Send email
        server.sendmail(sender_email, user.email, message.as_string())
        # Cut server connection
        server.close()



def process_disruptions(database: Database, url: str, disruptions: list, 
                        users: list, new_url: bool):
    """Iterates over disruptions. If a new disruption is found, 
        save it to the database and email any affected users."""
    print("processing disruptions")
    for d in disruptions:
        d.hash = generate_hash(d.text_ge)
        add_disruption = True

        # If False, the URL exists in the DB and the page has been updated
        if new_url == False:
            # If the hash exists in the DB, the disruption hasn't been changed
            # So it doesn't need to be processed
            if d.hash in get_disruption_hashes(database, url):
                print("disruption already in db")
                add_disruption = False

        if add_disruption:
            # Translate disruption to English, extract disruption times
            d.process()
            # Find users affected by disruption
            affected_users = find_affected_users(d, users)

            # Email affected users
            for user in affected_users:
                # If phone saved, user wants texts
                if not user.phone == None:  
                    text_user(user)
                email_affected_user(user)
            # Save translated disruption text to database
            save_disruption(database, d)



def in_list_of_dicts(dicts: list, value: str):
    """Returns true if a given value is found within a list of dictionaries"""
    for d in dicts:
        if value in d.values():
            return True



def scrape_and_save(database: Database, disruption_urls: list, disruption_func,
                    users: list, urls: list):
    """Scrapes disruption urls, translates them, 
        and saves new disruptions to DB"""
    print("Scraping urls...")
    for url in disruption_urls:
        print(url)
        # get all disruptions from URL
        disruptions = disruption_func(url)
        # Generate a hash of outages from URL
        url_hash = generate_hash("".join([d.text_ge for d in disruptions]))
        # Is URL already in DB?
        if in_list_of_dicts(urls, url):
            print("url is already in db")

            # If the hash isn't in the urls, the page has been updated
            if not in_list_of_dicts(urls, url_hash):
                print("found new/updated disruptions")
                save_url(database, url, url_hash, True)
                process_disruptions(database, url, disruptions, users, False)
            else:
                print("no new disruptions found")
        else:
            save_url(database, url, url_hash, False)
            print("url is not in db")
            process_disruptions(database, url, disruptions, users, True)
    


if __name__ == "__main__":
    text_ge= "საბურთალოს რაიონი\nგადაუდებელი სამუშაოების გამო 10:00 საათიდან 18:00 საათამდე შეზღუდვა შეეხება: ნუცუბიძის IV მიკრორაიონის, ყაზბეგის გამზირის (ნაწილობრივ), პეკინის გამზირის (ნაწილობრივ), საბურთალოს, თამარაშვილის, ქუთათელაძის, უნივერსიტეტის, ლორთქიფანიძის, ცინცაძის, კუტუზოვის, საირმის, მიცკევიჩის, გამრეკელის, შმიდტის, იოსებიძის, ხვიჩიას, ბახტრიონის, ფანასკერტელ-ციციშვილის, კოსტავას, ცაგარელის და იყალთოს ქუჩების მოსახლეობას.\n გადაუდებელი სამუშაოების გამო 11:00 საათიდან 18:00 საათამდე შეზღუდვა შეეხება: დიდი დიღმის I მიკრორაიონის, პეტრე იბერის, გიორგი ბრწყინვალეს და მეფე მირიანის ქუჩების მოსახლეობას."
    announcement_ge = "სხვადასხვა სამუშაოების ჩატარების გამო 6 თებერვალს ელექტრომომარაგება დროებით შეიზღუდება"
    d = Disruption(text_ge, announcement_ge,"Electricity", "http://www.telasi.ge/ge/power/15698")
    d.process()
    test_user = User('1', 'Shash', 'shashwighton@gmail.com', 'Ikalto street', 'Saburtalo', '598865300')
    test_user.generate_communications(d)
    # print(test_user.id)
    # if not test_user.phone == None:
    email_affected_user(test_user)
        # text_user(test_user)

    # text = "Saburtalo district, water supply will be interrupted from 02/13 16:00 to 02/14 01:00 in order to carry out damage restoration works on the water pipeline network on Oseti Street: In Saburtalo district: Mukhran Machavariani, Oseti, Beritashvili streets.In the Vaki district: Amashukeli, Mary Davitashvili, Varden Tsulukidze, Varini and Nutsubidze N77 streets, Nutsubidze 3 m/r 1 sq.m. N4, 5, 6, 7, 8, 15, 16."

    # street = "tabidze"

    # print(find_near_matches(street, text, max_l_dist=1))