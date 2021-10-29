from util import remove_dup

def test_remove_dup():
    d = [1, 2, 3, 3, 3, 4, 5, 4, 5, 6, 7, 7]
    assert remove_dup(d) == [1, 2, 3, 4, 5, 6, 7]
