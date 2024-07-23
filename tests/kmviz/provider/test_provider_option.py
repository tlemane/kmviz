import pytest
from kmviz.ui.components.option import make_user_option, make_select_data
from kmviz.core.provider.options import NumericOption, TextOption, RangeOption, ChoiceOption, MultiChoiceOption
from dash_extensions.enrich import dcc, callback, Input, Output
from dash import Patch

def make_callback_f(name, opt_name):
    def update(value):
        patch = Patch()
        patch[name][opt_name] = value
        return patch
    return update

def make_callback(name, opt_name, input_id, output_id):
    return callback(
        Input(input_id, "value"),
        Output(output_id, "data"),
        prevent_initial_call=True
    )(make_callback_f(name, opt_name))

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
            "className": "kmviz-dmc-user-number-input",
            "classNames": { 'root': "kmviz-dmc-numeric-input-root" }
        }
        assert dmc_opt.to_plotly_json()["props"] == dmc_props

    def test_range_option(self):
        opt = RangeOption("range", 1, 0, 5, 1)
        assert opt.name == "range"
        assert opt.default == 1
        assert opt.min == 0
        assert opt.max == 5
        assert opt.step == 1

        dmc_opt = make_user_option(opt, {"type": "range-option-test", "index": "id"}).children[1]
        dmc_props = {
            "id": {"type": "range-option-test", "index": "id"},
            "min": 0, "max": 5, "step": 1, "value": 1,
            "precision": 2, "updatemode": "mouseup",
            "className": "kmviz-dmc-user-slider",
            "marks": [
                {"value": opt.min, "label": str(round(opt.min, 2))},
                {"value": opt.max, "label": str(round(opt.max, 2))},
            ],
            "size": "sm"
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
            "className": "kmviz-dmc-user-text-input",
            "classNames": { 'root': "kmviz-dmc-text-input-root" },
            "size":"xs"
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
            "className": "kmviz-dmc-user-select",
            "clearable": True, "searchable": True,
            "data": make_select_data([1, 2, 3]),
            "classNames": { 'root': "kmviz-dmc-select-input-root" },
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
            "className": "kmviz-dmc-user-multi-select",
            "clearable": True, "searchable": True,
            "data": make_select_data([1, 2, 3]),
            "classNames": { 'root': "kmviz-dmc-select-input-root" },
            "size":"xs"
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