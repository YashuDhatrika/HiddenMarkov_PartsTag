###################################
# CS B551 Fall 2018, Assignment #3
#
#Yashaswini Dhatrika(yhatrik)
#Sushant (sgakhar)
#Devanshi (dsmittal)
# (Based on skeleton code by D. Crandall)
#
#
####
# The following are the process and models using for part of tagging the sentence:

#Step1:Training process:
#The required dictionaries are used which would be useful while implementing different models
#words_dic():stores probabilities of words in the trainingdataset where word is key and prob is value
#t2w() :nested dictionary which stores the count of word in a given tag and total count
#tag_dic():stores probabilities of tags, where each tag is key and prob is value
#transition():stores the probability of each tag starting the sentence
#start_tag_dic:stores the probability of each tag starting the sentence
#tri_transition:stores the 3 consecutive tag states as key and respective count


#Step2:
#Model1:Simplified Method:
#Calculation of pred tags to a sentence:
#1)P(Si/wi) for each tag for a given word is calculated using bayes law, which is equalivalent to P(wi/si)*p(si)/P(w1)
#2) And a tag for a given word is assigned based on maximum probability.


#Calculation of log(posterior):
#1:calculating the posterior as P(Si,Si+1,Si+2/wi,wi+1,w+2)=P(wi/si)*p(si)*P(wi+1/si+1).../P(wi,wi+1,wi+2..)
#2:In the calculation we are ignoring the denominator as it is constant


##Model2: HMM model using viterbi Algorithm

#Calculation of pred tags to a sentence:
#Step1: Emission probabilities(P(wi/si)), Transition probabilities(P(si/si-1) 
# and most probable path in the prior state is calculated (v(i))
#Step2:for the 1st word in the sentence or the 1st word (emission probability* intital prob) is calculated
        #Intital prob=the prob of tag starting the sentence.
#Step3: for all the remaining words, by emission probab*max(transition probability*V(i))
#Step4: In order to track which prior state tag is resulting a max value of present state, a key called prev_tag is created to store the values.
#Step5: Once, the step 3 and Step4 is carried for all the words in the sentence, then tag for each word can be found using the backtracking mechanism 
        
#Calculation of log(posterior): 
#1.Calculating the posterior as P(s1,s2,s3../w1,w2,w3..)=P(w1/s1)*P(s1)*P(w2/s2)*P(s2/s1)*P(w3/s3)*P(s3/s2)..../P(w1,w2,w3,w4...)
#2.In the calculation we are ignoring the denominator as it is constant        
    
##Model3: Complex model using gibbs samplings

#Calculation of pred tags to a sentence:
#Step1:  The idea in Gibbs sampling is to generate posterior samples by  sweeping through each variable (or block of variables) to sample from its conditional distribution with the remaining variables fixed to their current values.
#Step2: Calculation of  conditional probability (CP) can break down to 4 cases
    # Let i be the position of word in the sentence which we are sampling
    #Case1: if i==0 (i.e. 1st word in the sentence)
        #CP=P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1)/marginalization over s1(P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1))
    #Case2: if i==1(i.e. 2nd word in the sentence)
        #CP=P(s2/s1)*P(s3/s2,S1)*P(s4/s3,s2)*P(w2/s2)/marginalization over s2(P(s2/s1)*P(s3/s2,S1)*P(s4/s3,s2)*P(w2/s2))

    #Case3: if i=len(sentence)-1 ((i.e. 1st word in the sentence))
        #CP=P(wi/si)*P(si/si-1,si-2)/arginalization over si(P(wi/si)*P(si/si-1,si-2))
    #Case4: Other words in the sentence:
        #CP=P(si/si-1,si-2)*P(wi/si)*P(si+1/si,si-1)*P(si+2/Si,Si+1)/marginalization over Si(P(si/si-1,si-2)*P(wi/si)*P(si+1/si,si-1)*P(si+2/Si,Si+1))

#Step3: Now the samples are generated by using the conditional distribution.The process is just like a flipping a coin but which # of outputs and also baised. 
        #A random output of a tag is assigned using the conditional distribution
#Step4: few thousands of samples are generated and for calculating the predictive tag we eliminate 
#the initial sample generate(warm up period)

#Step5:Based on the max. occurrence in the reliable sample, the tag is assigned to each word.

#Calculation of log(posterior):
 # Calculating the posterior as P(s1,s2,s3../w1,w2,w3..)=P(w1/s1)*P(s1)*P(w2/s2)*P(s2/s1)*P(w3/s3)*P(s3/s1,s2)..../P(w1,w2,w3)
 ##In the calculation we are ignoring the denominator as it is constant       
        
####Results (accuracies) for each technique on test data
##So far scored 2000 sentences with 29442 words.
                  ## Words correct:     Sentences correct: 
 ## 0. Ground truth:      100.00%              100.00%
 ##       1. Simple:       91.73%               37.75%
 ##       2. HMM:          94.88%               53.55%
   ##     3. Complex:       91.74%               40.20%
####

#Observation of the results:
#We can see that HMM Model is outperforms the other models in accuracy
#But generally it is expected that complex model is better than others model as it consider a sequence of tags while computing
# But it might be possible that if the training data isn't huge, then we would be able to get the all the combination of transitions,so thereby missing out some details   

import random
import math
import numpy as np


# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:

    def __init__(self):
        # word_dic stores probabilities of words in the trainingdataset where word is key and prob is value
        self.words_dic = {}
        # tag_dic: stores probabilities of tags, where each tag is key and prob is value
        self.tag_dic = {}
        # t2w is nested dictionary which stores the count of word in a given tag and total count
        # for example {N:{word:4},N:{tag_count:100}}
        self.t2w = {}
        # transition is nested dictionary which stores the transition state of 2 consecutive pairs in the traindata
        self.transition = {}
        # start_tag_dic stores the probability of each tag starting the sentence
        self.start_tag_dic = {}
        # tri_transition is dictionary which stores the 3 consecutive tag states as key and respective count
        self.tri_transition = {}

    # Calculating the log of the posterior probability of a given sentence for given model
    def posterior(self, model, sentence, label):
        # if the tag and word pair isn't found in the training set, a very low probability is assigned
        if model == "Simple":
            log_posterior = 0
            for word, tag in zip(sentence, label):
                # calculating the posterior as P(Si,Si+1,Si+2/wi,wi+1,w+2)=P(wi/si)*p(si)*P(wi+1/si+1).../P(w1,w2,w3)
                # In the calculation we are ignoring the denominator as it is constant
                if word in self.t2w[tag].keys():
                    pos_prob = (self.t2w[tag][word] / self.t2w[tag]['tag_count']) \
                               * (self.tag_dic[tag])
                    log_posterior += math.log(pos_prob)

                else:
                    pos_prob = 0.0000001
                    log_posterior += math.log(pos_prob)
            return log_posterior
        elif model == "Complex":
            # Calculating the posterior as P(s1,s2,s3../w1,w2,w3..)=P(w1/s1)*P(s1)*P(w2/s2)*P(s2/s1)*P(w3/s3)*P(s3/s1,s2)..../P(w1,w2,w3)
            ##In the calculation we are ignoring the denominator as it is constant
            # if the tag and word pair isn't found in the training set, a very low probability is assigned
            # if an transition between states aren't found in the training data a very low probability is assigned.
            log_post = 0
            log_prob = 0
            for i in range(len(sentence)):
                # calculating p(wi/si) using the dictionary t2w

                prob_w_s = self.t2w.get(label[i]).get(sentence[i], 0.0000001)
                if prob_w_s != 0.0000001:
                    prob_w_s = prob_w_s / self.t2w.get(label[i]).get('tag_count')
                # for 1st word in the sentence, we need to calculate P(s1)
                if i == 0:
                    prob_trans = self.tag_dic[label[i]]
                    log_prob += math.log(prob_trans)
                # for 2nd word in the sentence, we need to calculate P(s2/s1)
                elif i == 1:
                    prob_trans = self.transition.get(label[i - 1]).get(label[i], 0.0000001)
                    if prob_trans != 0.0000001:
                        prob_trans = prob_trans / self.transition.get(label[i - 1]).get('trans_count')
                    log_prob += math.log(prob_trans)
                # for all other words in the sentence, we need to calculate P(si/si-1,si-2)
                else:
                    if label[i - 2] + "/" + label[i - 1] + "/" + label[i] in self.tri_transition.keys():
                        tri_trans_key = label[i - 2] + "/" + label[i - 1] + "/" + label[i]
                        prob_trans = self.tri_transition[tri_trans_key] / self.tri_transition['tot_count']
                    else:
                        prob_trans = 0.0000001
                    log_prob += math.log(prob_trans)
                log_prob += math.log(prob_w_s)
                log_post += log_prob
            return log_post

        elif model == "HMM":
            # Calculating the posterior as P(s1,s2,s3../w1,w2,w3..)=P(w1/s1)*P(s1)*P(w2/s2)*P(s2/s1)*P(w3/s3)*P(s3/s2)..../P(w1,w2,w3)
            ##In the calculation we are ignoring the denominator as it is constant
            # if the tag and word pair isn't found in the training set, a very low probability is assigned
            # if an transition between states aren't found in the training data a very low probability is assigned.
            log_post = 0
            for i in range(len(sentence)):
                # for the 1st word calculating the P(s1) and P(w1/s1)
                if i == 0:
                    s0 = self.start_tag_dic.get(label[i])
                    prob_w0_s0 = self.t2w.get(label[i]).get(sentence[i], 0.0000001)
                    if prob_w0_s0 != 0.0000001:
                        prob_w0_s0 = prob_w0_s0 / self.t2w[label[i]]['tag_count']
                    prob0 = math.log(s0 * prob_w0_s0)
                    log_post += prob0

                # for all other words, calculating the P(si/si-1) and P(wi/si)
                if i >= 1:
                    if self.transition[label[i - 1]].get(label[i]) != None:
                        prob_trans = self.transition[label[i - 1]][label[i]] / self.transition[label[i - 1]][
                            'trans_count']
                    else:
                        prob_trans = 0.0000001
                    prob_w_s = self.t2w.get(label[i]).get(sentence[i], 0.0000001)
                    if prob_w_s != 0.0000001:
                        prob_w_s = prob_w_s / self.t2w[label[i]]['tag_count']
                    log_prob = math.log(prob_trans * prob_w_s)
                    log_post += log_prob
            return log_post
        else:
            print("Unknown algo!")

    # Do the training!

    def train(self, data):
        # Calculation of P[Si]
        S = []
        for i in range(0, len(data)):
            x = data[i][1]
            S.append(x)
        S = [tag for sentence in S for tag in sentence]
        dict = {}
        for i in S:
            if (i in dict.keys()):
                dict[i] += 1
            else:
                dict[i] = 1

        total = sum(dict.values())

        self.tag_dic = {k: dict[k] / total for k in dict}

        # Calculation of p(wi)
        W = []
        for i in range(0, len(data)):
            x = data[i][0]
            W.append(x)
        W_new = ('&&'.join([data for ele in W for data in ele])).split('&&')
        dict1 = {}
        for i in W_new:
            if (i in dict1.keys()):
                dict1[i] += 1
            else:
                dict1[i] = 1

        total = sum(dict1.values())

        self.words_dic = {k: dict1[k] / total for k in dict1.keys()}

        # calculation of p(w/s)
        tags_per_sentence = [x[1] for x in data]
        words_per_sentence = [x[0] for x in data]

        W = [w for sentence in words_per_sentence for w in sentence]

        word_data = [(i, j) for i, j in zip(W, S)]

        S = set(S)

        for tag in S:
            temp = []
            for word in word_data:
                if word[1] == tag:
                    temp.append(word[0])
            if tag not in self.t2w.keys():
                self.t2w[tag] = {'tag_count': 0}
            for word in temp:
                if word not in self.t2w[tag].keys():
                    self.t2w[tag][word] = 1
                else:
                    self.t2w[tag][word] += 1
                self.t2w[tag]['tag_count'] += 1

        # calculation of p(Si+1/Si):
        for tags in tags_per_sentence:
            for i in range(0, len(tags) - 1):
                if tags[i] not in self.transition.keys():
                    self.transition[tags[i]] = {'trans_count': 0}
                if tags[i + 1] not in self.transition[tags[i]].keys():
                    self.transition[tags[i]][tags[i + 1]] = 1
                else:
                    self.transition[tags[i]][tags[i + 1]] += 1
                self.transition[tags[i]]['trans_count'] += 1

        # Calculating the prob of each tag starting a sentence
        start_tag = [tags_per_sentence[i][0] for i in range(len(tags_per_sentence))]
        start_dict = {}
        for i in start_tag:
            if (i in start_dict.keys()):
                start_dict[i] += 1
            else:
                start_dict[i] = 1
        total = sum(start_dict.values())
        self.start_tag_dic = {k: start_dict[k] / total for k in start_dict.keys()}

        # Calculation of p(Si+1/Si,Si-1)
        for tags in tags_per_sentence:
            self.tri_transition['tot_count'] = 0
            for i in range(0, len(tags) - 2):
                temp = tags[i] + "/" + tags[i + 1] + "/" + tags[i + 2]
                if temp not in self.tri_transition.keys():
                    self.tri_transition[temp] = 1
                else:
                    self.tri_transition[temp] += 1
                self.tri_transition['tot_count'] += 1


# Functions for each algorithm which predicts the the tags for each word in the sentence
# Following are the consideration taken:
# 1.if the tag and word pair isn't found in the training set, a very low probability is assigned
# 2.if an transition between states aren't found in the training data a very low probability is assigned.

    def simplified(self, sentence):
        list_pred = []
        tags = self.tag_dic.keys()
        for word in sentence:
            temp_tag = {}
            # Simplified model: We just need to calculate the P(si/wi) for all the
            # tag and assign the tag to the word which has max. prob
            for tag in tags:
                if word in self.t2w[tag].keys():
                    # P(si/wi)=P(si/w1)*p(si)/P(wi)
                    temp_tag[tag] = (self.t2w[tag][word] / self.t2w[tag]['tag_count']) \
                                    * (self.tag_dic[tag] / self.words_dic[word])
                else:
                    temp_tag[tag] = 0.0000001
            tag_pred = max(temp_tag, key=temp_tag.get)
            list_pred.append(tag_pred)

        return list_pred

#     The below function calculates the condition probabilities for each word in the sentence, this probabilies are useful gibbs sampling
#    Calculation of P(Si/all the other states except Si are fixed)
#    Calculation of  conditional probability (CP) can break down to 4 cases:
#     Let i be the position of word in the sentence which we are sampling
#    Case1: if i==0 (i.e. 1st word in the sentence)
#        CP=P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1)/marginalization over s1(P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1))
#    Case2: if i==1(i.e. 2nd word in the sentence)
#        CP=P(s2/s1)*P(s3/s2,S1)*P(s4/s3,s2)*P(w2/s2)/marginalization over s2(P(s2/s1)*P(s3/s2,S1)*P(s4/s3,s2)*P(w2/s2))
#
#    Case3: if i=len(sentence)-1 ((i.e. 1st word in the sentence))
#        CP=P(wi/si)*P(si/si-1,si-2)/arginalization over si(P(wi/si)*P(si/si-1,si-2))
#    Case4: Other words in the sentence:
#        CP=P(si/si-1,si-2)*P(wi/si)*P(si+1/si,si-1)*P(si+2/Si,Si+1)/marginalization over Si(P(si/si-1,si-2)*P(wi/si)*P(si+1/si,si-1)*P(si+2/Si,Si+1))


    def joint_dist(self, tag_sample, sentence, i):
        #Attributes:
        # 1.tag_sample: this is the list of all tags assigned to words in the sentence
        #2. Sentence: Sentence of dataset
        #3. i: i is the position on which sampling is done using gibbs sampling
        self.sentence = sentence
        self.sample = tag_sample
        tags = self.tag_dic.keys()
        list1 = []
        #Some of edge cases are considered, when a sentence as single word:
        #CP=P(s1)P(sw1/s1)/marginalization over s1(P(s1)P(sw1/s1))
        if len(sentence) == 1:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys():
                    joint_prob = self.tag_dic[tag] * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        # CP=P(s1)P(sw1/s1)*P(s2/s1)/Marginalization over s2(P(s1)P(sw1/s1)*P(s2/s1))
        if len(sentence) == 2 and i == 0:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and tag_sample[i + 1] in self.transition[tag].keys():
                    joint_prob = self.tag_dic[tag] * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                 * (self.transition[tag][tag_sample[i + 1]] / self.transition[tag]['trans_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        # CP=P(s2/s1)*P(w2/s2)/marginalization over (P(s2/s1)*P(w2/s2))
        if len(sentence) == 2 and i == 1:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and tag in self.transition[tag_sample[i - 1]].keys():
                    joint_prob = (self.transition[tag_sample[i - 1]][tag] / self.transition[tag_sample[i - 1]][
                        'trans_count']) \
                                 * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        #CP=P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1)/marginalization over s1(P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1))
        if len(sentence) == 3 and i == 0:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and tag_sample[i + 1] in self.transition[tag].keys() \
                        and tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2] in self.tri_transition.keys():
                    tri_trans_key = tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2]
                    joint_prob = self.tag_dic[tag] * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                 * (self.transition[tag][tag_sample[i + 1]] / self.transition[tag]['trans_count']) \
                                 * (self.tri_transition[tri_trans_key] / self.tri_transition['tot_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        # CP=P(s2/s1)*P(s3/s2,S1)*P(w2/s2)/marginalization over s2(P(s2/s1)*P(s3/s2,S1)*P(w2/s2))
        if len(sentence) == 3 and i == 1:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and tag in self.transition[tag_sample[i - 1]].keys() and \
                        tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1] in self.tri_transition.keys():
                    tri_trans_key1 = tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1]
                    joint_prob = (self.transition[tag_sample[i - 1]][tag] / self.transition[tag_sample[i - 1]][
                        'trans_count']) \
                                 * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                 * (self.tri_transition[tri_trans_key1] / self.tri_transition['tot_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        #case3:CP=P(wi/si)*P(si/si-1,si-2)/arginalization over si(P(wi/si)*P(si/si-1,si-2))
        if (len(sentence) == 3 and i == 2) or (i == len(sentence) - 1):
            for tag in tags:
                tri_trans_key = tag_sample[i - 2] + "/" + tag_sample[i - 1] + "/" + tag_sample[i]
                if sentence[i] in self.t2w[tag].keys() and tri_trans_key in self.tri_transition.keys():
                    joint_prob = (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                 * (self.tri_transition[tri_trans_key] / self.tri_transition['tot_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        #Case1:CP=P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1)/marginalization over s1(P(s1)P(sw1/s1)*P(s2/s1)*P(s3/s2,S1))
        if i == 0:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and tag_sample[i + 1] in self.transition[tag].keys() \
                        and tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2] in self.tri_transition.keys():
                    tri_trans_key = tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2]
                    joint_prob = self.tag_dic[tag] * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                 * (self.transition[tag][tag_sample[i + 1]] / self.transition[tag]['trans_count']) \
                                 * (self.tri_transition[tri_trans_key] / self.tri_transition['tot_count'])
                    list1.append(joint_prob)

                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        #Case2:#CP=P(s2/s1)*P(s3/s2,S1)*P(s4/s3,s2)*P(w2/s2)/marginalization over s2(P(s2/s1)*P(s3/s2,S1)*P(s4/s3,s2)*P(w2/s2))
        if i == 1:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and tag in self.transition[tag_sample[i - 1]].keys() and \
                        tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1] in self.tri_transition.keys() and \
                        tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2] in self.tri_transition.keys():
                    tri_trans_key1 = tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1]
                    tri_trans_key2 = tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2]
                    joint_prob = (self.transition[tag_sample[i - 1]][tag] / self.transition[tag_sample[i - 1]][
                        'trans_count']) \
                                 * (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                 * (self.tri_transition[tri_trans_key1] / self.tri_transition['tot_count']) \
                                 * (self.tri_transition[tri_trans_key2] / self.tri_transition['tot_count'])
                    list1.append(joint_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]
            return list1
        #Case4:
        if i > 1:
            for tag in tags:
                if sentence[i] in self.t2w[tag].keys() and len(sentence) - 1 >= i + 2 and \
                        tag_sample[i - 2] + "/" + tag_sample[i - 1] + "/" + tag in self.tri_transition.keys() and \
                        tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1] in self.tri_transition.keys() and \
                        tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2] in self.tri_transition.keys():
                    tri_trans_key1 = tag_sample[i - 2] + "/" + tag_sample[i - 1] + "/" + tag
                    tri_trans_key2 = tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1]
                    tri_trans_key3 = tag + "/" + tag_sample[i + 1] + "/" + tag_sample[i + 2]
                    # print(tri_trans_key1,tri_trans_key2,tri_trans_key3,sentence[i],tag)
                    join_prob = (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                * (self.tri_transition[tri_trans_key1] / self.tri_transition['tot_count']) \
                                * (self.tri_transition[tri_trans_key2] / self.tri_transition['tot_count']) \
                                * (self.tri_transition[tri_trans_key3] / self.tri_transition['tot_count'])
                    list1.append(join_prob)

                elif sentence[i] in self.t2w[tag].keys() and len(sentence) - 1 >= i + 1 and \
                        tag_sample[i - 2] + "/" + tag_sample[i - 1] + "/" + tag in self.tri_transition.keys() and \
                        tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1] in self.tri_transition.keys():
                    tri_trans_key1 = tag_sample[i - 2] + "/" + tag_sample[i - 1] + "/" + tag
                    tri_trans_key2 = tag_sample[i - 1] + "/" + tag + "/" + tag_sample[i + 1]
                    join_prob = (self.t2w[tag][sentence[i]] / self.t2w[tag]['tag_count']) \
                                * (self.tri_transition[tri_trans_key1] / self.tri_transition['tot_count']) \
                                * (self.tri_transition[tri_trans_key2] / self.tri_transition['tot_count'])
                    list1.append(join_prob)
                else:
                    joint_prob = 0.0000001
                    list1.append(joint_prob)
            value = sum(list1)
            list1 = [x / value for x in list1]

        return list1


    # This function performs the MCMC -Gibbs samplings
    #Flow of the code inside complex_mcmc is as follows:
    #Step1.A random tag is assigned to each words in the sentence
    #Step2.Gibbs sampling is performed across all the words using the the joint_dist function
    #Step3: Each tag for a word is sampled based on the distribution , and a tag is choosen from the 12 values just as flipping a coin but which as many outputs and baised
    #Step4: Few thousands of samples are generated by fixing all the tags and just sampling one.
    #Step5: Then the posterior for each word is calculated based on the max. occurrence on the samples excluding some of the inital samples generated(warm up period)
    def complex_mcmc(self, sentence):
        tags = list(self.tag_dic.keys())
        #Random tag of len of sentence is generated
        rand_tag = list(np.random.choice(list(tags), len(sentence)))
        all_sample = []
        all_sample.append(rand_tag)
        t = 0
        while t <= 500:
            for i in range(0, len(sentence)):
                #samples are generating by sampling one tag which would traverse from 1st word of sentence to last
                tags_prob = self.joint_dist(rand_tag, sentence, i)
                # a tag is assigned based on conditional distribution using random.choice()
                rand_tag[i] = np.random.choice(list(tags), 1, p=tags_prob)[0]
                all_sample.append(rand_tag)
            t += 1

        reliable_sample = all_sample[100:]
        dict1 = {}
        for i in range(0, len(sentence)):
            if i not in dict1.keys():
                dict1[i] = {}
        for sample in reliable_sample:
            for j in range(0, len(sample)):
                if sample[j] not in dict1[j].keys():
                    dict1[j][sample[j]] = 1
                else:
                    dict1[j][sample[j]] += 1
        pred_tag = []
        for i in range(len(sentence)):
            pred_tag.append(max(dict1[i], key=lambda x: dict1[i][x]))
        return pred_tag
    
    
    
    
    
#The below function perform the viterbi algorithm
#Flow of code inside the function is as follows:
#Step1: for the 1st word emission probability* intital prob is calculated
    #where emission probability=p(wi/si)
    #Intital prob=the prob of tag starting the sentence.
#Step2: for all the remaining words, by emission probab*max(transition probability*prob of prior state)
#Step3: In order to track which prior state tag is resulting a max value of present state, a key called prev_tag is created to store the values.
#Step4: Once, the step 2 and Step3 is carried for all the words in the sentence, then tag for each word can be found using the backtracking mechanism   
    def hmm_viterbi(self, sentence):
        vit = []
        for i in range(0, len(sentence)):
            temp_dic = {tag: {'prob': 0, 'prev_tag': ''} for tag in self.tag_dic.keys()}
            # temp_lst=[]

            for cur_tag in self.tag_dic.keys():
                #
                max_prob = -9999999
                likely_tag = ''
                if sentence[i] not in self.t2w[cur_tag].keys():
                    e_prob = 0.000001
                else:
                    e_prob = self.t2w[cur_tag][sentence[i]] / self.t2w[cur_tag]['tag_count']

                if i == 0:

                    if cur_tag not in self.start_tag_dic.keys():
                        init_prob = 0.0000001
                    else:
                        init_prob = self.start_tag_dic[cur_tag]
                    temp_dic[cur_tag]['prob'] = e_prob * init_prob

                    # print(temp_dic)

                    # temp_dic[cur_tag]['prob']=0.000001
                else:
                    for prev_tag in vit[-1].keys():

                        if cur_tag not in self.transition[prev_tag].keys():
                            trans_prob = 0.0000001
                        else:
                            trans_prob = self.transition[prev_tag][cur_tag] / self.transition[prev_tag]['trans_count']

                        if max_prob < vit[-1][prev_tag]['prob'] * trans_prob:
                            max_prob = vit[-1][prev_tag]['prob'] * trans_prob
                            likely_tag = prev_tag

                    temp_dic[cur_tag]['prob'] = e_prob * max_prob
                    temp_dic[cur_tag]['prev_tag'] = likely_tag
            #                    print(temp_dic[cur_tag])
            vit.append(temp_dic)
        #            print(vit[-1])
        #Backtracking in order to assign the predictive tag to each word based on the max value obtained
        pred = []
        start = max(vit[-1], key=lambda x: vit[-1][x]['prob'])
        pred.append(start)
        vit = vit[::-1]
        for i in range(0, len(vit) - 1):
            pred.append(vit[i][start]["prev_tag"])
            start = vit[i][start]["prev_tag"]

        return pred[::-1]

    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself.
    # It should return a list of part-of-speech labelings of the sentence, one
    #  part of speech per word.
    #
    def solve(self, model, sentence):
        if model == "Simple":
            return self.simplified(sentence)
        elif model == "Complex":
            return self.complex_mcmc(sentence)
        elif model == "HMM":
            return self.hmm_viterbi(sentence)
        else:
            print("Unknown algo!")

