import os


def fixture_path(file_name):
    return os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            file_name
        )
    )
