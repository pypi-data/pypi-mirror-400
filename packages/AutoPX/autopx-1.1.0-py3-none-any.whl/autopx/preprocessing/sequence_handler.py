from autopx.utils.constants import ModelType

# TensorFlow imports with fallback
try:
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from tensorflow.keras.preprocessing.text import Tokenizer
except ImportError:
    # Minimal mock
    def pad_sequences(sequences, maxlen=None, padding='post', truncating='post'):
        return sequences

    class Tokenizer:
        def __init__(self, **kwargs): pass
        def fit_on_texts(self, texts): pass
        def texts_to_sequences(self, texts): 
            return [list(range(len(t.split()))) for t in texts]

class SequenceHandler:
    """
    Handles sequence preparation for deep learning and transformer models.
    """

    def __init__(self, max_len: int = None, oov_token: str = "<OOV>"):
        self.max_len = max_len
        self.tokenizer = Tokenizer(oov_token=oov_token)

    def fit_tokenizer(self, texts: list[str]):
        self.tokenizer.fit_on_texts(texts)
        return self

    def texts_to_sequences(self, texts: list[str]) -> list[list[int]]:
        return self.tokenizer.texts_to_sequences(texts)

    def pad_sequences(self, sequences: list[list[int]], padding='post', truncating='post') -> list[list[int]]:
        if not self.max_len:
            self.max_len = max(len(seq) for seq in sequences) if sequences else 0
        return pad_sequences(sequences, maxlen=self.max_len, padding=padding, truncating=truncating)

    def fit_transform(self, texts: list[str]) -> list[list[int]]:
        self.fit_tokenizer(texts)
        sequences = self.texts_to_sequences(texts)
        padded = self.pad_sequences(sequences)
        return padded
