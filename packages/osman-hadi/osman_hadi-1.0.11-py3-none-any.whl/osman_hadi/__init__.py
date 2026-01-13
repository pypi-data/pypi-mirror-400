# osman_hadi/__init__.py

from .osman_bio import bio
from .osman_edu import edu
from .osman_career import career
from .osman_family import family
from .osman_july import july_uprising as july_hadi
from .osman_quotes import quotes
from .osman_initiatives import initiatives
from .osman_martyrdom import martyrdom

# ছবি দেখানোর কমান্ডসমূহ
from .styles import his_face1, his_face2, his_face3, his_face4, his_face5

def show_all(lang='b'):
    """
    একসাথে সব তথ্য দেখার জন্য।
    lang='b' দিলে বাংলা এবং lang='e' দিলে ইংরেজি দেখাবে।
    """
    bio(lang)
    edu(lang)
    career(lang)
    family(lang)
    july_hadi(lang)
    initiatives(lang)
    quotes(lang)
    martyrdom(lang)

def help():
    print("""
    --- SHAHEED OSMAN BIN HADI ARCHIVE HELP ---
    
    ব্যবহার বিধি:
    প্রতিটি কমান্ডের ভেতর 'e' দিলে ইংরেজি এবং 'b' দিলে বাংলা দেখাবে।
    উদাহরণ: bio('e') অথবা show_all('e')
    
    Commands:
    1. bio(lang)         -> Biography (জীবন পরিচিতি)
    2. edu(lang)         -> Education (শিক্ষাজীবন - ঢাবি ও মাদরাসা)
    3. career(lang)      -> Career (কর্মজীবন ও লেখক সত্তা)
    4. family(lang)      -> Family (পরিবার ও একমাত্র পুত্র সন্তান)
    5. july_hadi(lang)   -> July Uprising (জুলাই বিপ্লব ও প্রতিরোধ)
    6. initiatives(lang) -> Initiatives (ইনকিলাব মঞ্চ ও উদ্যোগসমূহ)
    7. quotes(lang)      -> Quotes & Philosophy (ঐতিহাসিক উক্তি ও দর্শন)
    8. martyrdom(lang)   -> Martyrdom (শাহাদাত ও শেষ বিদায়)
    9. show_all(lang)    -> Display all information at once.
    
    Face Art: his_face1() to his_face5()

    -----------------------------------------------------
    সোর্স কোড ও যোগাযোগ (Source Code & Contact):
    -----------------------------------------------------
    Source Code: https://github.com/mahadi99900/Osman_Hadi
    
    For any corrections or queries, contact the developer:
    WhatsApp & Telegram: +8801701902728
    Email: islammdmahadi943@gmail.com
    
    যেকোনো ভুল বা তথ্যের প্রয়োজনে সরাসরি যোগাযোগ করুন।
    -----------------------------------------------------
    """)
