import datasets

DATASET_ID = "ucirvine/sms_spam"


def load_sms_spam(test_size=0.2, seed=42):
    """SMS 데이터를 train/validation으로 나눠 반환한다."""

    ds = datasets.load_dataset(DATASET_ID, split="train")

    # 원본에는 train split 하나만 있으므로 직접 분리
    split = ds.train_test_split(
        test_size=test_size,
        seed=seed,
        stratify_by_column="label"
    )

    train = split["train"]
    val = split["test"]

    return train, val


if __name__ == "__main__":
    train, val = load_sms_spam()

    print(f"train: {len(train)}개")
    print(f"validation: {len(val)}개")
    print(train[0])


