from deep_translator import GoogleTranslator
import sqlite3
from fuzzysearch import find_near_matches


disruption_text = (" ხვალ,15  ნოემბერს ჯორჯიან უოთერ ენდ ფაუერი  საგურამოს  სათავე  ნაგებობაზე წყალმომარაგების სტაბილურობისთვის აუცილებელ სამუშაოებს ჩაატარებს. \n ტექნიკური სამუშაოები 15 ნოემბერს დღის 13:00 საათიდან დაიწყება,   მთელი დღისგანმავლობაში ინტენსიურ რეჟიმში გაგრძელდებადა 16 ნოემბრის დილის 08:00 სთ-ზე დასრულდება. \n აღნიშნულთან დაკავშირებით აუცილებელია მაგისტრალური ქსელის წყლისგან დაცლა, რის გამოცხვალ, 15 ნოემბერს დღის 13:00 საათიდან 16 ნოემბრის დილის 08:00 საათამდე წყალმომარაგება შეეზღუდება: \n გლდანის რაიონში - გლდანის ''ა“I,II,III,IV,V,VI,VII,VIII მკრ სოფელ ბერთუბანს, გიორგიწმინდას დასახლებას, ტიხონოვის, ხერგიანის, წინამძღვრიშვილის, მარჯანიშვილის,მიქატაძის,გულისაშვილის,მაისურაძის,მებაღიშვილის ქუჩებს.თიანეთის გზატ. გლდანის საპატიმროს, ჰაიდერბერგცემენტს. ახმეტელის მეტროს  მიმდებარედ ორგანიზაციებს , შეშელიძის ქუჩას, იპოლიტოვ-ივანოვის, სარაჯიშვილის, ზარზმის, ილორის, ანდრონიკაშვილის,  ქერჩის, ვასაძის, მორეტის, ხიზაბავრის, ხიზანიშვილის, ფ. მოსულიშვილის,ლიბანის, ბარისახოს, უწერის, ყუშიტაშვილის, ვარდევანის, ხეჩუაშვილის, გაგრის, ბარალეთის, გლდანის ხევის,ნანეიშვილის ,ჯანჯღავას, კაჭარავას, მეგობრობის,ჭრებალოს ქუჩა თავისი ჩიხებით, 9 ძმა ხერულიძის, 26 მაისის, გმირი კურსანტების (ყოფილი უშიშროების აკადემის). ანგია ბოჭორიშვილის, ვართაგავას ქუჩებს. \n ზაჰესში გრ. ხანძთელის, სხვიტორის, კასკადის ენერგეტიკის ქუჩებს.\n საბურთალოს რაიონში -  ქოშიგორა (ჭავჭავაძის , უდაბნოს, მოწამეთას, კელასაურის, ასი ათაში მოწამეტას ქუჩებს), სასოფლოს დას, სოფ. ზურგოვანს (კოსტავას, ჩოხელის, სამაჩაბლოს, აფხაზეთის), ვიქტორ ნოზაძის ქუჩას, ამერიკის საელჩოს მიმდებარე დას, მუხათგვერდის გზას, დიღმის სასწავლო მეურნეობას, დიდ დიღომს მიკრო რაიონებით (1, 2, 3, 4 მრ/ებს) და მიმდებარე კერძო დას; ბენდუქიძის დასახლებას, ხელაშვილის, ფარნავზის, გ.ბრწყინვალეს, დ.თავდადებულის, პეტრიწის, ფერაძის,მირიან მეფის, ფარნავაზ მეფის, ტარიელის, თინათინის, არჩილ მეფის, კრისტოფერ კასტელის, არქანჯელო ლამბერტის, კრისტიან სტივენის, იან ჰომერის, ნესტან-დარეჯანის, ავთანდილის, ჩოლოყაშვილის, ფატმანის, რჩეულიშვილის, სოფელ დიღომში: გ.ბრწყინვალეს, სტრაბონის, გოგიაშვილის, მაქს ტილკეს, ცხაკაიას, გეხტმანის, ჭანდარის, ჰენრიკ პრინევსკის, ასმათის, ჰაინრიხ კლაპროთის, არჩილ მეფის, რამაზის, ჯავახიშვილის, ბერტა ფონ ზუტნერის, სონღულაშვილის, უგრელიძის, მარკო პოლოს, ჟოზეფ ტურნეფორის, კრისტოფერ კასტელის, ფედერიკ მონპერეს, არქანჯელო ლამბერტის, კრისტიან სტივენის, იან ჰომერის, იაკობ რაინეგსის, ნიკო ბურის, ბარონ დე ბაის, ჰუგო ჰუბერტის, დანიბეგაშვილის, ხატაეთის, შერმადინის, ნესტან-დარეჯანის, ფატმანის, ავთანდილის, დავარის, ვეფხისტყაოსნის, გულანშაროს, მულღაზანზარის, ნურადინ ფრიდონის, ცამეტი ასურელი მამის, სარაჯიშვილის, ათონელის, დიდგორის, იოაკიმე და ანას, ჩოლოყაშვილის, ხანძთელის, ფიროსმანის და ჭიაურელის ვაჟა-ფშაველას, ყაზბეგის, როსტევანის, ისიდორე დოლიძის, შეყლაშვილის, ლუარსაბ ანდრონიკაშვილის, გრიგოლ ჩხიკვაძის, დავით აღმაშენებლის, თამარ მეფის, მიხეილ მესხის, ფატმანის, კვირაცხოვლის, მუხრან მაჭავარიანის, ჭელიძის, ჯანიაშვილის, მაყაშვილის, ბიძინა ბარათაშვილის, სარგის კაკაბაძის, ბატონიშვილის, რჩეულიშვილის, შმერლინგის და თეთრი დუქნის ქუჩებს, დაცვის პოლიციის დეპარტამენტს, ცენტრალურ საარჩევნო კომისიას, ტოიოტას მიმდებარე ახალ დასახლება, საქალაქო სასამართლოს და მიმდებარე დასახლებას; თინათინ წერეთლის, ვალენტინ თოფურიას, თოფურიძის, ციალა გაბაშვილის ქუჩებს, ვაშლიჯვრის დასახლების კორპუსებს, ვაშლიჯვრის კერძო დასასახლებას, სარაჯიშვილის, კვანტალიანის, გოძიაშვილის ქუჩებს, შესახვევებს და კორპუსებს, მარშალ გელევანის გამზირს, სოფლის მეურნეობის სამინისტროს და მიმდებარე დასახლება, იასამნის, ბროწეულის, ბაქრაძის დაგოთუას ქუჩებს, გაგარინის 5, 19/2, ჰეიდარ აბაშიძის, ლვოვის, ოდესის, ოსეთის, ლომონოსოვის, მიხეილ \n ასათიანის, გივი კარტოზიას ქ.8, ტაშკენტის ქუჩა N51-65(კენტები), N54-78(ლუწები)ბუდაპეშტის N 1-11(კენტები)N2-10(ლუწები), კანდელაკის, ნუცუბიძის ქ, 2, თამარაშვილის, ზემო ვეძისის ქუჩას, ვაზისუბნის და ალასანიას ქუჩებს.\n დიდუბის რაიონში: აღამაშენბლის ხეივანი მე-12 კილომეტრს, დიღმის მასივი I კვ-ის N10, 11, 12 კორპუსებს.\n ჯორჯიან უოთერ ენდ ფაუერი ბოდიშს უხდის მომხმარებლებს დისკომფორტისთვის. სამუშაოების მიმდინარეობისას, წყალმომარაგების სრულად აღდგენამდე კომპანია მოსახლეობას წყალს ცისტერნებით მიაწვდის.")
if len(disruption_text) > 4000:
    # Split disruption_text into paragraphs
    paragraphs = disruption_text.split("\n")
    # Create list to store translated paragraphs
    translated_paragraphs = []
    # Iterate over paragraphs
    for p in paragraphs:
        if len(p) == 0:
            translated_paragraphs.append("\n")
        # Split paragraphs into sentences
        sentences = p.split(".")
        # Translated sentences
        translated_sentences = GoogleTranslator(source='ka', target='en').translate_batch(sentences)
        # Join translated sentences together to form translated paragraph
        translated_p = "".join(translated_sentences)
        # Add translated paragraph to list
        translated_paragraphs.append(translated_p)
    # Join translated paragraphs together to form translated disruption_text
    translated_disruption_text = "\n".join(translated_paragraphs)
    

else: 
    translated_disruption_text = GoogleTranslator(source='ka', target='en').translate(disruption_text)

# print(translated_disruption_text)

class User:
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
        self.email_text = "Hi {name},\n\nYour street has been included in a list of streets affected by a utility disruption in Tbilisi.\nPlease see the following warning for more details:\n\n{disruption_text}"

    def generate_email_text(self):
        return self.email_text.format(name=self.name, disruption_text=self.disruption_text)

# Iterates over users in DB and emails them if the disruption affects them
def find_affected_users(disruption_text: str):
    # Connect to the user DB
    con = sqlite3.connect("utility_scraper.db")
    c = con.cursor()

    # Create User objects from users in DB
    users = []
    for u in c.execute("SELECT * FROM users"):
        # Users are stored in db as (name, email, street, suburb)
        new_user = User(u[0], u[1], u[2])
        users.append(new_user)

    # Iterate over users and find those affected by cut
    for u in users:
        print(u.streetname)
        if find_near_matches(u.streetname, disruption_text, max_l_dist=3):
            print("match found")
            u.disruption_text = disruption_text
            email = u.generate_email_text()
            print(email)
        else:
            print("match not found")

            
    con.close()


find_affected_users(translated_disruption_text)