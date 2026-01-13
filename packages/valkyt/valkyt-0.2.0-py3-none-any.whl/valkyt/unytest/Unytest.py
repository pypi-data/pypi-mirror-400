import unittest

class Unytest:
    def __init__(self):
        self.unytestCase = unittest.TestCase()
        self.asyncUnytestCase = unittest.IsolatedAsyncioTestCase()
        ...
        
    def __view(
        self,
        assert_func,
        *args,
        message: str = "",
        context: str = "",
        bot = None,
        **kwargs
    ) -> None:
        try:
            assert_func(*args)
            self.__log.debug(f"[ PASS ] {message} :: {context}")
        except AssertionError as e:
            self.__log.error(f"[ FAIL ] {message} :: {context} -- {e}")
            if bot:
                bot(**kwargs)