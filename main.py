import math
import sys

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

WORDS_FREQ = open("words_freq.csv", "r").readlines()
WORDS_FREQ = list(map(lambda word_freq : word_freq.replace("\n","").split(","), WORDS_FREQ))
WORDS_FREQ = list(map(lambda word_freq : [ word_freq[0], float(word_freq[1]) ], WORDS_FREQ))

def matches_pattern(guess, word, pattern):
  for c in reversed(word):
    pattern_bit = pattern & 1
    if pattern_bit == 1 and c != guess:
      return False
    if pattern_bit == 0 and c == guess:
      return False
    pattern >>= 1
  return True

def get_pattern(guess, word):
  pattern = 0
  for c in word:
    pattern = pattern << 1
    if c == guess:
      pattern |= 1
  return pattern

def calculate_optimal_guess(word_length, words_freq):
  words_freq = list(filter(lambda word_freq : len(word_freq[0]) == word_length, words_freq))
  lenWordsFreq = len(words_freq)

  if lenWordsFreq == 1:
    return words_freq[0][0][0] # first char of the first word

  highest_entropy = 0
  chosen_guess = ""
  for guess in ALPHABET:
    entropy = 0
    pattern_probs = {}
    total_prob = 0

    for word_freq in words_freq:
      total_prob += word_freq[1]
      pattern = get_pattern(guess, word_freq[0])
      if pattern in pattern_probs:
        pattern_probs[pattern] = pattern_probs[pattern] + word_freq[1]
      else:
        pattern_probs[pattern] = word_freq[1]

    for pattern in pattern_probs:
      pattern_prob = pattern_probs[pattern]
      prob = pattern_prob / total_prob
      entropy += -math.log(prob) * prob

    if entropy > highest_entropy:
      highest_entropy = entropy
      chosen_guess = guess

  return chosen_guess

def filter_and_update_word_freq_list(guess, pattern, words_freq, length):
  filtered_words_freq = []
  for word_freq in words_freq:
    if not matches_pattern(guess, word_freq[0], pattern):
      continue

    if not len(word_freq[0]) == length:
      continue

    filtered_words_freq.append([ word_freq[0].replace(guess, ""), word_freq[1] ])
  return filtered_words_freq

def create_new_pattern_checker_func(old_pattern_checker_func, received_pattern, word_length):
  def new_func(guess):
    pattern = old_pattern_checker_func(guess)

    ret_pattern = 0

    j = 0
    for i in range(word_length):
      received_pattern_bit = (received_pattern >> i) & 1
      pattern_bit = (pattern >> i) & 1
      if received_pattern_bit == 0:
        ret_pattern |= pattern_bit << j
        j += 1

    return ret_pattern

  return new_func

def _play(pattern_checker_func, word_length, words_freq):
  if len(words_freq) == 1 and len(words_freq[0][0]) == 0:
    return

  guess = calculate_optimal_guess(word_length, words_freq)

  pattern = pattern_checker_func(guess)

  if pattern == 0:
    print(f'guess: {guess} x incorrect')
  else:
    print(f'guess: {guess}')

  words_freq = filter_and_update_word_freq_list(guess, pattern, words_freq, word_length)

  new_word_length = len(words_freq[0][0])

  smaller_answer = _play(
    create_new_pattern_checker_func(
      pattern_checker_func,
      pattern,
      word_length
    ),
    new_word_length,
    words_freq
  )

  full_answer = ""

  j = 0
  for i in range(word_length):
    pattern_bit = (pattern >> i) & 1
    if pattern_bit == 1:
      full_answer = guess + full_answer
    else:
      full_answer = smaller_answer[new_word_length - j - 1] + full_answer
      j += 1

  return full_answer

def play(pattern_checker_func, word_length):
  return _play(pattern_checker_func, word_length, WORDS_FREQ)

def main():
  word = sys.argv[1]

  if word == "":
    print("no word provided")
    return

  

  print(play(lambda guess : get_pattern(guess, word), len(word)))

main()
