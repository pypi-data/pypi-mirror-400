from cave_utils.builders.groups import DateGroupsBuilder

date_data = ["2023-01-01", "2023-02-01"]

# Test 1: Basic
builder = DateGroupsBuilder(
    group_name="Dates",
    date_data=date_data,
    include_month=True,
    include_week_day=True,
)
serialized = builder.serialize()

# Check month is numbers
# We have dates from 2023-01-01 to 2023-02-01.
# Months: 01, 02
assert "01" in serialized["data"]["month"]
assert "02" in serialized["data"]["month"]
assert serialized["levels"]["month"]["ordering"] == ["01", "02"]

# Check week day is numbers
# We have all days of week in that range.
assert serialized["levels"]["week_day"]["ordering"] == ["0", "1", "2", "3", "4", "5", "6"]

# Test 2: Names
builder_names = DateGroupsBuilder(
    group_name="Dates",
    date_data=date_data,
    include_month=True,
    include_week_day=True,
    month_as_name=True,
    week_day_as_name=True,
)
serialized_names = builder_names.serialize()

# Check month is names
assert "January" in serialized_names["data"]["month"]
assert "February" in serialized_names["data"]["month"]
assert serialized_names["levels"]["month"]["ordering"] == ["January", "February"]

# Check week day is names
assert "Sunday" in serialized_names["data"]["week_day"]
assert "Monday" in serialized_names["data"]["week_day"]
# Ordering should be Sunday, Monday, Tuesday...
expected_ordering = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
assert serialized_names["levels"]["week_day"]["ordering"] == expected_ordering

# Test 3: All Features
builder_all = DateGroupsBuilder(
    group_name="Dates",
    date_data=date_data,
    include_year=True,
    include_year_month=True,
    include_year_month_day=True,
    include_year_week=True,
    include_year_day=True,
    include_month=True,
    include_month_week=True,
    include_month_day=True,
    include_week_day=True,
)
serialized_all = builder_all.serialize()

# Check keys exist
expected_keys = [
    "year",
    "year_month",
    "year_month_day",
    "year_week",
    "year_day",
    "month",
    "month_week",
    "month_day",
    "week_day",
]
for key in expected_keys:
    assert key in serialized_all["data"]
    assert key in serialized_all["levels"]

# Check some values
assert 2023 in serialized_all["data"]["year"]
assert "2023-01" in serialized_all["data"]["year_month"]
assert "2023-01-01" in serialized_all["data"]["year_month_day"]

print("DateGroupsBuilder Tests: Passed!")
