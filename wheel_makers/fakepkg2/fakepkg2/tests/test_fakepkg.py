from ..module1 import func1
from ..subpkg.module2 import func2, func3


def test_fakepkg():
    assert func1() == 1
    assert func2() == 2
    assert func3() == 3
