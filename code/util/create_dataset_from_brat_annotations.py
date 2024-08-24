import json
from nltk.tokenize import sent_tokenize
from transformers import BertTokenizer
import os

BRAT_ANNOTATIONS_PATH = '../brat/brat-data/'
BRAT_ANNOTATIONS_PATH_RIZA = f'{BRAT_ANNOTATIONS_PATH}CGDC_corpus_RB/'
BRAT_ANNOTATIONS_PATH_YOUCEF = f'{BRAT_ANNOTATIONS_PATH}CGDC_corpus_YB/'
BRAT_ANNOTATIONS_PATH_EWAN = f'{BRAT_ANNOTATIONS_PATH}PCWSubset_Ewan_RE/'
BRAT_ANNOTATIONS_CGDC_3 = f'{BRAT_ANNOTATIONS_PATH}mixed_riza/'


files = os.listdir(BRAT_ANNOTATIONS_CGDC_3)
files_filtered = [x for x in files if x[0].isdigit()]
file_names = [x[:-4] for x in files_filtered if x[-1] == "n"]



tokenizer = BertTokenizer.from_pretrained('bert-base-cased')

def entity_belongs_to_sentence(raw_text, sentences, sentence_index, sentence, named_entities, entity):
    text_before_entity = raw_text[:named_entities[entity]['start_index']].split()
    text_after_entity = raw_text[named_entities[entity]['end_index']:].split()
    starting_index = 0
    while True:
        try:
            text_before_word_from_sentence = sentence[:sentence.index(named_entities[entity]["name"], starting_index)].split()
            text_before_word_from_sentence = [x for x in text_before_word_from_sentence if x != ""]
            text_after_word_from_sentence = sentence[sentence.index(named_entities[entity]["name"], starting_index) + len(named_entities[entity]["name"]):].split()
            text_after_word_from_sentence = [x for x in text_after_word_from_sentence if x != ""]
            word_before_entity = text_before_entity[-1] if len(text_before_entity) != 0 else " "
            word_after_entity = text_after_entity[0] if len(text_after_entity) != 0 else " "
            word_before_word_from_sentence = text_before_word_from_sentence[-1] if len(text_before_word_from_sentence) != 0 else " "
            word_after_word_from_sentence = text_after_word_from_sentence[0] if len(text_after_word_from_sentence) != 0 else " "
            if word_before_word_from_sentence == " " and sentence_index != 0:
                word_before_word_from_sentence = sentences[sentence_index - 1].split()[-1]
            if word_after_word_from_sentence == " " and sentence_index != len(sentences) - 1:
                word_after_word_from_sentence = sentences[sentence_index + 1].split()[0]
            if word_before_entity == word_before_word_from_sentence and word_after_entity == word_after_word_from_sentence:
                return True
            else:
                starting_index = sentence.index(named_entities[entity]["name"], starting_index) + len(named_entities[entity]["name"])
        except ValueError:
            return False

def bert_sentence_tokenizer(sentence):
    sentence_split = tokenizer.tokenize(sentence)
    offset = 0
    for index in range(len(sentence_split)):
        if sentence_split[index - offset].startswith("##"):
            sentence_split[index - 1 - offset] += sentence_split[index - offset][2:]
            del sentence_split[index - offset]
            offset += 1
    return sentence_split

data = {}

for idx, file_name in enumerate(file_names):
    print(f"File name: {file_name} ({idx+1}/{len(file_names)})")
    with open(f'{BRAT_ANNOTATIONS_CGDC_3}{file_name}.ann', 'r') as infile:
        annotation_data = []
        for line in infile:
            annotation_data.append(line[:-1])

    named_entities = {}
    relations = {}
    for line in annotation_data:
        if line.split()[0][0] == "T":
            (entity_number, entity_type, start_index, end_index) = line.split()[:4]
            #If NE goes on new line, syntax in brat adds ;
            if ";" in end_index:
                (entity_number, entity_type, start_index, _ , end_index) = line.split()[:5]
                print("HERE")
            name = " ".join(line.split()[4:])
            named_entities[entity_number] = {
                'entity_type': entity_type,
                'start_index': int(start_index),
                'end_index': int(end_index),
                'name': name,
                'wiki_link': "N/A"
            }
        elif line.split()[0][0] == "R":
            (relation_number, relation_name, head_entity, tail_entity) = line.split()
            relations[f"{head_entity[5:]}_{tail_entity[5:]}"] = {
                'relation_name': relation_name,
                'head_entity': head_entity[5:],
                'tail_entity': tail_entity[5:],
                'sentence': ""
            }
        elif line.split()[0][0] == "#":
            try:
                (annotator_number, _, entity_number, wiki_link) = line.split()
            except ValueError:
                continue
            named_entities[entity_number]['wiki_link'] = wiki_link.split("/")[-1]
    
    with open(f'{BRAT_ANNOTATIONS_CGDC_3}{file_name}.txt', 'r') as infile:
        raw_text = infile.read()

    tokenized_text = sent_tokenize(raw_text)
    sentences = []
    for token in tokenized_text:
        sentences += token.split('\n')
    sentences = [x for x in sentences if x.strip() != ""]


    for sentence_index, sentence in enumerate(sentences):
        for head_entity in named_entities:
            for tail_entity in named_entities:
                if head_entity != tail_entity and named_entities[head_entity]["name"] in sentence and named_entities[tail_entity]["name"] in sentence:
                    if entity_belongs_to_sentence(raw_text, sentences, sentence_index, sentence, named_entities, head_entity) and entity_belongs_to_sentence(raw_text, sentences, sentence_index, sentence, named_entities, tail_entity):
                        if f"{head_entity}_{tail_entity}" not in relations and head_entity != tail_entity:
                            relations[f"{head_entity}_{tail_entity}"] = {
                                'relation_name': "NOTA",
                                'head_entity': head_entity,
                                'tail_entity': tail_entity,
                                'sentence': sentence
                            }
                        else:
                            relations[f"{head_entity}_{tail_entity}"]['sentence'] = sentence
    for key, obj in relations.items():
        sentence_split = bert_sentence_tokenizer(obj['sentence'])
        head_entity_name = named_entities[obj['head_entity']]['name']
        head_entity_name_split = bert_sentence_tokenizer(head_entity_name)
        tail_entity_name = named_entities[obj['tail_entity']]['name']
        tail_entity_name_split = bert_sentence_tokenizer(tail_entity_name)
        object_to_append = {
            'tokens': obj['sentence'],
            'h': [head_entity_name, named_entities[obj['head_entity']]['wiki_link'], named_entities[obj['head_entity']]['entity_type']],
            't': [tail_entity_name, named_entities[obj['tail_entity']]['wiki_link'], named_entities[obj['tail_entity']]['entity_type']]
        }
        if obj['relation_name'] in data:
            data[obj['relation_name']].append(object_to_append)
        else:
            data[obj['relation_name']] = [object_to_append]

# print(f"Total number of labels: {len(data.keys())}")
# for key, obj in data.items():
#     print(f"For key: {key}")
#     for i, sample in enumerate(obj):
#         print(f"Sample {i+1}")
#         print(f"Tokens: {sample['tokens']}")
#         print(f"Head: {sample['h']}")
#         print(f"Tail: {sample['t']}")
#         print()
#     print()

for key in data:
    data[key] = [obj for obj in data[key] if len(obj['tokens']) != 0 and len(obj['h'][0]) != 0 and len(obj['t'][0]) != 0]

with open("CGDC_dataset_3.0.json", 'w') as outfile:
    json.dump(data, outfile)