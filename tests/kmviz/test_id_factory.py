import pytest
from kmviz.ui.id_factory import IDFactory

class TestIDFactory:
    @pytest.fixture(scope="class")
    def factory(self):
        return IDFactory("main")
    
    def test_string_id(self, factory):
        assert factory.sid("child") == "main-child"

    def test_dict_id(self, factory):
        assert factory("child") == {"index": "child", "type": "main"}

    def test_child(self, factory):
        c = factory.child("child")
        assert c.sid("test") == "main-child-test"
        assert c("test") == {"index": "test", "type": "main-child"}