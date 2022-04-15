import collections
import glob

COREF_DATA_GLOB = "litbank/coref/conll/*"
SPEAKER_PLACEHOLDER = "Speaker0"

def coref_to_spans(coref_col, offset):
  span_starts = collections.defaultdict(list)
  complete_spans = []
  for i, orig_label in enumerate(coref_col):
    if orig_label == '-':
      continue
    else:
      labels = orig_label.split("|")
      for label in labels:
        if label.startswith("("):
          if label.endswith(")"):
            complete_spans.append((i, i, label[1:-1]))
          else:
            span_starts[label[1:]].append(i)
        elif label.endswith(")"):
          ending_cluster = label[:-1]
          assert len(span_starts[ending_cluster]) in [1, 2]
          maybe_start_idx = span_starts[ending_cluster].pop(-1)
          complete_spans.append((maybe_start_idx, i, ending_cluster))

  span_dict = collections.defaultdict(list)
  for start, end, cluster in complete_spans:
    span_dict[cluster].append((offset + start, offset + end))


  return span_dict

def clean_token_line(line):
  fields = line.strip().split("\t")
  return fields[3], fields[-1]

def build_document(filename):

  data = {
        "document_id":      None,
        "cased_words":      [],
        "sent_id":          [],
        "part_id":          [],
        "speaker":          [],
        "pos":              [],
        "deprel":           [],
        "head":             [],
        "clusters":         []
    }

  with open(filename, 'r') as f:
    lines = f.readlines()

  sentence_lines = []
  current_sentence = []
  for line in lines:
    if line.startswith("#begin"):
      _, _, wrapped_document, _, _ = line.split()
      data['document_id'] = wrapped_document[1:-2]
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
    data['cased_words'] += tokens
    data['sent_id'] += [sentence_index for _ in tokens]
    data['part_id'] += [0 for _ in tokens]
    data['speaker'] += [SPEAKER_PLACEHOLDER for _ in tokens]
    
    print(" ".join(tokens))
    print(coref_map)
    sentence_offset += len(tokens)
  data['clusters'] = list(cluster_builder.values())

def main():
  test_data =  []
  for filename in sorted(glob.glob(COREF_DATA_GLOB)):
    test_data.append(build_document(filename))
    break


if __name__ == "__main__":
  main()
