# code for loading the format for the notebook
import os

import os
import string
import re
from array import array

import nltk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import time
from collections import Counter
from keras.utils import to_categorical
from keras.utils.data_utils import get_file
from keras.models import Sequential, load_model
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.preprocessing.text import Tokenizer

# path : store the current path to convert back to it later
base_path = os.path.abspath('English Literature.txt')

with open(base_path, encoding='utf-8') as f:
    raw_text = f.read()

sample = raw_text


# print("Raw sample", sample)

###Data preprocessing - All the commas and dots are seperated by a space for data preprocessing.
def format_patent(patent):
    """Add spaces around punctuation and remove references to images/citations."""

    # Add spaces around punctuation
    patent = re.sub(r'(?<=[^\s0-9])(?=[:.,;?])', r' ', patent)

    # Remove references to figures
    patent = re.sub(r'\((\d+)\)', r'', patent)

    # Remove double spaces
    patent = re.sub(r'\s\s', ' ', patent)
    return patent


f = format_patent(sample)
# print("Formatted", f)

# tokenizer = Tokenizer(filters='"#$%&*+/:;<=>?@[\\]^_`{|}~\t\n')
# tokenizer.fit_on_texts([f])
# s = tokenizer.texts_to_sequences([f])[0]
# ' '.join(tokenizer.index_word[i] for i in s)
# tokenizer.word_index.keys()

# tokens = nltk.word_tokenize(f)

# print("No of token inputs", len(tokens))

##Convert the document into sentences
sentence_tokenize = nltk.tokenize.sent_tokenize(f)
print(sentence_tokenize)

sent_len = 15
i = 0
input_X = []
output_y = []

X = []
y = []
for i in range(len(sentence_tokenize)):
    sentences = nltk.word_tokenize(sentence_tokenize[i])
    tokenizer = Tokenizer()
    #tokenizer = nltk.RegexpTokenizer(r"\w+")
    #sentences = tokenizer.tokenize(sentence_tokenize[i])
    if (len(X) < sent_len) or (len(X) > sent_len):
        tokenizer.fit_on_texts([sentences])
        encoded = tokenizer.texts_to_sequences([sentences])[0]
        padded_sent = pad_sequences([encoded], maxlen=sent_len, dtype='int32', padding='pre', truncating='pre',
                                    value=0.0)
        for j in range(len(padded_sent)):
            input_X = padded_sent[0][:(sent_len - 1)]
            output_y = padded_sent[:, (sent_len - 1)]
            X.append(input_X)
            y.append(output_y)
    elif len(X) == sent_len:
        tokenizer.fit_on_texts([sentences])
        encoded = tokenizer.texts_to_sequences([sentences])[0]
        padded_sent = pad_sequences([encoded], maxlen=sent_len, dtype='int32', padding='pre', truncating='pre',
                                    value=0.0)
        for k in range(len(padded_sent)):
            input_X = padded_sent[0][:(sent_len - 1)]
            output_y = padded_sent[:, (sent_len - 1)]
            X.append(input_X)
            y.append(output_y)

# integer encode text
X = np.array(X)
y = np.array(y)
print(X, y)
max_words = 10

# integer encode text
tokenizer = Tokenizer()
tokenizer.fit_on_texts([f])
encoded = tokenizer.texts_to_sequences([f])[0]

# determine the vocabulary size
vocab_size = len(tokenizer.word_index) + 1
print('Vocabulary Size: %d' % vocab_size)


# one hot encode outputs
y = to_categorical(y, num_classes=vocab_size)

print(y)
print(len(y))

# define the network architecture: a embedding followed by LSTM
embedding_size = 15
lstm_size = 50
model1 = Sequential()
model1.add(Embedding(vocab_size, embedding_size, input_length=14))
model1.add(LSTM(lstm_size))
model1.add(Dense(vocab_size, activation='softmax'))
model1.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model1.summary())

# fit network
model1.fit(X, y, epochs=10, verbose=2)


# generate a sequence from the model
def generate_seq(model, tokenizer, seed_text, n_words):
    in_text, result = seed_text, seed_text
    # generate a fixed number of words
    for _ in range(n_words):
        # encode the text as integer
        encoded = tokenizer.texts_to_sequences([in_text])[0]
        encoded = np.array(encoded)
        # predict a word in the vocabulary
        yhat = model.predict_classes(encoded, verbose=0)
        # map predicted word index to word
        out_word = ''
        for word, index in tokenizer.word_index.items():
            if index == yhat:
                out_word = word
                break
        # append to input
        in_text, result = out_word, result + ' ' + out_word
    return result


# evaluate
print(generate_seq(model1, tokenizer, 'Speak', 6))
