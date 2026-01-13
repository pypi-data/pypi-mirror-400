def to_darija(word):
    """
    Translates common English words to Moroccan Darija.
    Example: to_darija('thanks') -> 'Shokran'
    """
    dictionary = {
        "hello": "Slam",
        "hi": "Slam",
        "thanks": "Shokran",
        "thank you": "Shokran bzaf",
        "how are you": "Labass?",
        "good": "Mzyan",
        "bad": "Khayb",
        "goodbye": "Bslama",
        "please": "3afak",
        "yes": "Ah",
        "no": "La",
        "friend": "Sahbi",
       
    }
    
    clean_word = word.lower().strip()
    return dictionary.get(clean_word, f"Samhli,  ma3reftch '{word}' (Sorry, I don't know )")

def say_hello_hassena():
    """Returns a special greeting from Hassena."""
    return "Slam mn 3nd Hassena! Merhba bik."
