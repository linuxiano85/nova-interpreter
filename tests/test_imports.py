def test_import_nova_prime_package():
    import nova_prime  # noqa: F401

def test_import_core_modules():
    from nova_prime.voice import hotword, stt, tts  # noqa: F401
    from nova_prime.services import apps, steam     # noqa: F401
    from nova_prime.modes import companion         # noqa: F401