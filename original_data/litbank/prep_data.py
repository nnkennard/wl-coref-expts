import collections
import glob
import json
import stanza
import tqdm

STANZA_PIPELINE = stanza.Pipeline(lang="en",
                                  processors="tokenize,pos,lemma,depparse",
                                  tokenize_pretokenized=True)

COREF_DATA_GLOB = "litbank/coref/conll/*"
SPEAKER_PLACEHOLDER = "Speaker0"


def coref_to_spans(coref_col, offset):
  span_starts = collections.defaultdict(list)
  complete_spans = []
  for i, orig_label in enumerate(coref_col):
    if orig_label == "-":
      continue
    else:
      labels = orig_label.split("|")
      for label in labels:
        if label.startswith("("):
          if label.endswith(")"):
            complete_spans.append((i, i + 1, label[1:-1]))
          else:
            span_starts[label[1:]].append(i)
        elif label.endswith(")"):
          ending_cluster = label[:-1]
          assert len(span_starts[ending_cluster]) in [1, 2]
          maybe_start_idx = span_starts[ending_cluster].pop(-1)
          complete_spans.append((maybe_start_idx, i+1, ending_cluster))

  span_dict = collections.defaultdict(list)
  for start, end, cluster in complete_spans:
    span_dict[cluster].append((offset + start, offset + end))

  return span_dict


def clean_token_line(line):
  fields = line.strip().split("\t")
  return fields[3], fields[-1]


def get_token_syntax(token, sentence_offset):
  (token_dict,) = token.to_dict()
  head = token_dict["head"] - 1
  head = None if head < 0 else sentence_offset + head
  return token_dict["xpos"], head, token_dict["deprel"]


def build_document(filename):

  data = {
      "document_id": None,
      "cased_words": [],
      "sent_id": [],
      "part_id": 0,
      "speaker": [],
      "pos": [],
      "deprel": [],
      "head": [],
      "clusters": [],
  }

  with open(filename, "r") as f:
    lines = f.readlines()

  sentence_lines = []
  current_sentence = []
  for line in lines:
    if line.startswith("#begin"):
      _, _, wrapped_document, _, _ = line.split()
      data["document_id"] = "pt/litbank/00/"+ wrapped_document[1:-2]
    elif line.startswith("#end"):
      assert not current_sentence
    elif not line.strip():
      sentence_lines.append(current_sentence)
      current_sentence = []
    else:
      current_sentence.append(line)

  sentence_offset = 0
  cluster_builder = collections.defaultdict(list)
  for sentence_index, token_list in enumerate(sentence_lines):
    tokens, coref_col = zip(*[clean_token_line(line) for line in token_list])
    coref_map = coref_to_spans(coref_col, sentence_offset)
    for cluster_id, spans in coref_map.items():
      cluster_builder[cluster_id] += spans
    data["cased_words"] += tokens
    data["sent_id"] += [sentence_index for _ in tokens]
    data["speaker"] += [SPEAKER_PLACEHOLDER for _ in tokens]

    annotated = STANZA_PIPELINE(" ".join(tokens))
    (sentence,) = annotated.sentences
    pos, head, deprel = zip(
        *
        [get_token_syntax(token, sentence_offset) for token in sentence.tokens])
    data["pos"] += pos
    data["head"] += head
    data["deprel"] += deprel

    sentence_offset += len(tokens)
  data["clusters"] = list(cluster_builder.values())

  return data


def main():
  test_data = []
  for filename in tqdm.tqdm(sorted(glob.glob(COREF_DATA_GLOB))):
    test_data.append(build_document(filename))
  with open("../../preprocessed_data/litbank/english_test.jsonlines", 'w') as f:
    for document in test_data:
      f.write(json.dumps(document)+"\n")


if __name__ == "__main__":
  main()
