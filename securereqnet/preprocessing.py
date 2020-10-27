# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_preprocessing.ipynb (unless otherwise specified).

__all__ = ['__read_dataset', '__train_test_split', '__create_corpora', 'get_training_corpora', 'process_corpora',
           'vectorize_sentences']

# Cell
#danaderp May6'19
#Prediction For Main Issues Data Set
import csv
from tensorflow.keras.preprocessing import text
from nltk.corpus import gutenberg
from string import punctuation
from tensorflow.keras.preprocessing.sequence import skipgrams

# Cell
import pandas as pd
import numpy as np
import re
import nltk
import matplotlib.pyplot as plt

# Cell
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.layers import Dot, Input, Dense, Reshape, LSTM, Conv2D, Flatten, MaxPooling1D, Dropout, MaxPooling2D
from tensorflow.keras.layers import Embedding, Multiply, Subtract
from tensorflow.keras.models import Sequential, Model
from tensorflow.python.keras.layers import Lambda
from tensorflow.keras.callbacks import CSVLogger, ModelCheckpoint
from tensorflow.keras.callbacks import EarlyStopping

# Cell
# visualize model structure
#from IPython.display import SVG
#from keras.utils.vis_utils import model_to_dot
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.manifold import TSNE

# Cell
from .utils import Dynamic_Dataset, Processing_Dataset
from .utils import Embeddings

# Cell
def __read_dataset(path):
    process_unit = Processing_Dataset(path)
    ground_truth = process_unit.get_ground_truth()
    dataset = Dynamic_Dataset(ground_truth, path,False) # I'm not sure this needs to be False. RC
    return process_unit, ground_truth, dataset

# Cell
def __train_test_split(process_unit, ground_truth,isZipFile):
    test, train = process_unit.get_test_and_training(ground_truth,isZip = isZipFile)
    return test,train
#As the data is stored in a zip file isZip = True


# Cell
#Added due to a lookup error in the next cell
import nltk
nltk.download('stopwords')

# Cell
def __create_corpora(test,train):
    '''Creates the corpora for training. Returns corpora_train,corpora_test,max_len_sentences,embed_size'''
    embeddings = Embeddings()
    max_words = 5000 #<------- [Parameter]
    pre_corpora_train = [doc for doc in train if len(doc[1])< max_words]
    pre_corpora_test = [doc for doc in test if len(doc[1])< max_words]

    embed_path = '../data/word_embeddings-embed_size_100-epochs_100.csv'
    embeddings_dict = embeddings.get_embeddings_dict(embed_path)

    # .decode("utf-8") takes the doc's which are saved as byte files and converts them into strings for tokenization
    corpora_train = [embeddings.vectorize(doc[1].decode("utf-8"), embeddings_dict) for doc in pre_corpora_train]#vectorization Inputs
    corpora_test = [embeddings.vectorize(doc[1].decode("utf-8"), embeddings_dict) for doc in pre_corpora_test]#vectorization

    target_train = [[int(list(doc[0])[1]),int(list(doc[0])[3])] for doc in pre_corpora_train]#vectorization Output
    target_test = [[int(list(doc[0])[1]),int(list(doc[0])[3])]for doc in pre_corpora_test]#vectorization Output
    #target_train

    max_len_sentences_train = max([len(doc) for doc in corpora_train]) #<------- [Parameter]
    max_len_sentences_test = max([len(doc) for doc in corpora_test]) #<------- [Parameter]

    max_len_sentences = max(max_len_sentences_train,max_len_sentences_test)
    print("Max. Sentence # words:",max_len_sentences)

    min_len_sentences_train = min([len(doc) for doc in corpora_train]) #<------- [Parameter]
    min_len_sentences_test = min([len(doc) for doc in corpora_test]) #<------- [Parameter]

    min_len_sentences = max(min_len_sentences_train,min_len_sentences_test)
    print("Mix. Sentence # words:",min_len_sentences)

    embed_size = np.size(corpora_train[0][0])

    return corpora_train,corpora_test,max_len_sentences,embed_size

# Cell
def get_training_corpora(path,isZip):
    process_unit, ground_truth, dataset = __read_dataset(path)
    test, train = __train_test_split(process_unit, ground_truth,isZip)
    return __create_corpora(test,train)

# Cell
#Data set organization
from tempfile import mkdtemp
import os.path as path
def process_corpora(corpora_train,corpora_test,save_file=False,path="",name=""):
    '''
    Process the corpora data for model training. Takes in corpora_train,corpora_test,save,path,name.

    @param save_file (bool): Determine if the data should be saved on disk.

    @param path (string): Path to where the dataset should be save to.

    @param name (string): Name of the model used to name files saved.
    '''
    #Memoization
    file_corpora_train_x = path.join(mkdtemp(), name + '_temp_corpora_train_x.dat') #Update per experiment
    file_corpora_test_x = path.join(mkdtemp(), name + '_temp_corpora_test_x.dat')

    #Shaping
    shape_train_x = (len(corpora_train),max_len_sentences,embeddigs_cols,1)
    shape_test_x = (len(corpora_test),max_len_sentences,embeddigs_cols,1)

    #Data sets
    corpora_train_x = np.memmap(
        filename = file_corpora_train_x,
        dtype='float32',
        mode='w+',
        shape = shape_train_x)

    corpora_test_x = np.memmap( #Test Corpora (for future evaluation)
        filename = file_corpora_test_x,
        dtype='float32',
        mode='w+',
        shape = shape_test_x)

    target_train_y = np.array(target_train) #Train Target
    target_test_y = np.array(target_test) #Test Target (for future evaluation)

    #Reshaping Train Inputs
    for doc in range(len(corpora_train)):
        for words_rows in range(corpora_train[doc].shape[0]):
            embed_flatten = np.array(corpora_train[doc][words_rows]).flatten() #<--- Capture doc and word
            for embedding_cols in range(embed_flatten.shape[0]):
                corpora_train_x[doc,words_rows,embedding_cols,0] = embed_flatten[embedding_cols]

    #Reshaping Test Inputs (for future evaluation)
    for doc in range(len(corpora_test)):
        for words_rows in range(corpora_test[doc].shape[0]):
            embed_flatten = np.array(corpora_test[doc][words_rows]).flatten() #<--- Capture doc and word
            for embedding_cols in range(embed_flatten.shape[0]):
                corpora_test_x[doc,words_rows,embedding_cols,0] = embed_flatten[embedding_cols]

    #Saving Test Data
    if(save_file):
        np.save(name + '/corpora_test_x.npy',corpora_test_x)
        np.save(name + '/target_test_y.npy',target_test_y)



# Cell
from .utils import Embeddings
import nltk
import numpy as np

def vectorize_sentences(sentences):
    """"""
    nltk.download('stopwords')

    embeddings = Embeddings()
    embed_path = '../data/word_embeddings-embed_size_100-epochs_100.csv'
    embeddings_dict = embeddings.get_embeddings_dict(embed_path)
    inp_shape = (len(sentences), 618, 100, 1)

    for i, sentence in enumerate(sentences):
        vectorized = embeddings.vectorize(sentence, embeddings_dict)

        inp = np.zeros(shape=inp_shape, dtype='float32')
        for words_rows in range(vectorized.shape[0]):
            embed_flatten = np.array(vectorized[words_rows]).flatten()
            for embedding_cols in range(embed_flatten.shape[0]):
                inp[i,words_rows,embedding_cols,0] = embed_flatten[embedding_cols]
        # print(inp)
    return inp