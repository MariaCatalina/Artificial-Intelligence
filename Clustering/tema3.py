''' Popa Maria-Catalina 342C1 '''

from __future__ import print_function
from copy import deepcopy
from math import log, sqrt, pow
from os import listdir
from os.path import isfile, join
import os
import re
from chardet import detect
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import numpy as np
from numpy import unravel_index
from scipy.spatial import distance

# -*- coding: utf-8 -*-
# coding: utf-8


def process_data(filename, dictionary, values, all_words):
    ''' read from file and extract the most significant words '''

    open_file = open(filename, "r")

    list_tags_available = ['VB', 'NN', 'JJ']

    lmtzr = WordNetLemmatizer()

    TF = {}
    for line in open_file:
        # solve non ASCI characters
        encoding = lambda x: detect(x)['encoding']
        n_line = unicode(line, encoding(line), errors='ignore')

        tokens = nltk.word_tokenize(n_line)

        # get list of tags extract prepositions, articles, particles
        tags = nltk.pos_tag(tokens)

        for (word, tag) in tags:
            if tag in list_tags_available:

                # extract just word with letters
                if re.match("^[a-zA-Z]+$", word):
                    new_word = (lmtzr.lemmatize(word)).lower()

                    # create list with all different words
                    if new_word not in all_words:
                        all_words.append(new_word)
                        TF[new_word] = 1

                    else:
                        new_val = TF[new_word]
                        TF[new_word] = new_val + 1

    files_words = []
    files_values = []
    for (key, val) in TF.iteritems():
        if val > 1:
            files_words.append(key)
            files_values.append(val)
        else:
            all_words.remove(key)

    dictionary[filename] = files_words
    values[filename] = files_values


def search_in_docs(word, dictionary):
    ''' method search how many documents contains a word '''
    count = 0
    for doc in dictionary.keys():
        list_words = dictionary[doc]
        if word in list_words:
            count += 1

    return count


def calculate_df_value(words_list, dictionary, df_words, df_values):
    ''' for each word calculate the number of appearances in documents '''
    for word in words_list:
        count = search_in_docs(word, dictionary)
        df_words.append(word)
        df_values.append(count)


def get_min_position(matrix, number_lines):
    ''' method return the position of the minimum value from matrix '''

    min_val = 10000
    pos_x = -1
    pos_y = -1

    for i in range(number_lines):
        for j in range(i + 1, number_lines):
            if  matrix[i][j] < min_val:
                min_val = matrix[i][j]
                pos_y = j
                pos_x = i

    return pos_x, pos_y


def main():
    ''' the main method '''

    print("solution homework 3")

    files_path = "dataset/"
    list_directories = []

    directories = listdir("dataset")
    classes = {}
    for directory in directories:
        if os.path.isdir(files_path + directory):
            list_directories.append(files_path + directory)
            classes[directory] = 0

    all_words = []
    list_files = []
    dictionary = {}
    values = {}

    # c = {'id': root, 'list': [{}], 'classes': {}}
    cluster_dictionary = []

    for directory in list_directories:
        only_files = [f for f in listdir(directory) if isfile(join(directory, f))]

        for filename in only_files:
            # use for later
            current_file = directory
            directory_file = current_file.split('/')

            my_classes = deepcopy(classes)
            my_classes[directory_file[1]] = 1

            create_file = directory + "/" + filename
            cluster_dictionary.append({'id': create_file, 'list': [], 'classes': my_classes})

            list_files.append(create_file)

            file_list_words = []
            process_data(create_file, dictionary, values, file_list_words)

            all_words += file_list_words

    print(len(all_words))

    print("calculate DF")
    df_words = []
    df_values = []
    calculate_df_value(all_words, dictionary, df_words, df_values)

    print("calculate TF-IDF")

    N = len(list_files)

    TF_IDF = np.arange(len(all_words) * N).reshape(N, len(all_words))
    TF_IDF.fill(0)

    for j in range(N):
        doc_name = list_files[j]
        list_words = dictionary[doc_name]

        for i in range(len(list_words)):

            word = list_words[i]

            tf = 0
            if word in dictionary[doc_name]:
                pos = dictionary[doc_name].index(word)
                tf = values[doc_name][pos]

            df = 0
            if word in df_words:
                pos = df_words.index(word)
                df = df_values[pos]

            IDF = log((N - df + 0.5) / (df + 0.5))
            TF_IDF[j][i] = tf * IDF

    euclidean_distance = np.arange(N * N).reshape(N, N)
    euclidean_distance.fill(0)

    for i in range(N):
        for j in range(i + 1, N):
            if i != j:
                euclidiand = distance.euclidean(TF_IDF[i], TF_IDF[j])
                euclidean_distance[i][j] = euclidiand
                euclidean_distance[j][i] = euclidiand

    print ("calculate clusters")

    while N > 1:
        (pos_x, pos_y) = get_min_position(euclidean_distance, N)

        list_predecessors = []
        list_predecessors.append((cluster_dictionary[pos_x]))
        list_predecessors.append((cluster_dictionary[pos_y]))
        root = "(" + str(cluster_dictionary[pos_x]['id']) + "/" + \
                     str(cluster_dictionary[pos_y]['id']) + ")"

        sum_classes_x = cluster_dictionary[pos_x]['classes']
        sum_classes_y = cluster_dictionary[pos_y]['classes']

        new_sum = {}
        for key in sum_classes_y:
            new_sum[key] = sum_classes_x[key] + sum_classes_y[key]

        cluster_dictionary[pos_x] = {'id': root, 'list': list_predecessors, 'classes': new_sum}
        del cluster_dictionary[pos_y]

        # calculate new value for rows
        new_matrix = euclidean_distance
        for j in range(N):
            if euclidean_distance[pos_x][j] < euclidean_distance[pos_y][j]:
                new_matrix[pos_x][j] = euclidean_distance[pos_x][j]
                new_matrix[j][pos_x] = euclidean_distance[pos_x][j]
            else:
                new_matrix[pos_x][j] = euclidean_distance[pos_y][j]
                new_matrix[j][pos_x] = euclidean_distance[pos_y][j]

        # delete row and column from matrix
        new_matrix = np.delete(new_matrix, pos_y, 0)
        new_matrix = np.delete(new_matrix, pos_y, 1)

        euclidean_distance = deepcopy(new_matrix)
        N -= 1

    print("Calculate performance ")

    sum_purity = 0

    # multimea claselor
    for d in cluster_dictionary:
        list_doc_classification = d['classes']
        print(list_doc_classif)

        maxVal = -10000
        for key in list_doc_classification:
            if list_doc_classif[key] > maxVal:
                maxVal = list_doc_classification[key]

        sum_purity += maxVal

    purity = float(sum_purity / len(list_files))
    print("Purity: ", purity)

main()
