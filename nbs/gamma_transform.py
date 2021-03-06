
import tensorflow as tf
import tensorflow_transform as tft
import nltk
import gamma_constants

sequence_length = 618
key = "sentence"

_VOCAB_FEATURE_KEYS = gamma_constants.VOCAB_FEATURE_KEYS
_VOCAB_SIZE = gamma_constants.VOCAB_SIZE
_OOV_SIZE = gamma_constants.OOV_SIZE
_LABEL_KEY = gamma_constants.LABEL_KEY
_transformed_name = gamma_constants.transformed_name

def process_sentence(sentences):
    sentences = tf.strings.lower(sentences)
    sentences = tf.strings.regex_replace(sentences, r" '| '|^'|'$", " ")
    sentences = tf.strings.regex_replace(sentences,"\n","")
    nums = '0123456789'
    for item in nums:
        sentences = tf.strings.regex_replace(sentences, item, "")
    for item in '"#$%&,-/:;<=>@_`|~:'+ "'":
        sentences = tf.strings.regex_replace(sentences,item,"")
    for item in "()*+?[][]{}^\!":
        sentences = tf.strings.regex_replace(sentences,"\\" + item,"")
    sentences = tf.strings.regex_replace(sentences,"\\.","")
    
    stop_words = nltk.corpus.stopwords.words('english')
    for word in stop_words:
        sentences = tf.strings.regex_replace(sentences,r"\\b"+word+"\\b","")
    sentences = tf.strings.strip(sentences)
    return sentences

def tokenize(sentences):
    sentences = process_sentence(sentences)
    start_tokens = tf.fill([tf.shape(sentences)[0], 1], "<START>")
    tokens = tf.strings.split(sentences)[:, :sequence_length]
    end_tokens = tf.fill([tf.shape(sentences)[0], 1], "<END>")
    tokens = tf.concat([start_tokens, tokens, end_tokens], axis=1)
    tokens = tokens[:, :sequence_length]
    tokens = tokens.to_tensor(default_value="<PAD>")
    pad = sequence_length - tf.shape(tokens)[1]
    tokens = tf.pad(tokens, [[0, 0], [0, pad]], constant_values="<PAD>")
    return tf.reshape(tokens, [-1, sequence_length])


def preprocessing_fn(inputs):
  """tf.transform's callback function for preprocessing inputs.
  Args:
    inputs: map from feature keys to raw not-yet-transformed features.
  Returns:
    Map from string feature key to transformed feature operations.
  """
  outputs = {}
  #outputs["senteces_processed"] = process_sentence(_fill_in_missing(inputs["sentence"]))
  #for key in _VOCAB_FEATURE_KEYS:
    # Build a vocabulary for this feature.
    #outputs[_transformed_name(key)] = tft.compute_and_apply_vocabulary(
        #_fill_in_missing(inputs[key]),
        #top_k=_VOCAB_SIZE,
        #num_oov_buckets=_OOV_SIZE)

  
  tokens = tokenize(_fill_in_missing(inputs["sentence"]))
  #Build a vocabulary for this feature.
  outputs[_transformed_name(key)] = tft.compute_and_apply_vocabulary(
    tokens,
    top_k=_VOCAB_SIZE,
    num_oov_buckets=_OOV_SIZE,
  )
  outputs[_transformed_name(_LABEL_KEY)] = _fill_in_missing(inputs[_LABEL_KEY])
  tft.vocabulary(tokens, vocab_filename="sentence_key")
  return outputs


def _fill_in_missing(x):
  """Replace missing values in a SparseTensor.
  Fills in missing values of `x` with '' or 0, and converts to a dense tensor.
  Args:
    x: A `SparseTensor` of rank 2.  Its dense shape should have size at most 1
      in the second dimension.
  Returns:
    A rank 1 tensor where missing values of `x` have been filled in.
  """
  default_value = '' if x.dtype == tf.string else 0
  return tf.squeeze(
      tf.sparse.to_dense(
          tf.SparseTensor(x.indices, x.values, [x.dense_shape[0], 1]),
          default_value),
      axis=1)
