import stanza

SPEAKER_PLACEHOLDER = "Speaker0"

STANZA_PIPELINE = stanza.Pipeline(lang="en",
                                  processors="tokenize,pos,lemma,depparse",
                                  tokenize_pretokenized=True,
                                  tokenize_no_ssplit=True)



def get_token_syntax(token, sentence_offset):
  (token_dict,) = token.to_dict()
  head = token_dict["head"] - 1
  head = None if head < 0 else sentence_offset + head
  return token_dict["xpos"], head, token_dict["deprel"]


def get_sentence_syntax(tokens, sentence_offset):
    annotated = STANZA_PIPELINE(" ".join(tokens))
    (sentence,) = annotated.sentences
    return zip(
        *
        [get_token_syntax(token, sentence_offset) for token in sentence.tokens])


def get_document_syntax(document_string):
  doc_pos = []
  doc_head = []
  doc_deprel = []
  annotated = STANZA_PIPELINE(document_string)
  sentence_offset = 0
  for sentence in annotated.sentences:
    pos, head, deprel =  zip(
        *
        [get_token_syntax(token, sentence_offset) for token in sentence.tokens])
    doc_pos += pos
    doc_head += head
    doc_deprel += deprel
    sentence_offset += len(sentence.tokens)

  return doc_pos, doc_head, doc_deprel

