def notion_prop(name: str):
    """
    クラスデコレータ: PROP_NAME を自動的に設定する。
    """

    def decorator(cls):
        # クラスに PROP_NAME を設定
        setattr(cls, "PROP_NAME", name)
        return cls

    return decorator
