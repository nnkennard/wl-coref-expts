import collections
import json
import tqdm
import prep_lib

SPACE = "SPACE"

def clean_sentence(tokens):
  clean = []
  for token in tokens:
    if not token.strip() and not token == '\x7f':
      clean.append(SPACE)
    else:
      clean.append(token)
  return clean

def convert_document(document):

  data = {
        "document_id":      "pt/preco/00/"+document["id"],
        "cased_words":      [],
        "sent_id":          [],
        "part_id":          0,
        "speaker":          [],
        "pos":              [],
        "deprel":           [],
        "head":             [],
        "clusters":         []
    }

  offset_map = {}
  offset = 0
  text_for_parsing = []
  for i, sentence in enumerate(document['sentences']):
    cleaned_sentence = clean_sentence(sentence)
    offset_map[i] = offset
    offset += len(cleaned_sentence)
    data['sent_id'] += [i] * len(cleaned_sentence)
    text_for_parsing.append(" ".join(cleaned_sentence))
    data['cased_words'] += cleaned_sentence

  pos, head, deprel = prep_lib.get_document_syntax("\n\n".join(text_for_parsing))
  data['pos'] = pos
  data['head'] = head
  data['deprel'] = deprel
  data['speaker'] = [prep_lib.SPEAKER_PLACEHOLDER for _ in pos]

  assert len(set([len(data[key]) for key in "cased_words sent_id speaker pos head deprel".split()])) == 1

  for cluster in document['mention_clusters']:
    new_cluster = []
    for sentence, begin, end in cluster:
      new_cluster.append([offset_map[sentence] + begin, offset_map[sentence] +
      end])
    data['clusters'].append(new_cluster)

  return json.dumps(data)


def main():

  example_lists = collections.defaultdict(list)

  with open(f'PreCo_1.0/train.jsonl', 'r') as f:
    for i, line in enumerate(f):
      if i % 10 == 0:
        example_lists['dev'].append(line)
      else:
        example_lists['train'].append(line)
  with open(f'PreCo_1.0/dev.jsonl', 'r') as f:
    for line in f:
      example_lists['test'].append(line)

  for subset, examples in example_lists.items():
    print(subset)
    with open(f"../../preprocessed_data/preco/english_{subset}.jsonlines", 'w') as f:
      for example in tqdm.tqdm(examples):
        f.write(convert_document(json.loads(example)) + "\n")


if __name__ == "__main__":
  main()

