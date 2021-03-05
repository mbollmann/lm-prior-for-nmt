import collections
import functools
import hashlib
import inspect
import os
import pickle
import random
from subprocess import check_output

import numpy
from matplotlib import pyplot as plt
from tqdm import tqdm

from modules.data.vocab import Vocab
from sys_config import BASE_DIR


def vectorize(tokens, vocab, oovs=0, return_map=False):
    """
    Covert array of tokens, to array of ids
    Args:
        tokens (list): list of tokens
        vocab (Vocab):
    Returns:  list of ids
    """
    ids = []
    oov2tok = {}
    tok2oov = {}
    for token in tokens:

        # if token in the vocabulary, add its token id
        if token in vocab.tok2id:
            ids.append(vocab.tok2id[token])

        # if an OOV token has already been encountered, use its token_id
        elif token in tok2oov:
            ids.append(vocab.tok2id[tok2oov[token]])

        # if this is a new OOV token, add it to oov2tok and use its token_id
        elif oovs > len(oov2tok):
            _oov = f"<oov-{len(oov2tok)}>"
            ids.append(vocab.tok2id[_oov])
            oov2tok[_oov] = token
            tok2oov[token] = _oov

        # if the OOV token exceed our limit, use the generic UNK token
        else:
            ids.append(vocab.tok2id[vocab.UNK])
    if oovs > 0 and return_map:
        return ids, oov2tok
    else:
        return ids


def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])


def args_to_str(args):
    _str = []
    for x in args:
        if callable(x):
            _str.append(inspect.getsource(x))
        else:
            _str.append(str(x))
    return _str


def disk_memoize(func):
    cache_dir = os.path.join(BASE_DIR, "_cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # check fn arguments
        args_str = ''.join(args_to_str(args))
        key = hashlib.md5(args_str.encode()).hexdigest()
        cache_file = os.path.join(cache_dir, key)

        if os.path.exists(cache_file):
            print(f"Loading {cache_file} from cache!")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        else:
            print(f"No cache file for {cache_file}...")
            data = func(*args, **kwargs)

            with open(cache_file, 'wb') as pickle_file:
                pickle.dump(data, pickle_file)

            return data

    return wrapper_decorator


def iterate_data(data):
    if isinstance(data, str):
        assert os.path.exists(data), f"path `{data}` does not exist!"
        with open(data, "r") as f:
            for line in tqdm(f, total=wc(data), desc=f"Reading {data}..."):
                if len(line.strip()) > 0:
                    yield line

    elif isinstance(data, collections.Iterable):
        for x in data:
            yield x


def fix_paths(path, separator):
    # root = BASE_DIR.split(os.sep)[-1]
    # base_a = path.split(root)[0]
    # base_b = os.path.dirname(os.path.realpath(__file__)).split(root)[0]
    # return path.replace(base_a, base_b)

    if len(path.split(separator)) > 0:
        return os.path.join(BASE_DIR, separator,
                            path.split(separator + os.sep)[-1])
    else:
        return path


# @disk_memoize
def read_corpus(file, tokenize):
    _vocab = Vocab()

    _data = []
    for line in iterate_data(file):
        tokens = tokenize(line)
        _vocab.read_sequence(tokens)
        _data.append(tokens)

    return _vocab, _data


# @disk_memoize
def build_vocab_from_file(file, tokenize):
    _vocab = Vocab()

    for line in iterate_data(file):
        tokens = tokenize(line)
        _vocab.read_sequence(tokens)

    return _vocab


def hist_dataset(data, seq_len):
    lengths = [len(x) for x in data]
    plt.hist(lengths, density=1, bins=20)
    plt.axvline(seq_len, color='k', linestyle='dashed', linewidth=1)
    plt.show()


def coverage(vocab, top_n):
    occurrences = [freq for tok, freq in vocab.most_common()]
    total = sum(occurrences)
    cov = sum(occurrences[:top_n]) / total
    return cov


def unks_per_sample(keys, data):
    known = set(keys)
    _coverage = [len(set(x) - known) / len(x) for x in data]
    return numpy.mean(_coverage) * 100


def token_shuffle(words, factor):
    words = list(words)
    length = len(words)
    shuffles = int(length * factor)

    if len(words) < 5:
        return words

    for i in range(shuffles):
        i, j = tuple(int(random.random() * length) for i in range(2))
        words[i], words[j] = words[j], words[i]
    return words


def token_swaps(words, factor):
    if not factor > 0:
        return words

    words = list(words)
    length = len(words)
    shuffles = int(length * factor)

    if len(words) < 4:
        return words

    for it in range(shuffles):
        j = random.randint(0, length - 2)
        words[j], words[j + 1] = words[j + 1], words[j]

    return words
