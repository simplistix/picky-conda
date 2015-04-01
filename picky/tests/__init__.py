import os


def sample_output_path(filename):
    return os.path.join(
        os.path.dirname(__file__),
        'sample_output',
        filename
    )