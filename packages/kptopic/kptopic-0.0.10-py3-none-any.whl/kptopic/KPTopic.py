from avnBase.avn_base import  spellCorrect, preVisnet, spaceOut,merge_emoji_tokens, cleanDetNum,cleanText,semanticEdges,edges2DF, docRetoken,MaverickCoref,convert_specific_unicode,uniSimilarNodesDF
from visBase.vis_base import visnet
import networkx as nx
import spacy
import pandas as pd 
from tqdm import tqdm
from datetime import datetime
import time
from typing import List, Optional,Dict

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("custom_sentencizer", before="parser") 



import sys

def print_progress(current, total, bar_length=20,printText ='Generating AAVN Edges'):
    percent = current / total * 100
    filled_length = int(bar_length * current / total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write(
        f'\r{printText}: |{bar}| {percent:6.2f}% Completed. '
    )
    sys.stdout.flush()






from spacy.tokenizer import Tokenizer
# Ensure the spaCy tokenizer doesn't split the emoji components
def custom_tokenizer(nlp):
    # This ensures that ZWJ sequences are kept together as one token
    return Tokenizer(nlp.vocab, rules=nlp.Defaults.tokenizer_exceptions)


def semanticX(data:pd.DataFrame | List[str], text_column='text',nlpModel=None, spellCheck = True,nonCheckWords:List[str] = ['Atsaniik'], coreference = False,corefPath = None,
              det=None, valid_particles =None, number_words=True, clean_emoji=False, 
              heavy_number = False,verbPhrase = False, extraClean = False,
              reADJ:List[str]=['meilide'], reADV:List[str]=['piaoliangdi'],reVERB:List[str]=['caiquxingdong'], 
              reNOUN:List[str]=['Natural Language Processing'],reENT = True,hyphenated = True,
              NEG_Lemmas:set = {"no", "not", "n't", "never", "none", "nothing", "nobody", "neither","nor"},
              nonSemantic = 0, NN = 'notInclude',
              sentiScore = True, 
              UNICODE_TO_ASCII:dict =  {'’': "'", '‘': "'", '“': '"',  '”': '"',  '–': '-', '—': '-',  '…': '...',},
              copulaBridge = True,
              verbose = True
              ):
    """turn text to AAVN semantic edges 

    Args:
        data (list or dataframe): list of text or dataframe has text column 
        text_column (str, optional): text column name. Defaults to 'text'.
        nlpModel(spacy language model pipline): Defauts to  nlp = spacy.load("en_core_web_sm")
        spellCheck(bool): corret the words spellings , Defuats to True.
        nonCheckWords (list): the words are not to be corrected, 1 word by 1 and case sensative such as Peng Yang should be ['Peng','Yang'] not ['peng','yang'] or ['Peng Yang']
        coreference (bool, optional): if coreferee text. Defaults to False.  # pip install torch transformers hydra-core pytorch-lightning, pip install --no-deps git+https://github.com/Atsaniik/maverick-coref.git
        corefPath (_type_, optional): the model path. Defaults to None.    # hf download sapienzanlp/maverick-mes-preco --local-dir ./maverick-mes-preco # hf download sapienzanlp/maverick-mes-ontonotes --local-dir ./maverick-ontonotes
        det (list, optional):det. if None, Defaults to ["a", "an", "the"].
        valid_particles(set): if None, valid_particles = {
                            "up", "off", "away", "out", "over", "back",
                            "down", "on", "in", "with", "into", "by", "after"
                                                                            }
        number_words (bool, optional): remove numbers but keep such as G-8, Covi-19. Defaults to True.
        clean_emoji (bool, optional): remove emoji. Defaults to False.
        heavy_number (bool, optional): remove all numbers. Defaults to False.
        verbPhrase (bool, optional): if true, then 'take it off' beacome 'take off it' in the new text. Defaults to False.
        extraClean (bool, optional): Remove ( xxx ) parentheses and everything inside them. Defaults to False.
        reADJ (list, optional): retokenzie specific adjective. Defaults to ['meilide']. case-sensitive 
        reADV (list, optional): retokenzie specific adverb. Defaults to ['piaoliang'].  case-sensitive 
        reVERB (list, optional): retokenzie specific verb. Defaults to ['caiquxingdong']. case-sensitive 
        reNOUN (list, optional): retokenzie specific noun. Defaults to ['Natural Language Processing']. case-sensitive 
        reENT (bool, optional): retokenzie specific enity words. Defaults to True.
        hyphenated (bool, optional): retokenzie specific hyphenated words. Defaults to True.
        NEG_Lemmas (dict, optional): negative words to detect the edge weight postive or negative. Defaults to {"no", "not", "n't", "never", "none", "nothing", "nobody", "neither","nor"}.
        nonSemantic(digit,optional): if nonSemantic = 1, then generate avn edges of non semantic text adj-adv, adj-noun, adv-verb, verb-noun 
        NN: (vaule: [inlcude, only , notInclude] ) if only then only noun-noun type nonSemantic edges, if notInclude then A-A-V, if include the all A-A-V-N edge
        sentiScore (bool, optional): add sentiment score of edge. Defaults to True.
        reNameNode (bool, optional): add A-A-V-N label to each word ends. Defaults to True.
        UNICODE_TO_ASCII (dict, optional): change the unicode to ascii of English puncs. Defaults to {'’': "'", '‘': "'", '“': '"',  '”': '"',  '–': '-', '—': '-',  '…': '...',}.
        copulaBridge (bool): Finland is beautiful add one extra edge Finland-beautiful connected by copula Be , otherwise only Finland-be, be-beautiful 
        verbose(bool,optional): print the raw text and processed one 
    Returns:
        dataframes: edgesDF,eueDF(email, url,emoji of each row or item of original data)
    """
    if nlpModel:
        nlp = nlpModel
    else:
        nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("custom_sentencizer", before="parser") 
    
    # --- 1. Normalize Input to DataFrame ---
    if isinstance(data, list):
        # Convert list to DataFrame, no metadata
        df = pd.DataFrame({text_column: data})
        metadata_cols = [] 
    elif isinstance(data, pd.DataFrame):
        df = data.copy() # Work on a copy
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in the DataFrame.")
        # Identify metadata columns (everything except the text)
        metadata_cols = [col for col in df.columns if col != text_column]
    else:
        raise TypeError("Input 'data' must be either a list of strings or a pandas DataFrame.")

    # --- 2. Process Rows ---
    df_list = [] # To collect small DataFrames (one per row)
    
    
    emails = [] 
    urls = []
    emojis = []
    verbphrases = []
    total_rows = len(df)
    for i,(index, row) in enumerate(df.iterrows(),start=1):
        print_progress(i, total_rows)
        raw_text = row[text_column]
        if verbose:
            print(f'raw_text ({i})  {raw_text}')
        raw_text = spaceOut(raw_text)
        #print('space out text', raw_text)
        # Safety check: ensure text is a string
        if not isinstance(raw_text, str):
            continue
        raw_text = convert_specific_unicode(raw_text,UNICODE_TO_ASCII=UNICODE_TO_ASCII )
        # A. Preprocessing
        # Uses 'raw_text' from the row, NOT 'texts' from the old list

        if spellCheck:
            raw_text = spellCorrect(raw_text, nonCheckWords=nonCheckWords)
            #print(f'correct text ({i})  ',raw_text)
        else:
            pass
        if coreference:
            raw_text = MaverickCoref.resolve(raw_text,device=None, path=corefPath)
        else:
            pass
        
        #text = cleanDetNum(text, nlp)
        final_text, unique_Verbphrases, email, url, emoji = cleanText(raw_text, nlp, det=det, valid_particles =valid_particles,
                                                                         number_words=number_words, clean_emoji=clean_emoji, heavy_number = heavy_number,
                                                                         verbPhrase = verbPhrase, extraClean = extraClean,
                                                                         reADJ=reADJ, reADV=reADV,
                                                                         reVERB=reVERB, reNOUN=reNOUN,
                                                                         reENT = reENT,hyphenated = hyphenated)
        #print('final_text',final_text)
        if verbose:
            print(f'processed_text ({i})  {final_text}')
        emails.append(email)
        urls.append(url)
        emojis.append(emoji)
        verbphrases.append(unique_Verbphrases)
        # B. Tokenization
        
        doc = docRetoken(final_text, nlp,reADJ=reADJ, reADV=reADV,
                         reVERB=reVERB + unique_Verbphrases, reNOUN=reNOUN,
                         reENT = reENT,hyphenated = hyphenated)
        #print('doc_text',doc.text)
        doc = merge_emoji_tokens(doc)
        # C. Edge Generation
        current_row_edges = []
        for sent in doc.sents:
            #print('sent.text',sent.text)
            #sent = nlp(sent.text)
            # semanticEdges returns a SET of strings like {'word-word (POS)', ...}
            edges_set = semanticEdges(sent, NEG_Lemmas = NEG_Lemmas,
                            nonSemantic = nonSemantic, NN = NN,copulaBridge=copulaBridge)
            #print('edges_set',edges_set)
            current_row_edges.extend(list(edges_set))
        
        # Only proceed if edges were found in this row
        if current_row_edges:
            # D. Convert strings to a DataFrame using your existing helper
            temp_df = edges2DF(current_row_edges,sentiScore = sentiScore)
            
            # E. Add Metadata (if any exist)
            for meta_col in metadata_cols:
                temp_df[meta_col] = row[meta_col]
            
            df_list.append(temp_df)

    # --- 3. Combine Results ---
    if df_list:
        edgesDF = pd.concat(df_list, ignore_index=True)
        eueDF = pd.DataFrame({'emials':emails,'urls':urls,'emojis':emojis,'verbphrases':verbphrases})
    else:
        # Return empty structures if no edges found
        return pd.DataFrame(),pd.DataFrame()
    return edgesDF,eueDF




def nounKPT(G,max_topic):
    """ topic generated by the high degree of noun and its edges 
    Args:
        G (_type_): _description_
        max_topic (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
    # Node Degrees
    nodeDegree = dict(G.degree(weight=True))
    nodeDegreeDF = pd.DataFrame({'node': list(nodeDegree.keys()), 'nodeDegree': list(nodeDegree.values())}) 
    nodeDegreeDF = nodeDegreeDF.sort_values(by='nodeDegree', key=lambda x: x.abs(), ascending=False)

    # Extract Topics
    central_nouns = []
    associate_words = []
    noun_edges = []
    i = 0
    
    for node in nodeDegreeDF.node:
        if isinstance(node,str):
            if '_2noun' in node:
                i += 1
                if i <max_topic:
                    central_nouns.append(node)
                    associate_words.append(G.adj[node])
                    #print('G.adj[node]',G.adj[node])
                    noun_edges0 = []
                    for neighbor, attr in G.adj[node].items():
                        weight = attr['weight']
                        noun_edges0.append((node,neighbor,weight))
                        #print("node:", neighbor, "weight:", weight)
                    noun_edges.append(noun_edges0)

    topicDF = pd.DataFrame({'central noun': central_nouns, 'associate_words': associate_words,'noun_edges':noun_edges})
    return topicDF


import networkx as nx
import pandas as pd

def communKPT(G, min_weight=1, k_clique=3, louvain_resolution = 1, method='louvain', topicN=True, maxNOUNtopic=5):
    """
    Generates communities using either K-clique percolation or Louvain detection.
    Extracts edges preserving the original source-target order from G.
    
    Parameters:
    - method: 'k-clique' or 'louvain'
    """
    # 1. Filter edges based on weight
    strong_edges = [
        (u, v) for u, v, d in G.edges(data=True) 
        if abs(d.get('weight', 1)) >= min_weight
    ]
     
    G2 = G.to_undirected()
    # Create the filtered graph for community detection
    G_filtered = G2.edge_subgraph(strong_edges).copy()
    
    # 2. Find Communities based on selected method
    try:
        if method == 'louvain':
            # Louvain algorithm (resolves to partitions of the graph)
            communities = nx.community.louvain_communities(G_filtered, weight='weight',resolution = louvain_resolution)
        else:
            # Original K-Clique algorithm
            communities = nx.community.k_clique_communities(G_filtered, k=k_clique)
        
        communities = list(communities)
        source_G = G_filtered
        
    except Exception as e:
        # Fallback to the original graph if filtering causes issues or k-clique fails
        if method == 'louvain':
            communities = list(nx.community.louvain_communities(G, weight='weight',resolution= louvain_resolution))
        else:
            communities = list(nx.community.k_clique_communities(G, k=k_clique))
        source_G = G

    # Sort communities by size (largest first)
    communities = sorted(communities, key=len, reverse=True)

    # 3. Handle Topic Generation
    if topicN:
        # Assuming nounKPT is defined elsewhere in your workspace
        topicDFnoun = nounKPT(source_G, max_topic=maxNOUNtopic)
    else:
        topicDFnoun = pd.DataFrame()

    community_edges = []
    community_is = []
    community_nodes = []

    # 4. Extract Data preserving Edge Orientation
    for i, nodes in enumerate(communities):
        nodes_set = set(nodes)
        edges_with_data = []
        
        # Iterate over ORIGINAL G edges to maintain 'starting -> targeting' order
        for u, v, data in G.edges(data=True):
            if u in nodes_set and v in nodes_set:
                weight = data.get('weight', None)
                if weight is not None:
                    edges_with_data.append((u, v, weight))
                else:
                    edges_with_data.append((u, v))
                    
        community_edges.append(edges_with_data)
        community_is.append(i)
        community_nodes.append(list(nodes))
        
    communityDF = pd.DataFrame({
        'community_no': community_is, 
        'community_nodes': community_nodes,
        'community_edges': community_edges
    })
    
    return communityDF, topicDFnoun


def communKPT_old(G, min_weight=1, k_clique=3, topicN=True, maxNOUNtopic=5):
    """
    Generates communities using k-clique percolation and extracts edges 
    preserving the original source-target order from G.
    """
    # 1. Filter edges based on weight
    # We use abs(d.get('weight', 0)) to handle cases where 'weight' might be missing
    strong_edges = [
        (u, v) for u, v, d in G.edges(data=True) 
        if abs(d.get('weight', 1)) >= min_weight
    ]
     
    G2 = G.to_undirected()
    # Create the filtered graph for community detection
    G_filtered = G2.edge_subgraph(strong_edges).copy()
    
    # 2. Find Communities
    try:
        communities = list(nx.community.k_clique_communities(G_filtered, k=k_clique))
        #communities = list(nx.community.louvain_communities(G_filtered))
        source_G = G_filtered
    except Exception as e:
        #print(f"K-clique failed on filtered graph: {e}. Falling back to original G.")
        communities = list(nx.community.k_clique_communities(G, k=k_clique))
        source_G = G
    communities = sorted(list(communities), key=len, reverse=True)  # add 05.Jan.2026
    # 3. Handle Topic Generation
    if topicN:
        # Assuming nounKPT is defined elsewhere
        topicDFnoun = nounKPT(source_G, max_topic=maxNOUNtopic)
    else:
        topicDFnoun = pd.DataFrame()

    #print(f"Found {len(communities)} communities.\n")

    community_edges = []
    community_is = []
    community_nodes = []

    # 4. Extract Data preserving Edge Orientation
    for i, nodes in enumerate(communities):
        nodes_set = set(nodes)
        edges_with_data = []
        
        # We iterate over the ORIGINAL G edges to maintain 'starting -> targeting' order
        # and only keep those where both nodes are in the current community
        for u, v, data in G.edges(data=True):
            #print('G2-u-v',u,v)
            if u in nodes_set and v in nodes_set:
                weight = data.get('weight', None)
                if weight is not None:
                    edges_with_data.append((u, v, weight))
                else:
                    edges_with_data.append((u, v))
                    
        community_edges.append(edges_with_data)
        community_is.append(i)
        community_nodes.append(list(nodes))
        
    communityDF = pd.DataFrame({
        'community_no': community_is, 
        'community_nodes': community_nodes,
        'community_edges': community_edges
    })
    
    return communityDF, topicDFnoun


emoji_pattern = r'[\U00010000-\U0010ffff]'

def has_emoji(series):
    return series.str.contains(emoji_pattern, na=False, regex=True)



def netKPT(edgesDF:pd.DataFrame,col1 = 'node1',col2 = 'node2',col1a ='node1a',col2a='node2a',
            colorNOUN = 'skyblue', shapeNOUN= 'box',
            colorADJ = 'gold', shapeADJ = 'triangle',
            colorVERB = 'pink', shapeVERB = 'square',
            colorADV ='brown', shapeADV = 'star',
            zeroWeightC = 'black',posWeightC ='green',negWeightC ='red',
            topicBYnoun = True, maxNOUNtopic = 5,
            minWeightTopic=1,kCliqueCOMMtopic = 2, 
            lowerText = True, nodeMinLen =3, keep_emoji = True,
            removeNodes:List[str] = ['when','how','why','what', 'who', 'around', 'also','that','this','these','those','you','mine','ours','their','her','his','round','go','be','have','is','are','was','were','get'],
            unifySimliarNodes = True, similarPOS ='NOUN',minSimilar = 0.99, manual_simPair:Dict[str, str] = {'suomi_2noun': 'finland_2noun'},
            visualizeNET = False,
            visNoPOS = True,
            vis_network_title = 'Atsaniik',
            vis_description_df: Optional[pd.DataFrame] = None,
            vis_description_title = "Introduce your network",
            vis_writeHTML = "network_visualization.html",
            vis_browserView= False,
            vis_min_default_node_size= -1000,
            vis_min_default_edge_width = -1000,
            vis_maximum_display = 100):
    """semantic edges to be cleaned and weighted for creating topics 

    Args:
        edgesDF (dataframe): semantic edges dataframe 
        col1 (str, 'good_2adj'): full starting node column name. Defauts to 'node1'
        col2 (str,'food_2noun'): full targeting node column name. Defauts to 'node2
        col1a (str,'good'): starting node column name. Defauts to 'node1a'
        col2a (str,'food'): targeting node column name. Defauts to 'node2a'
        colorNOUN (str, optional): _description_. Defaults to 'blue'.
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
        topicBYnoun(bool): if true also generate topic by Noun by centrality degree 
        maxNOUNtopic (int, optional): _description_. Defaults to 5.
        minWeightTopic (int, optional): set minimal weight absoluate value. Defaults to 1. greater than 1 or less than 1. Defaults to 1.
        kCliqueCOMMtopic (int, optional): comunnity clique number. Defaults to 3. Defaults to 3.
        lowerText (bool, clean edges): lower all nodes . Defaults to True.
        nodeMinLen (int, clean edges):  node text minimun length. Defaults to 3. 
        keep_emoji(bool,clean edges): if keep or remove the emoji edges 
        removeNodes (list, clean edges): remove edges that have the specific nodes. Defaults to ['when','how','why','what','that','this','these','those','you','mine','ours','their','her','his'].
        unifySimliarNodes ( bool ): if unify the simliar nodes in the edges, Defualts to True , only take noun and verb. 
        similarPOS (str, unify nodes by pos): Defautls to 'NOUN',
        minSimilar (float, unify nodes minimal similarity): Defauts to 0.91 # food drink 0.909 
        manual_simPair(list of dict): {'helsinki_2noun': 'finland_2noun'}
        visualizeNET (bool): if visualize the semantic network
        visNoPOS(bool): if true, then 'good_2adj' to 'good' in vis
        network_title (str): Defauts to 'Atsaniik'
        vis_description_df (str): Defausts to None
        vis_description_title (str): Defaults to "Introduce your network"
        vis_writeHTML: str = "network_visualization.html"
        vis_browserView: bool = False,
        vis_min_default_node_size: int = 0
        vis_min_default_edge_width: int = 0
        vis_maximum_display: int = 100
    Returns:
        topicDFnoun: topic by noun by centrality degree; 
        topicDFcomm: topic by community;
        edgesDF1: clean edgesDF by lowerText, nodeMinLen, and removeModes;
        edgesDF_vis: edgesDF weighted by edge groups for visualization;
        visNodes, visEdges : prepare for visnet visualization of the whole network;
    """
    
    pbar = tqdm(total=6, desc="Initializing Pipeline")
    # Combine: Remove if either column meets the criteria
    if lowerText:
        edgesDF = edgesDF.map(lambda x: x.lower() if isinstance(x, str) else x)
     
       
    if keep_emoji:

        mask1 = (
            (edgesDF[col1a].str.len() < nodeMinLen) & ~has_emoji(edgesDF[col1a])
        ) | (edgesDF[col1a].isin(removeNodes))

        mask2 = (
            (edgesDF[col2a].str.len() < nodeMinLen) & ~has_emoji(edgesDF[col2a])
        ) | (edgesDF[col2a].isin(removeNodes))
        
        edgesDF1 = edgesDF[~(mask1 | mask2)]
        
    else:
        
       mask1 = (edgesDF[col1a].str.len() < nodeMinLen) | (edgesDF[col1a].isin(removeNodes))
       mask2 = (edgesDF[col2a].str.len() < nodeMinLen) | (edgesDF[col2a].isin(removeNodes))
       edgesDF1 = edgesDF[~(mask1 | mask2)]    
       
    pbar.update(1)
    pbar.set_description("Grouping and aggregating edges")   
    
    if unifySimliarNodes:
        # col1 ='node1',col2='node2', similarPOS ='NOUN',minSimilar = 0.91
        edgesDF1,similarNodesDF = uniSimilarNodesDF(edgesDF1, col1 =col1,col2= col2, pos =similarPOS,minSimilar =minSimilar,manual_pairs=manual_simPair)
    
        edgesDF_global = edgesDF1.groupby([col1, col2]).agg(weight=('weight', 'sum')).reset_index()
    else:
        edgesDF_global = edgesDF1.groupby([col1, col2]).agg(weight=('weight', 'sum')).reset_index()
    
    
    
    pbar.update(1)
    pbar.set_description("Constructing NetworkX Graph")
    
    
    G = nx.DiGraph() 
    weighted_edge_list = list(zip(edgesDF_global[col1], edgesDF_global[col2], edgesDF_global['weight']))
    G.add_weighted_edges_from(weighted_edge_list)
    
    # Node Degrees
    nodeDegree = dict(G.degree(weight="weight")) # type: ignore
    nodeDegreeNode0 = list(nodeDegree.keys())
    nodeDegreeNode1a = [x.split('_2')[0] for x in nodeDegreeNode0]
    nodeDegreeNode1b = [x.split('_2')[1] for x in nodeDegreeNode0]
    
    nodeDegreeDF = pd.DataFrame({'node': nodeDegreeNode0, 'node1': nodeDegreeNode1a, 'nodeDegree': list(nodeDegree.values()),'pos': nodeDegreeNode1b}) 
    nodeDegreeDF = nodeDegreeDF.sort_values(by='nodeDegree', ascending=False)
    
    #for u, v, data in G.edges(data=True):
        #print('G1-u-v',u,v)
    pbar.update(1)
    pbar.set_description("Processing Node attributes")

    # --- 6. Visualization Data ---
    visNodes = []
    for node, degree in zip(nodeDegreeDF.iloc[:, 0], nodeDegreeDF.iloc[:, 2]):
        
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
        if visNoPOS:
            visNode = {"id": node, "label": node.split("_2")[0], "size": degree, "color": color, "shape": shape, "title": f"{title}-{degree}"}
        else:
            visNode = {"id": node, "label": node, "size": degree, "color": color, "shape": shape, "title": f"{title}-{degree}"}
        visNodes.append(visNode)
    pbar.update(1)
    pbar.set_description("Processing Edge attributes")
        
    visEdges = []
  
    # Calculate global sentiment for coloring
    global_sentiment = edgesDF1.groupby([col1, col2]).agg(sentiment=('sentiment', lambda x: x.mode().iat[0])).reset_index()
    edges_viz = pd.merge(edgesDF_global, global_sentiment, on=[col1,col2])

    for node1, node2, weight, sentiment in zip(edges_viz[col1], edges_viz[col2], edges_viz['weight'], edges_viz['sentiment']):
        if weight == 0:
            color = zeroWeightC
        elif weight > 0:
            color =posWeightC
        else:
            color = negWeightC
            
        visEdge = {"from": node1, "to": node2, "width": abs(weight), "color": {"color": color}, "arrows": "to", "title": f"weight-sentiment: {weight}-{sentiment}"}
        visEdges.append(visEdge)
    
    pbar.update(1)
    pbar.set_description("Generating topics") 
        
    #topicDFnoun = nounKPT(G,max_topic=maxNOUNtopic) 
    topicDFcomm,topicDFnoun = communKPT(G, min_weight=minWeightTopic, k_clique = kCliqueCOMMtopic,topicN = topicBYnoun , maxNOUNtopic=maxNOUNtopic)
    if visualizeNET:
        sentiments2 = []
        for edge in visEdges:
            sentiments2.append (float(edge['title'].split('-')[-1]))
            
        visDF = pd.DataFrame({
                    "Name": ["Ave Sentiment"],
                    "Description": [round(sum(sentiments2)/len(sentiments2),2)]
                })
        if vis_description_df is not None:
            visDF2 = vis_description_df
        else:
             visDF2 = visDF
        
        visnet(visNodes,visEdges,
        network_title = vis_network_title,
        description_df = visDF2,
        description_title = vis_description_title,
        writeHTML = vis_writeHTML,
        browserView= vis_browserView,
        min_default_node_size= vis_min_default_node_size,
        min_default_edge_width = vis_min_default_edge_width,
        maximum_display = vis_maximum_display) 
    pbar.update(1)
    pbar.close() # Clean up the bar from the terminal
    return topicDFnoun, topicDFcomm,edgesDF1,edgesDF_global, edges_viz,nodeDegreeDF, visNodes, visEdges,similarNodesDF
    
def visTopic(edges, vis_network_title = 'Atsaniik',
            vis_description_df = None,
            vis_description_title = "Introduce your network",
            vis_writeHTML = None,
            vis_browserView= False,
            vis_min_default_node_size= 0,
            vis_min_default_edge_width = 0,
            vis_maximum_display = 100):
    """visualize the topic based on the aavn weighted edges + generatation of sentiment of edge

    Args:
        edges (list): weighted edges 
        vis_network_title (str, optional): _description_. Defaults to 'Atsaniik'.
        vis_description_df (_type_, optional): _description_. Defaults to None.
        vis_description_title (str, optional): _description_. Defaults to "Introduce your network".
        vis_writeHTML (_type_, optional): _description_. Defaults to None.
        vis_browserView (bool, optional): _description_. Defaults to False.
        vis_min_default_node_size (int, optional): _description_. Defaults to 0.
        vis_min_default_edge_width (int, optional): _description_. Defaults to 0.
        vis_maximum_display (int, optional): _description_. Defaults to 100.

    Returns:
        visnet nodes,visnet edges and nodedegree: visNodesTopic, visEdgesTopic,nodeDegreeDF
    """
    if len(edges) < 1:
        raise ValueError("topic edges must have at least 1 edge")
    visNodesTopic, visEdgesTopic,nodeDegreeDF =preVisnet(edges)
    sentiments = []
    for edge in visEdgesTopic:
        sentiments.append (float(edge['title'].split('-')[-1]))
    
    visDF = pd.DataFrame({
                "Name": ["Nodes amount", "Edges amount","Ave Sentiment"],
                "Description": [len((visNodesTopic)), len((visEdgesTopic)),round(sum(sentiments)/len(sentiments),2)]
            })
    
    #visADD = rf"C:\PhDDocs\pythonPhD\myPYPI\kptopic2\topic_visual/topic_{topic}.html"

    if vis_description_df:
        visDF2 = vis_description_df
    else:
        visDF2 = visDF
    if vis_writeHTML:
        vis_writeHTML = vis_writeHTML
    else:
        time.sleep(1)
        now1 = datetime.now()
        now1 = now1.strftime("%Y_%m_%d_%H_%M_%S")
        vis_writeHTML = f"topic_{now1}.html"
    
    visnet(visNodesTopic,visEdgesTopic,
    network_title = vis_network_title,
    description_df = visDF2,
    description_title = vis_description_title,
    writeHTML = vis_writeHTML,
    browserView= vis_browserView,
    min_default_node_size= vis_min_default_node_size,
    min_default_edge_width = vis_min_default_edge_width,
    maximum_display = vis_maximum_display) 
    
    return visNodesTopic, visEdgesTopic,nodeDegreeDF



import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def visDIST(data,color='skyblue',edgecolor='black', alpha = 0.7, bins = 30, title = 'sentiment distribution', figsize = (10,6),saveADD = 'distribution_plot.png'):
    """visulize the distribtion of list of numbers 

    Args:
        data (list): a list of numbers 
        color (str, optional): _description_. Defaults to 'skyblue'.
        edgecolor (str, optional): _description_. Defaults to 'black'.
        alpha (float, optional): _description_. Defaults to 0.7.
        bins (int, optional): _description_. Defaults to 30.
        title (str, optional): _description_. Defaults to 'sentiment distribution'.
        figsize (tuple, optional): _description_. Defaults to (10,6).
        saveADD (str, optional): _description_. Defaults to 'distribution_plot.png'.
    """
    
    
    #data = edgesDF1.round(2).sentiment.tolist()

    # 2. Calculate mean and standard deviation
    mean = float(np.mean(data))
    std_dev = float(np.std(data))

    # 3. Create the plot
    plt.figure(figsize=(10, 6))
    sns.histplot(data, kde=True, color=color, edgecolor= edgecolor, alpha=alpha,bins=bins,)

    # 4. Add vertical lines for mean and standard deviation
    # Solid line for the mean
    plt.axvline(mean, color='red', linestyle='-', linewidth=2, 
                label=rf'Mean ($\mu$): {mean:.2f}')

    # Dashed lines for standard deviations
    plt.axvline(mean - std_dev, color='green', linestyle='--', linewidth=1.5, 
                label=rf'1 Std Dev ($\sigma$): {std_dev:.2f}')
    plt.axvline(mean + std_dev, color='green', linestyle='--', linewidth=1.5)

    # 5. Add labels and legend
    plt.title(title, fontsize=16)
    plt.xlabel('Value', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend()

    # 6. Save the plot
    plt.savefig(saveADD)



if __name__ == "__main__":
    
    texts = ['I love you, I would not come to finland this year😊 visit us at uef.fi ',
             'I do not love you, I can go to school now, contact us peng@uef.fi , we will have great food',
             'this is extremely good food, you must try it',
             'Finland has a lot delicious food and drinks, highly recommended',
             'I do not recommend🤷‍♂️ you eat the food',
             'Finland is beautiful country','I do not love you']
    
    edgesDF,eueDF = semanticX(texts, verbPhrase= True,coreference= False,corefPath=None,)
    topicDFnoun, topicDFcomm,edgesDF1,edgesDF_global, edges_viz,nodeDegreeDF, visNodes, visEdges,similarNodesDF = netKPT(edgesDF,colorNOUN='skyblue',kCliqueCOMMtopic=2,removeNodes = [],minSimilar=.96,visualizeNET=True)
    
  
    with pd.ExcelWriter(r"C:\PhDDocs\pythonPhD\myPYPI\kptopic2/kpt_edges.xlsx") as writer:
        topicDFnoun.to_excel(writer, sheet_name='topicNOUN',index=False)
        topicDFcomm.to_excel(writer,sheet_name='topicCOMM',index=False)
        edges_viz.to_excel(writer,sheet_name='edges_vis',index=False)
        #edgesDF_global.to_excel(writer,sheet_name='cleaned weighted',index= False)
        edgesDF1.to_excel(writer,sheet_name='cleaned edges',index= False)
        edgesDF.to_excel(writer, sheet_name='original edges', index= False)
        nodeDegreeDF.to_excel(writer,sheet_name ='node_degree')
        eueDF.to_excel(writer, sheet_name='eue', index= False)
        similarNodesDF.to_excel(writer,sheet_name='simNodes')
    # AI Prompt to generate topic:
    """You are given a central keyword and a list of related words with numerical weights representing their associations. Positive weights indicate positive associations, negative weights indicate negative associations, and zero weight indicates neutral association. Using this information, write one coherent topic sentence about the central keyword that naturally reflects both the positive and negative associations. Include the most important related words, convey the overall sentiment, and ensure the sentence reads smoothly as if written by a human."

    Example Input:
    Central word: food
    Edges: {'Finland_2noun': 1, 'delicious_2adj': 1, 'drink_2noun': 1, 'good_2adj': 1, 'lot_2noun': 1, 'have_2verb': 1, 'recommend_2verb': 0, 'eat_2verb': -1, '\u200d_2noun': -1, '♂_2noun': -1}

    Example Output (Topic Sentence):
    "In Finland, the food is generally good and delicious, with plenty of drinks available, though some dishes may not be enjoyable or suitable for everyone."""
