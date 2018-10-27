from ..module1 import func1
from ..subpkg.module2 import func2, func3


def test_fakepkg():
    func1() == 1
    func2() == 2
    func3() == 3
