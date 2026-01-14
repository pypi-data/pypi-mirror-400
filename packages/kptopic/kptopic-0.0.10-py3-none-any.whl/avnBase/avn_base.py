
from spellchecker import SpellChecker
import os,re,spacy
from unidecode import unidecode
import torch
import pandas as pd
from maverick import Maverick
from typing import List
from spacy.language import Language
import unicodedata
from spacy.matcher import PhraseMatcher
from itertools import combinations
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import wordnet as wn
import networkx as nx
import ast

# ADJ -ADV, ADJ -NOUN, ADV-VERB, VERB-NOUN 
#text = "girls has extremely wonderful food and drink, boy are loved deeply by grandparents."

# NOUN, PROPN, ENTITY (only get lenght larger than 2 )
# VERB(AUX), ADJ, ADV

# nlp = spacy.load("en_core_web_trf") 

#text = "Harry Potter, the leading tourism scholar, google , Apple company in rovaniemi  has good prodcut in Finland , applies artificial intelligence ,natural language processing to Finnish business. University of Eastern Finland peng(at)hotmail dot com, peng@uef.fi www.uef.fi or uef.fi"
# Define the set of negating lemmas
#NEG_LEMMAS = {"no", "not", "n't", "never", "none", "nothing", "nobody", "no one", "neither","nor"} # nobody, nothing, none will be kept in the results as NOUN 



@Language.component("custom_sentencizer")
def custom_sentencizer(doc):
    """nlp.add_pipe("custom_sentencizer", before="parser")

    doc = nlp("I do not love you, neither you nor me is good, I haven't checked the food yet, how about we are just waiting for mother")

    for sent in doc.sents:
        print("SENT:", sent.text)"""
    for i, token in enumerate(doc):
        # Define words that can start new sentences
        sentence_starters = ["neither", "however", "how", "but", "so",
                             "i", "we", "they", "you", "he", "she", "it","none"]

        # Mark as sentence start if token matches and is not the first token
        if token.text.lower() in sentence_starters and i > 0:
            # Also ensure the previous token is punctuation or comma
            if doc[i - 1].text in [",", ".", "!", "?",";","-","--"]:
                token.is_sent_start = True
    return doc


def spaceOut(text):
    """ make space of emojis"""
    #targets = {',', '.', '!', '?', ';'}
    output = []
    
    for char in text:
        # Check if it's one of your specific punctuation marks
        #if char in targets:
            #output.append(f" {char} ")
        # Check if it's an emoji (Unicode range for most emojis)
        if ord(char) > 0x2000: 
            output.append(f" {char} ")
        else:
            output.append(char)
            
    # Join and clean up double spaces
    return " ".join("".join(output).split())


def word_similarity(word1, word2, pos=wn.NOUN):
    """find two words simliarty 

    Args:
        word1 (string): word1
        word1 (string): word1
        pos (part of speech, optional): wn.VERB,wn.NOUN,wn.ADJ,wn.ADV. Defaults to wn.NOUN.

    Returns:
        foat: word simliarity 0-1 
    """
    synsets1 = wn.synsets(word1, pos=pos)
    synsets2 = wn.synsets(word2, pos=pos)

    # Exit early if either word has no synsets (e.g., not in WordNet or incorrect POS)
    if not synsets1 or not synsets2:
        return 0.0

    max_sim = 0.0
    for s1 in synsets1:
        for s2 in synsets2:
            if s1 is not None:
                sim = s1.wup_similarity(s2)
                
            # This check is crucial: It ignores any sim value that is None
            if sim is not None and sim > max_sim:
                max_sim = sim
    
    return max_sim

# Example usage (assuming 'tree' and 'bush' are Noun synsets)
# print(word_similarity('tree', 'bush', pos=wn.NOUN))




def uniSimilarNodesDF(original_edges, col1 ='node1',col2='node2', pos ='NOUN',minSimilar = 0.91,manual_pairs=None):
    """mapping the high simaliry ndoes in nodes dataframe, e.g. replace time to period , if both in the nodes 

    Args:
        original_edges (_type_): dataframe with columns by node1 and node2 of edge 
        col1,col2 : nodes column names
        pos: simliarty coparison by part of speech, only NOUN, VERB 
        minSimilar: set the minimal value of similarity # food drink 0.909 
        manual_pairs (dict): Optional dictionary of { 'old_value': 'new_value' }
    Return:
           new nodes dataframe replaced simliar words, simlilarity mapping  
    """
    if pos =='NOUN':
        pos1 = wn.NOUN
        pos_cut = '_2noun'
    else:
        raise ValueError(f"Unexpected pos found: '{pos}'. we only take NOUN simliarity, please add other pairs manually")
    noun_nodes = original_edges[col1].tolist() + original_edges[col2].tolist()
    noun_nodes1 = set(noun_nodes)
    noun_nodes2 = [node for node in noun_nodes1 if pos_cut in node]
    

    noun_pairs = list(combinations(noun_nodes2, 2))
 
    #simPairs = {}
    simPairs = manual_pairs.copy() if manual_pairs else {}
    for pair in noun_pairs:
        
        word1 = pair[0][:-6]
        word2 = pair[1][:-6]
        simV = word_similarity(word1,word2, pos=pos1)   # food drink 0.909 
        if simV > minSimilar:
            simPairs.update({pair[0]:pair[1]})

    # Apply the replacement to specific columns
    cols_to_fix = [col1, col2]
    #original_edges[cols_to_fix] = original_edges[cols_to_fix].replace(simPairs)
    original_edges.loc[:, cols_to_fix] = original_edges[cols_to_fix].replace(simPairs)
    simPairs = pd.DataFrame(list(simPairs.items()), columns=['key', 'value'])
    return original_edges, simPairs  





UNICODE_TO_ASCII = {
    '’': "'",   # Right Single Quote (Apostrophe)
    '‘': "'",   # Left Single Quote
    '“': '"',   # Left Double Quote
    '”': '"',   # Right Double Quote
    '–': '-',   # En Dash
    '—': '-',   # Em Dash
    '…': '...', # Ellipsis
    # Add any other non-emoji problematic chars here (e.g., U+00A0 non-breaking space)
}

def convert_specific_unicode(text,UNICODE_TO_ASCII = UNICODE_TO_ASCII):
    """Replaces specific Unicode characters (non-emojis) with their ASCII equivalent."""
    for unicode_char, ascii_char in UNICODE_TO_ASCII.items():
        text = text.replace(unicode_char, ascii_char)
    return text

def merge_emoji_tokens(doc):
    spans = []
    i = 0
    while i < len(doc) - 1:
        # Check if next token is a ZWJ or emoji modifier
        if i + 1 < len(doc) and doc[i+1].text in ['\u200d', '\ufe0f', '♂️', '♀️']:
            start = i
            end = i + 2
            while end < len(doc) and doc[end].text in ['\u200d', '\ufe0f', '♂️', '♀️']:
                end += 1
            
            # If the sequence ended on a ZWJ, grab the next emoji char
            if end < len(doc) and doc[end-1].text == '\u200d':
                end += 1
                
            spans.append(doc[start:end])
            i = end
        else:
            i += 1

    with doc.retokenize() as retokenizer:
        for span in spans:
            # CLEAN THE TEXT: Remove the ZWJ from the merged token's text
            clean_text = span.text.replace('\u200d', '').strip()
            
            # Force the merged token to be a NOUN so semanticEdges likes it
            retokenizer.merge(span, attrs={"ORTH": clean_text, "LEMMA": clean_text, "POS": "NOUN"})
            
    return doc



def is_ascii_word(word):
    try:
        word.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False
spell = SpellChecker()
def spellCorrect(text,nonCheckWords = ['offf']):
    """_summary_

    Args:
        text (_type_): _description_
        nonCheckWords (list, optional): _description_. Defaults to ['offf'].

    Returns:
        _type_: _description_
    """
    
    
    # Split text into words and punctuation
    tokens = text.split()
    spell.word_frequency.load_words(nonCheckWords)
    corrected_tokens = []
    for token in tokens:
        if token.isalpha() and is_ascii_word(token):
            corrected = spell.correction(token)
            
            corrected_tokens.append(corrected if corrected else token)
        elif len(token)>0:
            corrected_tokens.append(token)
            
        
    return " ".join(
        corrected_tokens
                    )



class MaverickCoref:
    """
    word coreference 
    # Make sure dependencies are installed:
    # pip install torch transformers hydra-core pytorch-lightning
    # pip install --no-deps git+https://github.com/Atsaniik/maverick-coref.git

    # hf download sapienzanlp/maverick-mes-preco --local-dir ./maverick-mes-preco
    # hf download sapienzanlp/maverick-mes-ontonotes --local-dir ./maverick-ontonotes

    # import nltk
    # nltk.download('punkt_tab')

    # To uninstall existing torch (if using pip)
    # pip uninstall torch torchvision torchaudio
    # pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 , instll the cuda 

    """
    _model = None
    _device = None
    
    # Store the path used to load the current cached model
    _loaded_path = None 

    @classmethod
    def _ensure_model_loaded(cls, path=None, device=None):
        """
        Internal method to load and cache the model ONLY if it hasn't been loaded yet 
        OR if a different path/device is requested.
        """
        # Define the path to use for this check
        default_path = os.path.join(os.getcwd(), "sapienzanlp", "maverick-ontonotes")
        path_to_use = path if path is not None else default_path
        
        # 1. Auto-detect CUDA only if device is not explicitly set
        if device is None:
            device_to_use = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device_to_use = device

        # 2. Load model ONLY if it's the first time OR if the device/path has changed
        if cls._model is None or cls._device != device_to_use or cls._loaded_path != path_to_use:
            cls._device = device_to_use
            cls._loaded_path = path_to_use # Update the stored path
            print(f"Loading Maverick model from {path_to_use} on {cls._device.upper()}...")
            
            try:
                cls._model = Maverick(
                    hf_name_or_path=path_to_use,
                    device=cls._device
                )
            except Exception as e:
                print(f"Error loading model from path: {path_to_use}. Error: {e}")
                # Reset cache variables if loading fails
                cls._model = None
                cls._device = None
                cls._loaded_path = None
                raise # Re-raise the exception to stop execution

    @classmethod
    def resolve(cls, text, device=None, path=None)-> str: # Added 'path' argument
        """
        Resolves coreference chains in the input text using the cached model.

        Args:
            text (str): The input text string.
            device (str, optional): The device to use. Defaults to auto-detect.
            path (str, optional): The path to the Maverick model. If provided, 
                                  it will override the default path and force a reload 
                                  if the model is not already loaded from this location.

        Returns:
            str: The text with coreferences resolved.
        """
        # 1. Ensure the model is loaded, passing both device and the optional path
        # This will trigger a reload if the model in cache was loaded from a different path.
        cls._ensure_model_loaded(path=path, device=device) 
        
        # 2. Directly access the cached model, which is guaranteed to be loaded here
        model = cls._model
        assert model is not None
        # 3. Proceed with prediction using the model instance
        result = model.predict(text)
        resolved_tokens = result['tokens'][:]

        for cluster in result['clusters_token_offsets']:
            first_mention = cluster[0]
            first_mention_text = " ".join(result['tokens'][first_mention[0]:first_mention[1]+1])
            
            for mention in cluster[1:]:
                start, end = mention
                resolved_tokens[start] = first_mention_text 
                for i in range(start+1, end+1): 
                    resolved_tokens[i] = ""

        return " ".join([tok for tok in resolved_tokens if tok])
   

def replace_word(text, old, new, case_insensitive=True):
    "replace strictly of words of old to new but protect the other forms such as old.com , older"
    flags = re.IGNORECASE if case_insensitive else 0
    pattern = rf'(?<![\w@./?&=#-]){re.escape(old)}(?![\w.])'
    return re.sub(pattern, new, text, flags=flags)



def verbPhrase(doc):
    """
    Detects compact phrasal and prepositional verbs like:
    'give up', 'take off', 'look after', 'put up with', 'give away', 'turn off'.
    Returns list of base-form verb phrases (lemma-based) and new text 
    """
    
    #doc = nlp(text)
    new_text =  doc.text
    results = []
    valid_particles = {
        "up", "off", "away", "out", "over", "back",
        "down", "on", "in", "with", "into", "by","after"
    }

    for token in doc:
        if token.pos_ != "VERB":
            continue

        phrase_parts = [token.lemma_]
        found = False

        # --- Direct particle or preposition ---
        for child in token.children:
            if (
                child.text.lower() in valid_particles
                and child.dep_ == "prt" #   child.dep_ == in {"prt", "prep"} deprecated on 6.01.2026
            ):
                phrase_parts.append(child.text)
                #print('new_phrase', child.text,doc[token.i +1])
                if child.text != doc[token.i +1].text:
                    
                    new_text = new_text.replace(doc[child.i].text,"").replace(doc[token.i].text, " ".join([token.lemma_,child.text]))
                    
                found = True

        if found:
            results.append(" ".join(phrase_parts))
            continue



    return  list(dict.fromkeys(results)), new_text




def is_emoji(token):
    # Emojis are symbols with Unicode category starting with 'So'
    return any(unicodedata.category(char).startswith('So') for char in token.text)

def cleanEEL(doc,cleanEMOJI = False):
    """ remove the emojis, emails, urls 
    Args:
        doc (doc): spacy doc 
        nlp (lanaguge): spacy nlp model , for better detection esepaiclly emails and urls , spacy.load("en_core_web_trf") is recommended

    Returns:
        tuple[str, list[str], list[str], list[str]]:
            (cleaned_text, emojis, emails, urls)
    """
    #doc = nlp_trf(text)
    cleaned_tokens = []
    emails = []
    urls = []
    emojis = []
    for token in doc:
        # Skip if it's an email, URL, or emoji
        if token.like_email:
            emails.append(token.text)
            continue
        if token.like_url:
            urls.append(token.text)
            continue
        if cleanEMOJI:
            if is_emoji(token):
                emojis.append(token.text)
                continue

        cleaned_tokens.append(token.text)

    return " ".join(cleaned_tokens), emojis, emails, urls 

    # Example
    #sample_text = "Contact me at hello@sample.com 😄 or visit https://example.com for details! Peng Yang, the leading tourism scholar, applies natural language processing to  Finnish business. peng(at)hotmail dot com, peng@uef.fi www.uef.fi or uef.fi"
    #cleaned,emojis, emails, urls = cleanEEL(sample_text,nlp)
    #print(cleaned,emojis, emails, urls,sep="\n" )


def cleanDetNum(text,nlp:Language, det=["a", "an", "the"],numberWords =True ):
    """remove the Determiner a , an ,the and numbers but keep COVID-19, G20

    Args:
        text (string): any text 
        det (list, optional):det. Defaults to ["a", "an", "the"].
        numberWords(bool): if True, will remove any numbers including words such as one, two , zero. 

    Returns:
        str: new text without determiner or numbers
    """
    doc = nlp(text)
    cleaned_tokens = []

    for token in doc:
        lower = token.text.lower()

       
        if token.pos_ == "DET" and lower in det:
            continue
        
        if numberWords:
            if (
                token.like_num or
                re.fullmatch(r"\d+", token.text)
            ):
                # But keep tokens that have letters or hyphens (like COVID-19, G20)
                if not re.search(r"[A-Za-z-]", token.text):
                    continue
                if re.match(r".*[A-Za-z]+-\d+.*", token.text):
                    pass  # keep COVID-19
                else:
                    continue

        cleaned_tokens.append(token.text)

    return " ".join(cleaned_tokens)

    # Example
    #text = "The COVID-19 pandemic G200 20 kids , 3.14 one trillion lasted thirty one months and affected 9 million people in a year."
    #print(cleanDetNum(text,nlp2,numberWords=False))



def cleanText(text, nlp, det=None, valid_particles =None, number_words=True, clean_emoji=False, heavy_number = False,verbPhrase = False, extraClean = False
              ,reADJ=['meilide'], reADV=['piaoliangdi'],reVERB=['caiquxingdong'], 
              reNOUN=['Natural Language Processing'],reENT = True,hyphenated = True,):
    """
    Integrates text cleaning (removing determiners, numbers, URLs, emails) 
    with phrasal verb detection and normalization.
    
    Args:
        text (str): The raw input text.
        nlp (spacy.lang): Loaded Spacy language model.
        det (list): List of determiners to remove.
        verbPhrase: if true, then 'take it off' beacome 'take off it' in the new text
        valid_particles(set): valid_particles = {
                            "up", "off", "away", "out", "over", "back",
                            "down", "on", "in", "with", "into", "by", "after"
                                                                            }
        heavy_number(bool): If True, remove all numbers including COVID-19, G20, etc
        number_words (bool): If True, remove numbers (keeping COVID-19, G20, etc).
        clean_emoji (bool): If True, removes emojis.
        
    Returns:
        tuple: (cleaned_text, verb_phrases_list, emails_list, urls_list, emojis_list)
    """
    if det is None:
        det = ["a", "an", "the"]
    text = re.sub(r'([()\[\]{}])', r' \1 ', text)  # make space before and after both (,)
    #doc = nlp(text)
    doc = docRetoken(text, nlp,reADJ=reADJ, reADV=reADV,
                         reVERB=reVERB , reNOUN=reNOUN,
                         reENT = reENT,hyphenated = hyphenated)
    
    # --- Output Containers ---
    cleaned_tokens = []
    verb_phrases_found = []
    emails = []
    urls = []
    emojis = []
    
    # --- Phrasal Verb Configuration ---
    if valid_particles is None:
        valid_particles = {
            "up", "off", "away", "out", "over", "back",
            "down", "on", "in", "with", "into", "by", "after"
        }
    
    
    # Maps a verb's token index to its new string (e.g., "take off")
    verb_replacements = {} 
    # Set of token indices (particles) to skip during reconstruction
    indices_to_skip = set() 

    # ---------------------------------------------------------
    # PASS 1: Identify Phrasal Verbs (Dependency Parsing)
    # ---------------------------------------------------------
    if verbPhrase:
        for token in doc:
            if token.pos_ == "VERB":
                # Check children for particles
                for child in token.children:
                    if (child.text.lower() in valid_particles 
                        and child.dep_ == "prt"):   #  child.dep_ == "prt" updated 6.jan.2026 , child.dep_ in {"prt", "prep"}) 
                        
                        # We found a phrasal verb (e.g., "took ... off")
                        lemma_phrase = f"{token.lemma_} {child.text.lower()}"
                        
                        # Store the result
                        verb_phrases_found.append(lemma_phrase)
                        
                        # Logic for text reconstruction:
                        # 1. Mark the particle to be skipped later
                        indices_to_skip.add(child.i)
                        
                        # 2. Mark the verb to be replaced by "lemma + particle"
                        # Note: This unifies split verbs. "took it off" -> "take off it"
                        verb_replacements[token.i] = lemma_phrase
                        
                        # Only handle one particle per verb to avoid conflicts
                        break 

    # ---------------------------------------------------------
    # PASS 2: Filter Tokens and Reconstruct Text
    # ---------------------------------------------------------
    for token in doc:
        # 1. specific logic to skip particles of phrasal verbs
        if token.i in indices_to_skip:
            continue
            
        # 2. Extract specific entities
        if token.like_email:
            emails.append(token.text)
            #print(f'email:{token.text}')
            continue # Remove email from text? Remove this 'continue' if you want to keep it.
            
        if token.like_url:
            urls.append(token.text)
            #print(f'url:{token.text}')
            continue # Remove URL from text? Remove this 'continue' if you want to keep it.
            
        # 3. Emoji Logic
       
        # Simple check: if non-ascii and character category is Other Symbol (So)
        if is_emoji(token): 
            emojis.append(token.text)
            #print(f'emoji: {token.text}')
            if clean_emoji:
                    continue

        # 4. Determiner Logic
        if token.pos_ == "DET" and token.text.lower() in det:
            continue
            
        # 5. Number Logic
        if heavy_number:
            if number_words:
                is_number = (token.like_num or re.fullmatch(r"\d+", token.text))
                if is_number:
                    # Preservation Logic for G20, COVID-19
                    has_letters = re.search(r"[A-Za-z]", token.text)
                    is_compound = re.match(r".*[A-Za-z]+-\d+.*", token.text) # e.g. COVID-19
                    
                    if not has_letters: 
                        continue # Pure number -> skip
                    elif not is_compound and not has_letters:
                        continue # Redundant check, but keeps logic clear
                    
      
        else:
            if number_words:
                if token.like_num:
                    continue

                # contains any digits?
                if any(ch.isdigit() for ch in token.text):
                    # keep if contains letters OR hyphens → "COVID-19", "G20"
                    if any(ch.isalpha() for ch in token.text) or "-" in token.text:
                        pass  # keep
                    else:
                        continue
      
      
        #print('clean_text process --------', token.text )
        # 6. Text Reconstruction
        if verbPhrase:
            if token.i in verb_replacements:
                # This is the verb part of a phrasal verb -> Insert the full lemma phrase
                cleaned_tokens.append(verb_replacements[token.i])
            else:
                # Standard token -> Insert text
                cleaned_tokens.append(token.text)
        else:
            # Standard token -> Insert text
            cleaned_tokens.append(token.text)

    # Remove duplicates from results while preserving order
    unique_phrases = list(dict.fromkeys(verb_phrases_found))
    
    # Join cleaned text
    final_text = " ".join(cleaned_tokens)
    
    
    if extraClean:
        #final_text = re.sub(r'\s+([?.!,"])', r'\1', final_text) # Cleanup extra spaces around punctuation (optional polish)
        final_text = re.sub(r'\(.*?\)', '', final_text)  # remove () Remove parentheses and everything inside them
        final_text = re.sub(r'\s+', ' ', final_text).strip()

    return final_text, unique_phrases, emails, urls, emojis







def docRetoken(text, nlp, reADJ=['meilide'], reADV=['piaoliang'],reVERB=['caiquxingdong'], reNOUN=['natural language processing'],reENT = True,hyphenated = True):
    """retokenize specific words: adj,adv,verb, noun and entity 

    Args:
        text (str): _description_
        nlp (spacy nlp): _description_
        reNOUN (list, optional): list of noun to be retonized. Defaults to ['natural language processing'].
        reADJ (list, optional): _list of adj to be retonized. Defaults to ['meilide'].
        reADV (list, optional): list of adv to be retonized. Defaults to ['piaoliang'].
        reVERB (list, optional): list of verb to be retonized. Defaults to ['caiquxingdong'].
        reENT (bool, optional): if also retonize entity to noun. Defaults to True.
        hypenated(bool,opetional): if true, tokenie the hypenated word but POS it depends on the root 

    Returns:
        doc: new doc after retokenziation 
    """
    
    pinyin_rules = {
    "ADV": [nlp.make_doc(x) for x in reADV ],
    "VERB": [nlp.make_doc(x) for x in reVERB ],
    "ADJ": [nlp.make_doc(x) for x in reADJ ],
    "NOUN":[nlp.make_doc(x) for x in reNOUN]
     }
    

    # Create the PhraseMatcher
    matcher = PhraseMatcher(nlp.vocab)
    for pos_tag, patterns in pinyin_rules.items():
        matcher.add(pos_tag, patterns)

    # --- 2. Process the text ---
    doc = nlp(text)

    # Find all pinyin matches
    pinyin_matches = matcher(doc)

    # --- 3. Prepare all spans for merging ---
    # We will collect all spans (pinyin + entities) to merge them in one go.
    # We store them as (span, pos_tag)
    spans_to_merge = []
    
    if hyphenated:
        hyphenated_matches = re.finditer(r'\b\w+(?:-\w+)+\b', text)

        for match in hyphenated_matches:
            span = doc.char_span(match.start(), match.end())
            if span:
                #print(f"Span: {span.text}, POS: {span.root.pos_}")
                spans_to_merge.append((span, span.root.pos_))

    # Add pinyin matches
    for match_id, start, end in pinyin_matches:
        pos_tag = nlp.vocab.strings[match_id]
        span = doc[start:end]
        spans_to_merge.append((span, pos_tag))

    # Add entity matches (Rule: "turn all entity to noun")
    if reENT:
        for ent in doc.ents:
            # 'Peng Yang' will be found as an entity (PERSON)
            # We add it to our list with the target POS "NOUN"
            spans_to_merge.append((ent, "NOUN"))

        # Sort spans by their start index. This is crucial for retokenizing correctly.
        spans_to_merge.sort(key=lambda x: x[0].start)

    # --- 4. Retokenize in one step ---
    # Use doc.retokenize() to merge all collected spans
    with doc.retokenize() as retokenizer:
        for span, pos_tag in spans_to_merge:
            try:
                # Set the POS and TAG attributes for the merged token
                retokenizer.merge(span, attrs={"POS": pos_tag, "TAG": pos_tag})
            except ValueError:
                # This can happen if spans overlap (they don't in this case)
                # We can just skip the conflicting merge
                pass
    return doc



def get_all_conjuncts(token):
    """
    Helper function to return a list of a token and all its conjuncts.
    """
    return [token] + list(token.conjuncts)








def semanticEdges(doc,NEG_Lemmas = {"no", "not", "n't", "never", "none", "nothing", "nobody", "neither","nor"},
                            nonSemantic = 0, NN = 'notInclude',copulaBridge = True):
    """
    Analyzes doc and extracts a set of ANNOTATED semantic edges
    with POS/NEG negation labels.
    
    Note: verb and noun should put all forms and casesensetive , such as turn off, turned off, turn off; countries, country , natural language processing, Natural Language Processing
    Note2: the edge with nothing, nobody also show NEG, nothing-good-NEG then no need add label extra NEG. 
    Args:
        doc (doc): spacy nlp tokenzied doc 
        
        NEG_lemaas(set,optional): set of negating lemaas. Defaults to {"no", "not", "n't", "never", "none", "nothing", "nobody", "no one", "neither","nor"}
        nonSemantic(digit,optional): if nonSemantic = 1, then generate avn edges of non semantic text adj-adv, adj-noun, adv-verb, verb-noun 
        NN: (vaule: [inlcude, only , notInclude] ) noun-noun type nonSemantic edges, othervise A-A-V-N edge
        copulaBridge (bool): Finland is beautiful add one extra edge Finland-beautiful connected by copula Be , otherwise only Finland-be, be-beautiful 
    Returns:
        list: semantic edges with Negation labels  
    """

    
    
    #doc = docRetoken(text,nlp,reADJ=reADJs, reADV=reADVs,reVERB=reVERBs, reNOUN=reNOUNs,reENT = reENTs,hyphenated=reHyphens)
    
    edges = set()
    if 'none' in doc.text.lower():
        suffix ="NEG"
    else:
        suffix = "POS"
    for token in doc:
        dep = token.dep_
        head = token.head
      
        # Rule 1: NOUN-VERB (Subjects)
        # e.g., "girls have", "boy is loved", "nobody likes"
        if dep in ('nsubj', 'nsubjpass') and head.pos_ in ('VERB', 'AUX','SYM'):  # add 'SYM' 18.12.2025
            subjects = get_all_conjuncts(token)
            verbs = get_all_conjuncts(head)
            for s in subjects:
                for v in verbs:
                    if v.i > 0 and v.nbor(-1).lemma_.lower() in NEG_Lemmas:
                        suffix = "NEG"
                    elif s.i > 0 and s.nbor(-1).lemma_.lower() in NEG_Lemmas:  # neither you nor me like the food
                        suffix = "NEG"
                    edges.add(f"{s.lemma_}-{v.lemma_} (NOUN-VERB {suffix})")

        # Rule 2: VERB-NOUN (Objects)
        # e.g., "have food", "don't eat avocado", "none like coffee"
        #elif dep == 'dobj' and head.pos_ == 'VERB':
        elif dep in ('dobj', 'pobj', 'attr', 'dative') and head.pos_ in ('VERB', 'AUX','SYM'): # add 'SYM' 18.12.2025
            objects = get_all_conjuncts(token)
            verbs = get_all_conjuncts(head)
            
            # Find all subjects of the verb
            subjects = [c for c in head.children if c.dep_ in ('nsubj', 'nsubjpass')]
            
            for o in objects:
                for v in verbs:
                    if v.i > 0 and v.nbor(-1).lemma_.lower() in NEG_Lemmas:
                        suffix = "NEG"
                    edges.add(f"{v.lemma_}-{o.lemma_} (VERB-NOUN {suffix})")
                    
            # Rule 7: COMPREHENSIVE COPULA BRIDGE (Subject -> Attribute's Adjective)
            # Handles: "We become beautiful girls", "Finland is a safe country" to have We-beautiful , Finland-safe
            if dep == 'attr' and head.pos_ in ('VERB', 'AUX') and copulaBridge:
                # 1. Find the subjects of the copular verb (e.g., "We", "Finland")
                subjects = [c for c in head.children if c.dep_ in ('nsubj', 'nsubjpass')]
                
                # 2. Find adjectives modifying this attribute noun (e.g., "beautiful", "safe")
                # We look for 'amod' (adjectival modifiers)
                adjectives = [c for c in token.children if c.dep_ == 'amod']
                
                for s in subjects:
                    subj_conj = get_all_conjuncts(s)
                    for sc in subj_conj:
                        for adj in adjectives:
                            adj_conj = get_all_conjuncts(adj)
                            for ac in adj_conj:
                                local_suffix = suffix
                                # Check for local negation (e.g., "We become not-so-beautiful girls")
                                if ac.i > 0 and ac.nbor(-1).lemma_.lower() in NEG_Lemmas:
                                    local_suffix = "NEG"
                                
                                # Adding as NOUN-ADJ per your request (even if the subject is a pronoun like 'we')
                                edges.add(f"{sc.lemma_}-{ac.lemma_} (NOUN-ADJ {local_suffix})")                
    
    
    

        # Rule 3: ADJ-NOUN (Adjectival Modifier)
        # e.g., "wonderful food", "no tasty food"
        elif dep == 'amod' and head.pos_ == 'NOUN':
            adjectives = get_all_conjuncts(token)
            nouns = get_all_conjuncts(head)
            for a in adjectives:
                
                for n in nouns:
                    if a.i > 0 and a.nbor(-1).lemma_.lower() in NEG_Lemmas:
                        suffix = "NEG"
                        
                    edges.add(f"{a.lemma_}-{n.lemma_} (ADJ-NOUN {suffix})")

        # Rule 4: ADV-VERB / ADV-ADJ (Adverbial Modifier)
        elif dep == 'advmod':
            adverbs = get_all_conjuncts(token)
            
            # e.g., "loved deeply", "not really good"
            if head.pos_ in ('VERB', 'AUX'):
                verbs = get_all_conjuncts(head)
                for adv in adverbs:
                    for v in verbs:
                        if v.i > 0 and v.nbor(-1).lemma_.lower() in NEG_Lemmas:
                            suffix = "NEG"
                    edges.add(f"{adv.lemma_}-{v.lemma_} (ADV-VERB {suffix})")
                
            # e.g., "extremely wonderful", "not very good"
            elif head.pos_ == 'ADJ':
                adjectives = get_all_conjuncts(head)
                for adv in adverbs:
                    for adj in adjectives:
                        if adj.i > 0 and adj.nbor(-1).lemma_.lower() in NEG_Lemmas:
                            suffix = "NEG"
        
                        edges.add(f"{adv.lemma_}-{adj.lemma_} (ADV-ADJ {suffix})")

        # Rule 5: VERB-NOUN (Prepositional Objects & Agents)
        # e.g., "go to school", "is not in house"
        elif dep == 'pobj' and head.pos_ == 'ADP':
            verb = head.head
            if verb.pos_ in ('VERB', 'AUX') and head.dep_ in ('prep', 'agent'):
                objects = get_all_conjuncts(token)
                verbs = get_all_conjuncts(verb)
                
                # Find all subjects of the verb
                subjects = [c for c in verb.children if c.dep_ in ('nsubj', 'nsubjpass')]

                for v in verbs:
                    for o in objects:
   
                        if v.i > 0 and v.nbor(-1).lemma_.lower() in NEG_Lemmas:
                            suffix = "NEG"
                        edges.add(f"{v.lemma_}-{o.lemma_} (VERB-NOUN {suffix})")

        # Rule 6: NOUN-ADJ (Predicative Adjectives)
        # e.g., "food is wonderful", "food is not good"
        elif dep == 'acomp' and head.pos_ in ('VERB', 'AUX'):
            adjectives = get_all_conjuncts(token)
            subjects = [child for child in head.children if child.dep_ in ('nsubj', 'nsubjpass')]
            for s in subjects:
                subject_conj = get_all_conjuncts(s)
                for sc in subject_conj: 
                    for a in adjectives:
                        if a.i > 0 and a.nbor(-1).lemma_.lower() in NEG_Lemmas:
                            suffix = "NEG"
                        edges.add(f"{sc.lemma_}-{a.lemma_} (NOUN-ADJ {suffix})")
        
    if NN in ['only','include']:
        nonSemantic = 1                 
    # --- Add default edges if none found ---
    if  nonSemantic ==1:
        # Count negation lemmas
        edgesSemantic = [edge.split("(")[0].strip() for edge in edges]
        neg_count = sum(1 for token in doc if token.lemma_ in NEG_Lemmas)
        is_neg = (neg_count % 2 == 1)
        suffix = "NEG" if is_neg else "POS"

        # Filter out negation tokens
        valid_tokens = [t for t in doc if t.lemma_ not in NEG_Lemmas]

        advs = [t.lemma_ for t in valid_tokens if t.pos_ == "ADV"]
        adjs = [t.lemma_ for t in valid_tokens if t.pos_ == "ADJ"]
        verbs = [t.lemma_ for t in valid_tokens if t.pos_ == "VERB"]
        nouns = [t.lemma_ for t in valid_tokens if t.pos_ == "NOUN"]


        if NN=='only':
            # Get all combinations of size 2
            print('---- only NN non semantic edges added ----')
            all_pairs = list(combinations(nouns, 2))
            for nn in all_pairs:
                if f"{nn[0]}-{nn[1]}" not in edgesSemantic:
                    edges.add(f"{nn[0]}-{nn[1]} (NOUN-NOUN {suffix} NonSemantic)")
        elif NN =='notInclude':
            print('---- no NN but AAVN non semantic edges added ----')
            # ADV-ADJ
            for adv in advs:
                for adj in adjs:
                    if f"{adv}-{adj}" not in edgesSemantic:
                        edges.add(f"{adv}-{adj} (ADV-ADJ {suffix} NonSemantic)")

            # ADV-VERB
            for adv in advs:
                for verb in verbs:
                    if f"{adv}-{verb}" not in edgesSemantic:
                        edges.add(f"{adv}-{verb} (ADV-VERB {suffix} NonSemantic)")

            # ADJ-NOUN
            for adj in adjs:
                for noun in nouns:
                    if f"{adj}-{noun}" not in edgesSemantic:
                        edges.add(f"{adj}-{noun} (ADJ-NOUN {suffix} NonSemantic)")

            # VERB-NOUN
            for verb in verbs:
                for noun in nouns:
                    if f"{verb}-{noun}" not in edgesSemantic:
                        edges.add(f"{verb}-{noun} (VERB-NOUN {suffix} NonSemantic)")
        elif NN =='include':
            print('---- all NN and AAVN non semantic edges added ----')
                        # ADV-ADJ
            for adv in advs:
                for adj in adjs:
                    if f"{adv}-{adj}" not in edgesSemantic:
                         edges.add(f"{adv}-{adj} (ADV-ADJ {suffix} NonSemantic)")

            # ADV-VERB
            for adv in advs:
                for verb in verbs:
                    if f"{adv}-{verb}" not in edgesSemantic:
                        edges.add(f"{adv}-{verb} (ADV-VERB {suffix} NonSemantic)")

            # ADJ-NOUN
            for adj in adjs:
                for noun in nouns:
                    if f"{adj}-{noun}" not in edgesSemantic:
                        edges.add(f"{adj}-{noun} (ADJ-NOUN {suffix} NonSemantic)")

            # VERB-NOUN
            for verb in verbs:
                for noun in nouns:
                    if f"{verb}-{noun}" not in edgesSemantic:
                        edges.add(f"{verb}-{noun} (VERB-NOUN {suffix} NonSemantic)")
                    
            all_pairs = list(combinations(nouns, 2))
            for nn in all_pairs:
                if f"{nn[0]}-{nn[1]}" not in edgesSemantic:
                    edges.add(f"{nn[0]}-{nn[1]} (NOUN-NOUN {suffix} NonSemantic)")

    return edges



def renameAAVN(node1,pospe1):
    """some words can be both noun,verb or adj and adv, need to specify them such as LOVE, light 

    Args:
        node1 (_type_): node lable
        pospe1 (_type_): node part of speech

    Returns:
        _type_: _description_
    """
    node1 = node1.strip()
    if pospe1 == 'ADJ':
        node1b = node1+'_2adj'
    elif pospe1 == 'ADV':
        node1b = node1 +'_2adv'
    elif pospe1 == 'VERB':
        node1b = node1 +'_2verb'
    elif pospe1 == 'NOUN':
        #print("renameNoun", node1)
        node1b = node1 +'_2noun'
    return node1b
        
renameAAVN('love','VERB')      



sia = SentimentIntensityAnalyzer()
def edges2DF(edges,sentiScore = True):
    node1s_rn = []
    node2s_rn = []
    node1s = []
    node2s = []
    weights = []
    pospe1s = []
    pospe2s = []
    semanORnots = []
    sentis = []
    
    for edge in edges:
        #print('edge',edge)
        #text_to_split = "karelian-nothing (ADJ-NOUN POS)"
        split_pattern = r"\(|\)"
        split_result = re.split(split_pattern, edge)
        #print(split_result)
        
        nodes = split_result[0].strip().rsplit('-', 1)   # "Onze-Lieve-Vrouwekerk-be" to parts[0] -> "Onze-Lieve-Vrouwekerk"  parts[1] -> "be"
        #print(nodes)
        node1 = nodes[0]
        node2 = nodes[1]
        pospos = split_result[1].strip().split(" ")
        pospes = pospos[0].strip().split("-")
        #print(pospes)
        pospe1 = pospes[0]
        pospe2 = pospes[1]
        #print(pospes)
        weight0 = pospos[1]
        if weight0 =='POS':
            weight = 1
        elif 'nothing' in nodes or 'nobody' in nodes:
            weight = 1
        else:
            weight = -1
        weights.append(weight)
        if sentiScore:
            senti = sia.polarity_scores(f"{node1} {node2}")['compound']
            sentis.append(senti*weight)
        
        
        if len(pospos)>2:
        
            semanORnot = 'non_semantic'
        else:
            semanORnot = 'semantic'

        node1_rn = renameAAVN(node1,pospe1)
        node2_rn = renameAAVN(node2,pospe2)
        node1s_rn.append(node1_rn)
        node2s_rn.append(node2_rn)
            
        
        #print(node1,node2,pospe1, pospe2, semanORnot)

        node1s.append(node1)
        node2s.append(node2)
        pospe1s.append(pospe1)
        pospe2s.append(pospe2)
        semanORnots.append(semanORnot)
    if sentiScore:
        edgesDF = pd.DataFrame({'node1':node1s_rn,
                        'node2':node2s_rn,
                        'node1a':node1s,
                        'node2a':node2s,
                        
                        'weight':weights,
                        'pospe1':pospe1s,
                        'pospe2':pospe2s,
                        'semanORnot':semanORnots,
                        'sentiment':sentis})
    else:   
        edgesDF = pd.DataFrame({'node1':node1s_rn,
                                'node2':node2s_rn,
                                'node1a':node1s,
                                'node2a':node2s,
                                'weight':weights,
                                'pospe1':pospe1s,
                                'pospe2':pospe2s,
                                'semanORnot':semanORnots})
    return edgesDF
        





#weighted_edges = topicNOUN.noun_edges.tolist()

def preVisnet(weighted_edges, colorNOUN = 'skyblue', shapeNOUN= 'box',
             colorADJ = 'gold', shapeADJ = 'triangle',
             colorVERB = 'pink', shapeVERB = 'square',
             colorADV ='brown', shapeADV = 'star',
             zeroWeightC = 'black',posWeightC ='green',negWeightC ='red',):
    """add sentiment and prepare the visual of aavn weighted edges of topic dataframe e.g. topicNOUN, topicCOMM
    Args:
        weighted_edges (_type_): aavn edges 
        colorNOUN (str, optional): _description_. Defaults to 'skyblue'.
        shapeNOUN (str, optional): _description_. Defaults to 'box'.
        colorADJ (str, optional): _description_. Defaults to 'gold'.
        shapeADJ (str, optional): _description_. Defaults to 'triangle'.
        colorVERB (str, optional): _description_. Defaults to 'pink'.
        shapeVERB (str, optional): _description_. Defaults to 'square'.
        colorADV (str, optional): _description_. Defaults to 'brown'.
        shapeADV (str, optional): _description_. Defaults to 'star'.
        zeroWeightC (str, optional): _description_. Defaults to 'black'.
        posWeightC (str, optional): _description_. Defaults to 'green'.
        negWeightC (str, optional): _description_. Defaults to 'red'.

    Returns:
        _type_: _description_
    """
    
    G = nx.Graph() 
    
    if isinstance(weighted_edges,str):
        weighted_edges1 = ast.literal_eval(weighted_edges)
    else:
        weighted_edges1 = weighted_edges
        
    

    G.add_weighted_edges_from(weighted_edges1)
  
        

    # Node Degrees
    nodeDegree = dict(G.degree(weight=True)) # type: ignore
    nodeDegreeDF = pd.DataFrame({'node': list(nodeDegree.keys()), 'nodeDegree': list(nodeDegree.values())}) 
    nodeDegreeDF = nodeDegreeDF.sort_values(by='nodeDegree', ascending=False)



    # --- 6. Visualization Data ---
    visNodes = []
    for node, degree in zip(nodeDegreeDF.iloc[:, 0], nodeDegreeDF.iloc[:, 1]):
        
        if "_2noun" in node:
            
            color = colorNOUN; shape= shapeNOUN; title= node
        elif "_2adj" in node:
            color = colorADJ; shape = shapeADJ; title = node
        elif "_2verb" in node:
            color = colorVERB; shape = shapeVERB; title = node
        elif "_2adv" in node:
            color =colorADV; shape = shapeADV; title = node 
        else:
            color = 'black'; shape = 'dot'; title = 'non AAVN'
        
        visNode = {"id": node, "label": node.split("_2")[0], "size": degree, "color": color, "shape": shape, "title": f"{title}-{degree}"}
        visNodes.append(visNode)
        
    visEdges = []

    # Calculate global sentiment for coloring
    #global_sentiment = edgesDF.groupby(['node1', 'node2']).agg(sentiment=('sentiment', lambda x: x.mode().iat[0])).reset_index()
    #edges_viz = pd.merge(edgesDF_global, global_sentiment, on=['node1','node2'])

    for edge in  weighted_edges1:
      
        node1  = edge[0]
        node2 = edge[1]
        weight = edge[2]
        #print(node1,node2,weight)
        senti = sia.polarity_scores(f"{node1.split("_2")[0]} {node2.split("_2")[0]}")['compound']
        #print('edge, senti',edge, senti)
        if weight<0:
            sentiment = senti*-1
        else:
            sentiment = senti 
        if weight == 0:
            color = zeroWeightC
        elif weight > 0:
            color =posWeightC
        else:
            color = negWeightC
            
        visEdge = {"from": node1, "to": node2, "width": abs(weight), "color": {"color": color}, "arrows": "to", "title": f"weight-sentiment: {weight}-{sentiment}"}
        visEdges.append(visEdge)
        
    return visNodes, visEdges,nodeDegreeDF 




if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm") 
    text = "Kuopio is known for its kalakukko (fish pie)"
    edges = semanticEdges(nlp(text))
    print(f"text: {text}")
    print('---edges---')
    for edge in sorted(edges):
        
        print(edge)
    
