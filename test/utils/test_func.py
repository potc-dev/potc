from functools import wraps

import pytest

from potc.utils import args_iter, dynamic_call, static_call, post_process, pre_process, freduce, raising, warning_


@pytest.mark.unittest
class TestUtilsFunc:
    def test_args_iter(self):
        assert list(args_iter(1, 2, 3, a=1, c=3, b=4)) == [(0, 1), (1, 2), (2, 3), ('a', 1), ('b', 4), ('c', 3)]

    def test_dynamic_call(self):
        assert dynamic_call(lambda x, y: x ** y)(2, 3) == 8
        assert dynamic_call(lambda x, y: x ** y)(2, 3, 4) == 8
        assert dynamic_call(lambda x, y, t, *args: (args, (t, x, y)))(1, 2, 3, 4, 5) == ((4, 5), (3, 1, 2))
        assert dynamic_call(lambda x, y: (x, y))(y=2, x=1) == (1, 2)
        assert dynamic_call(lambda x, y, **kwargs: (kwargs, x, y))(1, k=2, y=3) == ({'k': 2}, 1, 3)
        assert dynamic_call(lambda x, y, *args, t=2, v=4, **kwargs: (args, kwargs, x, y, t, v))(1, 2, 3, 4, p=5, v=7) \
               == ((3, 4), {'p': 5}, 1, 2, 2, 7)

    def __get_wrapped_function(self):
        def _wrapper(func):
            @wraps(func)
            def _new_func(*args):
                return func(sum(args))

            return _new_func

        @dynamic_call
        @dynamic_call
        @_wrapper
        def f(x):
            return x ** x

        return f

    def test_dynamic_call_nested_with_wrapper(self):
        f = self.__get_wrapped_function()
        assert f(1, 2, 3, 4) == 10 ** 10

    def test_static_call(self):
        f = self.__get_wrapped_function()
        f = static_call(f, static_ok=False).__wrapped__
        assert f(2) == 4
        with pytest.raises(TypeError):
            _ = f(1, 2, 3, 4)

        def another_f(x):
            return x ** x

        with pytest.raises(TypeError):
            _ = static_call(another_f, static_ok=False)

    def test_pre_process(self):
        @pre_process(lambda x, y: (-x, (x + 2) * y))
        def plus(a, b):
            return a + b

        assert plus(1, 2) == 5

        @pre_process(lambda x, y: ((), {'a': -x, 'b': (x + 2) * y}))
        def plus2(a, b):
            return a + b

        assert plus2(1, 2) == 5

        @pre_process(lambda x, y: {'a': -x, 'b': (x + 2) * y})
        def plus3(a, b):
            return a + b

        assert plus3(1, 2) == 5

        @pre_process(lambda x, y: ((-x, -x + 1, -x + 2), (y, y + 1, y + 2)))
        def plus4(a, b):
            return a + b

        assert plus4(1, 2) == (-1, 0, 1, 2, 3, 4)

        @pre_process(lambda x: -x)
        def pw(a):
            return a ** a

        assert pw(-3) == 27

    def test_post_process(self):
        @post_process(lambda x: -x)
        def plus(a, b):
            return a + b

        assert plus(1, 2) == -3

        @post_process(lambda: None)
        def plus2(a, b):
            return a + b

        assert plus2(1, 2) is None

    def test_freduce(self):
        @freduce(init=lambda neg=False: 1 if neg else 0)
        def plus(a, b, neg: bool = False):
            return a + b if not neg else a * b

        assert plus() == 0
        assert plus(1) == 1
        assert plus(1, 2) == 3
        assert plus(1, 2, 3, 4, 5) == 15
        assert plus(1, 2, 3, 4, neg=True) == 24

        @freduce()
        def plus2(a, b, neg: bool = False):
            return a + b if not neg else a * b

        with pytest.raises(SyntaxError):
            _ = plus2()
        assert plus2(1) == 1
        assert plus2(1, 2) == 3
        assert plus2(1, 2, 3, 4, 5) == 15
        assert plus2(1, 2, 3, 4, neg=True) == 24

        @freduce(init=lambda neg=False: 1 if neg else 0, pass_kwargs=False)
        def plus3(a, b, neg: bool = False):
            return a + b if not neg else a * b

        assert plus3() == 0
        assert plus3(1) == 1
        assert plus3(1, 2) == 3
        assert plus3(1, 2, 3, 4, 5) == 15
        with pytest.warns(SyntaxWarning):
            assert plus3(1, 2, 3, 4, neg=True) == 10

    def test_raising(self):
        f1 = raising(lambda: RuntimeError)
        f2 = raising(RuntimeError)
        f3 = raising(RuntimeError())
        with pytest.raises(RuntimeError):
            f1()
        with pytest.raises(RuntimeError):
            f2()
        with pytest.raises(RuntimeError):
            f3()

        f4 = raising(lambda x: RuntimeError if x < 0 else x)
        assert f4(0) == 0
        assert f4(1) == 1
        with pytest.raises(RuntimeError):
            f4(-1)

    def test_warning(self):
        f1 = warning_(lambda: RuntimeWarning)
        f2 = warning_(RuntimeWarning)
        f3 = warning_(RuntimeWarning())
        f4 = warning_('warning')
        with pytest.warns(RuntimeWarning):
            f1()
        with pytest.warns(RuntimeWarning):
            f2()
        with pytest.warns(RuntimeWarning):
            f3()
        with pytest.warns(UserWarning):
            f4()

        f5 = warning_(lambda x: RuntimeWarning if x < 0 else x)
        with pytest.warns(None):
            f5(1)
        with pytest.warns(RuntimeWarning):
            f5(-1)

        f6 = warning_(lambda x: (RuntimeWarning, (), {}) if x < 0 else x)
        with pytest.warns(None):
            f6(1)
        with pytest.warns(RuntimeWarning):
            f6(-1)

        f7 = warning_(lambda x: (RuntimeWarning, ()) if x < 0 else x)
        with pytest.warns(None):
            f7(1)
        with pytest.warns(RuntimeWarning):
            f7(-1)

        f8 = warning_(lambda x: (RuntimeWarning, {}) if x < 0 else x)
        with pytest.warns(None):
            f8(1)
        with pytest.warns(RuntimeWarning):
            f8(-1)