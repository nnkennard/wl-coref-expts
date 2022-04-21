import json
import sys

def main():
  with open(sys.argv[1], 'r') as f:
    for line in f:
      obj = json.loads(line)
      words = obj['cased_words']
      for cluster in obj['clusters']:
        surface_forms = [" ".join(words[a:b+1]) for a,b in cluster]
        print(surface_forms)
      exit()


if __name__ == "__main__":
  main()

