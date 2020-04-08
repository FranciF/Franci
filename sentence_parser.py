#!/usr/bin/env python3
# coding: utf-8
# File: sentence_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10


import os
#from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer
from pyhanlp import *


class LtpParser():

    '''ltp基本操作'''
    '''postags, netags = self.basic_parser(words)'''
    def basic_parser(self, words):
        postags = list(self.postagger.postag(words))
        #postage= [str(term.nature) for term in self.HanLP.segment((words))]
        netags = self.recognizer.recognize(words, postags)
        return postags, netags

    '''ltp获取词性'''
    def get_postag(self, words):
        return list(self.postagger.postag(words))

    '''基于实体识别结果,整理输出实体列表'''
    '''name_entity_dist = self.format_entity(words, netags, postags)'''
    def format_entity(self, words, postags):
        name_entity_dist = {}
        name_entity_list = []
        place_entity_list = []
        organization_entity_list = []
        ntag_E_Nh = ""
        ntag_E_Ni = ""
        ntag_E_Ns = ""
        index = 0
        for item in zip(words, postags):
            word = item[0]
            ptag = item[1]
            if ptag == 'nr':
                name_entity_list.append(word+'_%s ' % index)
            elif ptag == 'nt':
                organization_entity_list.append(word+'_%s ' % index)
            elif ptag == 'ns':
                place_entity_list.append(word + '_%s ' % index)
                
            index += 1
        name_entity_dist['nhs'] = name_entity_list
        name_entity_dist['nis'] = organization_entity_list
        name_entity_dist['nss'] = place_entity_list
        
        return name_entity_dist

    '''entity修正,为rebuild_wordspostags做准备'''
    def modify_entity(self, entity_list, words, postags, tag):
        entity_modify = []
        if entity_list:
            for entity in entity_list:
                entity_dict = {}
                subs = entity.split(' ')[:-1]
                start_index = subs[0].split('_')[1]
                end_index = subs[-1].split('_')[1]
                entity_dict['stat_index'] = start_index
                entity_dict['end_index'] = end_index
                if start_index == entity_dict['end_index']:
                    consist = [words[int(start_index)] + '/' + postags[int(start_index)]]
                else:
                    consist = [words[index] + '/' + postags[index] for index in range(int(start_index), int(end_index)+1)]
                entity_dict['consist'] = consist
                entity_dict['name'] = ''.join(tmp.split('_')[0] for tmp in subs) + '/' + tag
                entity_modify.append(entity_dict)
        return entity_modify

    '''基于命名实体识别,修正words,postags'''
    '''words, postags = self.rebuild_wordspostags(name_entity_dist, words, postags)'''
    def rebuild_wordspostags(self, name_entity_dist, words, postags):
        pre = ' '.join([item[0] + '/' + item[1] for item in zip(words, postags)])
        post = pre
        for et, infos in name_entity_dist.items():
            if infos:
                for info in infos:
                    post = post.replace(' '.join(info['consist']), info['name'])
        post = [word for word in post.split(' ') if len(word.split('/')) == 2 and word.split('/')[0]]
        words = [tmp.split('/')[0] for tmp in post]
        postags = [tmp.split('/')[1] for tmp in post]

        return words, postags

    '''依存关系格式化'''
    '''tuples = self.syntax_parser(words, postags)'''
    def syntax_parser(self, words, postags,sentence):
        sentence_parse = HanLP.parseDependency(sentence)
        word_array = sentence_parse.getWordArray()
        arcs = [str(word.HEAD).split('\t')[0] for word in word_array]
        relation = [str(word.DEPREL) for word in word_array]
        tuples = list()
        for index in range(len(words)-1):
            arc_index = arcs[index]
            tuples.append([index+1, words[index], postags[index], words[arc_index], postags[arc_index], arc_index, arc_relation[index]])

        return tuples

    '''为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
    '''child_dict_list = self.build_parse_child_dict(words, postags, tuples)'''
    def build_parse_child_dict(self, words, postags, tuples):
        child_dict_list = list()
        for index, word in enumerate(words):
            child_dict = dict()
            for arc in tuples:
                if arc[3] == word:
                    if arc[-1] in child_dict:
                        child_dict[arc[-1]].append(arc)
                    else:
                        child_dict[arc[-1]] = []
                        child_dict[arc[-1]].append(arc)
            child_dict_list.append([word, postags[index], index, child_dict])

        return child_dict_list

    '''parser主函数'''
    '''抽取出事件三元组'''
    '''tuples, child_dict_list = self.parser.parser_main(words, postags)'''
    def parser_main(self, words, postags,sentence):
        tuples = self.syntax_parser(words, postags,sentence)
        child_dict_list = self.build_parse_child_dict(words, postags, tuples)
        return tuples, child_dict_list

    '''基础语言分析'''
    '''对句子进行分词，词性标注处理'''
    '''words, postags = self.parser.basic_process(sent)'''
    def basic_process(self, sentence):
        words=[str(term.word) for term in self.HanLP.segment((sentence))]
        postage= [str(term.nature) for term in self.HanLP.segment((sentence))]
        name_entity_dist = self.format_entity(words, postags)
        #words, postags = self.rebuild_wordspostags(name_entity_dist, words, postags)
        return words, postags





