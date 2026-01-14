import re
from collections.abc import Iterable
from itertools import chain

import regex
import torch
from transformers import PreTrainedTokenizer, StoppingCriteria, add_start_docstrings
from transformers.generation.stopping_criteria import STOPPING_CRITERIA_INPUTS_DOCSTRING
from utf8_tokenizer.control import CONTROl_TOKENS_PATTERN

from words_segmentation.languages import segment_text

_COMPILED_GRAPHEME_PATTERN = regex.compile(r"\X")
_COMPLETE_WORD_PATTERNS = [
    rf"[{CONTROl_TOKENS_PATTERN}]",  # Control tokens are always complete
    rf"[^\s{CONTROl_TOKENS_PATTERN}]+\s",  # Words with trailing space are complete
]


def words_to_text(words: Iterable[str]) -> str:
    return ''.join(words)


def text_to_words(text: str, max_bytes: int = None, max_characters: int = None) -> list[str]:
    words = chain.from_iterable(segment_text(text))

    # max_bytes and max_characters are mutually exclusive
    if max_bytes is not None and max_characters is not None:
        raise ValueError("max_bytes and max_characters are mutually exclusive")

    if max_bytes is None and max_characters is None:
        return list(words)

    if max_characters is not None:
        chunks = (character_chunks(word, max_characters=max_characters) for word in words)
    else:
        chunks = (utf8_chunks_grapheme_safe(word, max_bytes=max_bytes) for word in words)
    return list(chain.from_iterable(chunks))

def character_chunks(text: str, max_characters: int) -> Iterable[str]:
    """
    Split a string into chunks of at most max_characters characters.
    """
    if len(text) <= max_characters:
        yield text
        return

    start = 0
    while start < len(text):
        end = start + max_characters
        yield text[start:end]
        start = end

def utf8_chunks_grapheme_safe(text: str, max_bytes: int = 16) -> Iterable[str]:
    """
    Split a string into chunks of at most max_bytes bytes, without splitting grapheme clusters.
    Except, if there is a single grapheme cluster longer than max_bytes, it will be in its own chunk. 👩‍👩‍👧‍👦
    """
    text_bytes = text.encode("utf-8")
    if len(text_bytes) <= max_bytes:
        yield text
        return

    clusters = _COMPILED_GRAPHEME_PATTERN.findall(text)
    if len(clusters) == 1:
        yield text
        return

    curr = []
    curr_bytes = 0
    for cluster in clusters:
        cluster_bytes = len(cluster.encode("utf-8"))
        if curr_bytes + cluster_bytes > max_bytes:
            if curr:
                yield "".join(curr)
            curr = [cluster]
            curr_bytes = cluster_bytes
        else:
            curr.append(cluster)
            curr_bytes += cluster_bytes
    if curr:
        yield "".join(curr)


def is_word_complete(text: str) -> bool:
    for pattern in _COMPLETE_WORD_PATTERNS:
        if re.fullmatch(pattern, text):
            return True

    # TODO: not clear how to know if a word full of whitespaces is complete
    #       maybe if _TOKEN_PATTERN is not a full match, but then need to "delete" the last token.
    return False


class WordStoppingCriteria(StoppingCriteria):
    def __init__(self, tokenizer: PreTrainedTokenizer):
        self.tokenizer = tokenizer

    @add_start_docstrings(STOPPING_CRITERIA_INPUTS_DOCSTRING)
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> torch.BoolTensor:
        # TODO: we can check directly the input_ids without decoding, for better performance
        #       specifically, if the last non-padding token is a control token
        #       or if it is a space, preceded by non-space token, then the word is complete
        texts = self.tokenizer.batch_decode(input_ids.tolist())
        is_done = [is_word_complete(text) for text in texts]
        return torch.tensor(is_done, dtype=torch.bool, device=input_ids.device)

