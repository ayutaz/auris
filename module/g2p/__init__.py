from typing import List, Union, Tuple
import torch

from .japanese import JapaneseExtractor
#from .english import EnglishExtractor


class G2PProcessor:
    def __init__(self):
        self.extractors = {}

        # If you want to add a language, add processing here
        # ---
        self.extractors['ja'] = JapaneseExtractor()
        #self.extractors['en'] = EnglishExtractor()
        # ---

        self.languages = []
        phoneme_vocabs = []
        for mod in self.extractors.values():
            phoneme_vocabs += mod.possible_phonemes()
        self.languages += self.extractors.keys()
        self.phoneme_vocabs = ['<pad>'] + phoneme_vocabs

    def grapheme_to_phoneme(self, text: Union[str, List[str]], language: Union[str, List[str]]):
        if type(text) == list:
            return self._g2p_multiple(text, language)
        elif type(text) == str:
            return self._g2p_single(text, language)

    def _g2p_single(self, text, language):
        mod = self.extractors[language]
        return mod.g2p(text)

    def _g2p_multiple(self, text, language):
        result = []
        for t, l in zip(text, language):
            result.append(self._g2p_single(t, l))
        return result

    def phoneme_to_id(self, phonemes: Union[List[str], List[List[str]]]):
        if type(phonemes[0]) == list:
            return self._p2id_multiple(phonemes)
        elif type(phonemes[0]) == str:
            return self._p2id_single(phonemes)

    def _p2id_single(self, phonemes: List[str]):
        ids = []
        for p in phonemes:
            if p in self.phoneme_vocabs:
                ids.append(self.phoneme_vocabs.index(p))
            else:
                print("warning: unknown phoneme.")
                ids.append(0)
        return ids

    def _p2id_multiple(self, phonemes: List[List[str]]):
        sequences = []
        for s in phonemes:
            out = self._p2id_single(s)
            sequences.append(out)
        return sequences

    def language_to_id(self, languages: Union[str, List[str]]):
        if type(languages) == str:
            return self._l2id_single(languages)
        elif type(languages) == list:
            return self._l2id_multiple(languages)

    def _l2id_single(self, language):
        if language in self.languages:
            return self.languages.index(language)
        else:
            return 0

    def _l2id_multiple(self, languages):
        result = []
        for l in languages:
            result.append(self._l2id_single(l))
        return result

    def id_to_phoneme(self, ids):
        if type(ids[0]) == list:
            return self._id2p_multiple(ids)
        elif type(ids[0]) == int:
            return self._id2p_single(ids)

    def _id2p_single(self, ids: List[int]) -> List[str]:
        phonemes = []
        for i in ids:
            if i < len(self.phoneme_vocabs):
                p = self.phoneme_vocabs[i]
            else:
                p = '<pad>'
            phonemes.append(p)
        return phonemes

    def _id2p_multiple(self, ids: List[List[int]]) -> List[List[str]]:
        results = []
        for s in ids:
            results.append(self._id2p_single(s))
        return results

    def encode(self, sentences: List[str], languages: List[str], max_length: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        ids, lengths = self._enc_multiple(sentences, languages, max_length)
        language_ids = self.language_to_id(languages)

        ids = torch.LongTensor(ids)
        lengths = torch.LongTensor(lengths)
        language_ids = torch.LongTensor(language_ids)

        return ids, lengths, language_ids
    
    def _enc_single(self, sentence, language, max_length):
        phonemes = self.grapheme_to_phoneme(sentence, language)
        ids = self.phoneme_to_id(phonemes)
        length = min(len(ids), max_length)
        if len(ids) > max_length:
            ids = ids[:max_length]
        while len(ids) < max_length:
            ids.append(0)
        return ids, length
    
    def _enc_multiple(self, sentences, languages, max_length):
        seq, lengths = [], []
        for s, l in zip(sentences, languages):
            ids, length = self._enc_single(s, l, max_length)
            seq.append(ids)
            lengths.append(length)
        return seq, lengths

