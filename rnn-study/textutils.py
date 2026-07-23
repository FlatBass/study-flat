"""
공용 도구 — 어제(Day 2) 만든 것을 그대로 가져오고, 오늘 필요한 것만 더했다.

    from textutils import tokenize_en, build_vocab, encode, pad_and_tensor

[어제에서 온 것 — 그대로]
  build_vocab · encode · decode
  → 사전을 만들고 정수로 바꾸는 일은 **언어와 무관하다.** 어제는 한국어였지만
    오늘 영어에도 똑같은 코드가 돈다. 이 재사용성 자체가 어제 배운 것이다.

[오늘 더한 것]
  tokenize_en   — 영어 토큰화 (어제 kiwi 자리를, 영어라 정규식으로)
  build_vocab 의 max_size — 상위 N개 단어만 남기는 인자 (어제는 min_freq만 있었다)
  pad_and_tensor — 길이를 맞춰 텐서로. RNN을 위해 **앞쪽**에 채운다 (이유는 05_train)

한 번 이해한 것은 함수로 묶어 두고 다음 개념(RNN)에 집중한다 — 어제와 같은 원칙.
"""

import re
from collections import Counter

import torch

PAD, UNK = "<pad>", "<unk>"
PAD_IDX, UNK_IDX = 0, 1


def tokenize_en(text):
    """영어 문장 → 소문자 단어 리스트.

    어제 본 문제 그대로다: `don't`·`good.`처럼 붙은 구두점을 떼야 한다.
    오늘은 **알파벳 덩어리만** 뽑는 정규식으로 간단히 처리한다.
    (한국어가 아니므로 kiwi 형태소 분석은 쓰지 않는다 — 토큰화 방법만 언어에 맞춰 바꾸고,
     그 뒤의 사전·인코딩·패딩은 어제 코드를 그대로 쓴다.)
    """
    return re.findall(r"[a-z]+", text.lower())


def build_vocab(token_lists, max_size=None, min_freq=1):
    """토큰 리스트들 → word2idx 사전.  (어제 코드 + max_size 인자)

    0번은 <pad>, 1번은 <unk> 로 **미리 예약**한다 (어제 배운 그대로).
    나머지는 많이 나온 순서대로 2, 3, 4… 를 받는다.

    max_size: 상위 몇 개 단어까지만 넣을지. None이면 전부.
              어휘가 너무 크면 임베딩 표도 커지므로, 자주 나온 단어만 남긴다.
    min_freq: 최소 등장 횟수 (어제 배운 트레이드오프 — 올리면 <unk>가 는다).
    """
    counter = Counter(tok for tokens in token_lists for tok in tokens)
    word2idx = {PAD: PAD_IDX, UNK: UNK_IDX}
    for word, freq in counter.most_common(max_size - 2):   # max_size=None이면 전부
        if freq >= min_freq:
            word2idx[word] = len(word2idx)
    return word2idx, counter


def encode(tokens, word2idx):
    """토큰 리스트 → 인덱스 리스트. 사전에 없는 단어는 <unk>(1).  (어제 그대로)"""
    return [word2idx.get(tok, UNK_IDX) for tok in tokens]


def decode(indices, word2idx):
    """인덱스 리스트 → 토큰 리스트. 확인용.  (어제 그대로)"""
    idx2word = {i: w for w, i in word2idx.items()}
    return [idx2word.get(i, "?") for i in indices]


def pad_and_tensor(token_lists, word2idx, max_len):
    """인코딩 → 길이 맞추기 → (batch, max_len) 텐서.

    두 가지가 어제와 다르다. 이유는 05_train.py 에서 **직접 실측으로** 확인한다.

      1) 긴 문장은 **뒤쪽 max_len개**만 남긴다 (앞을 버린다).
      2) 짧은 문장은 **앞쪽**에 <pad>(0)를 채운다 (뒤가 아니라).

    왜 하필 이렇게? RNN은 문장을 앞에서 뒤로 읽고 **마지막 은닉 상태**로 판단한다.
    만약 뒤쪽에 <pad>를 잔뜩 붙이면, 정작 볼 내용을 다 읽은 뒤 빈칸만 계속 읽다가
    끝나서 마지막 요약이 흐려진다. 그래서 실제 내용이 **맨 뒤에 오도록** 앞쪽을 채운다.
    """
    rows = []
    for tokens in token_lists:
        ids = encode(tokens, word2idx)[-max_len:]          # 뒤 max_len개만 (앞을 자름)
        ids = [PAD_IDX] * (max_len - len(ids)) + ids        # 앞쪽 패딩
        rows.append(ids)
    return torch.tensor(rows)
