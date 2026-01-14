def main():
    import warnings
    warnings.warn(
        "DIAAD has been renamed to TAAALCR. "
        "Please install and use the 'taaalcr' package instead.",
        DeprecationWarning,
    )
    print(
        "DIAAD is deprecated.\n"
        "See: https://github.com/nmccloskey/TAAALCR"
    )
