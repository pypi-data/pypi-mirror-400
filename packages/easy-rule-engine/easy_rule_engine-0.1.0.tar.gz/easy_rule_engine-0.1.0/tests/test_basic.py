import unittest

from easy_rule_engine import Rule, RuleEngine, attr_spec, attr_transform, dict_setter


class TestEasyRuleEngine(unittest.TestCase):
    def test_transform_and_keep_unmatched(self) -> None:
        items = [
            {"age": 15, "status": "UNKNOWN"},
            {"age": 20, "status": "OK"},
        ]

        get_age = lambda x: x["age"]
        get_status = lambda x: x["status"]

        is_minor = attr_spec(get_age, lambda v: v < 18)
        set_minor = attr_transform(
            getter=get_status,
            setter=dict_setter("status"),
            value_func=lambda _old: "MINOR",
        )

        engine = RuleEngine(
            rules=[Rule(condition=is_minor, transform=set_minor)],
            keep_unmatched=True,
            match_mode="all",
        )

        out = engine.process(items)
        self.assertEqual(out[0]["status"], "MINOR")
        self.assertEqual(out[1]["status"], "OK")

    def test_match_mode_first_stops(self) -> None:
        items = [{"x": 0}]
        get_x = lambda i: i["x"]

        always = attr_spec(get_x, lambda _v: True)
        inc = attr_transform(get_x, dict_setter("x"), lambda v: v + 1)

        engine = RuleEngine(
            rules=[Rule(always, inc), Rule(always, inc)],
            keep_unmatched=True,
            match_mode="first",
        )

        out = engine.process(items)
        self.assertEqual(out[0]["x"], 1)


if __name__ == "__main__":
    unittest.main()


