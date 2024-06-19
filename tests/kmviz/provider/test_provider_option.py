import pytest
from kmviz.ui.components.option import make_user_option, make_callback, make_select_data
from kmviz.core.provider.options import NumericOption, TextOption, RangeOption, ChoiceOption, MultiChoiceOption
from dash import dcc, Patch

class TestProviderOptions:
    
    def test_numeric_option(self):
        opt = NumericOption("numeric", 1, 0, 5, 1)
        assert opt.name == "numeric"
        assert opt.default == 1
        assert opt.min == 0
        assert opt.max == 5
        assert opt.step == 1
        
        dmc_opt = make_user_option(opt, "numeric_option_test_id")
        dmc_props = { 
            "id": "numeric_option_test_id",
            "min": 0, "max": 5, "step": 1, "value": 1,
            "precision": 2, "label": "numeric",
            "className": "kmviz-dmc-number-input"
        }
        assert dmc_opt.to_plotly_json()["props"] == dmc_props

    def test_range_option(self):
        opt = RangeOption("range", 1, 0, 5, 1)
        assert opt.name == "range"
        assert opt.default == 1
        assert opt.min == 0
        assert opt.max == 5
        assert opt.step == 1
        
        dmc_opt = make_user_option(opt, "range_option_test_id").children[1]
        dmc_props = { 
            "id": "range_option_test_id",
            "min": 0, "max": 5, "step": 1, "value": 1,
            "precision": 2, "updatemode": "mouseup",
            "className": "kmviz-dmc-slider",
        }
        assert dmc_opt.to_plotly_json()["props"] == dmc_props

    def test_text_option(self):
        opt = TextOption("text", "def", "placeholder")
        assert opt.name == "text"
        assert opt.default == "def"
        assert opt.placeholder == "placeholder"
        
        dmc_opt = make_user_option(opt, "text_option_test_id")
        dmc_props = { 
            "id": "text_option_test_id",
            "value": "def", "label": "text", "placeholder": "placeholder",
            "className": "kmviz-dmc-text-input"
        }
        assert dmc_opt.to_plotly_json()["props"] == dmc_props

    def test_choice_option(self):
        opt = ChoiceOption("choice", None, [1, 2, 3])
        assert opt.name == "choice"
        assert opt.default == None
        assert opt.choices == [1, 2, 3]
        
        dmc_opt = make_user_option(opt, "choice_option_test_id")
        dmc_props = { 
            "id": "choice_option_test_id",
            "value": None, "label": "choice",
            "className": "kmviz-dmc-select", 
            "clearable": True, "searchable": True,
            "data": make_select_data([1, 2, 3])
        }
        assert dmc_opt.to_plotly_json()["props"] == dmc_props

    def test_multichoice_option(self):
        opt = MultiChoiceOption("multi", None, [1, 2, 3])
        assert opt.name == "multi"
        assert opt.default == None
        assert opt.choices == [1, 2, 3]
        
        dmc_opt = make_user_option(opt, "multichoice_option_test_id")
        dmc_props = { 
            "id": "multichoice_option_test_id",
            "value": None, "label": "multi",
            "className": "kmviz-dmc-multi-select", 
            "clearable": True, "searchable": True,
            "data": make_select_data([1, 2, 3])
        }
        assert dmc_opt.to_plotly_json()["props"] == dmc_props

    def test_callback_option(self):
        opt = TextOption("text", "def", "placeholder")
        dmc_opt = make_user_option(opt, "input_id")
        call = make_callback("name", "opt_name", "input_id", "output_id")
        patch = call("text_value")
        assert isinstance(patch, Patch)
        res = {"location": ["name", "opt_name"], "operation": "Assign", "params": {"value": "text_value"}}
        assert patch.to_plotly_json()["operations"][0] == res