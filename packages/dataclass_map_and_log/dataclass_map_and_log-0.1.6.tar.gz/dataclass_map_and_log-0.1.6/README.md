# Dataclass Map And Log[![tag](https://img.shields.io/github/tag/namelivia/dataclass-map-and-log.svg)](https://github.com/namelivia/dataclass-map-and-log/releases) [![Build](https://github.com/namelivia/dataclass-map-and-log/actions/workflows/build.yml/badge.svg)](https://github.com/namelivia/dataclass-map-and-log/actions?query=workflow%3ABuild) [![codecov](https://codecov.io/gh/namelivia/dataclass-map-and-log/branch/master/graph/badge.svg)](https://codecov.io/gh/namelivia/dataclass-map-and-log)

Map dictionaries to pydantic dataclasses, log any extra attributes.

## Example
```python
from dataclass_map_and_log.mapper import DataclassMapper

@dataclass
class Child:
    name: str
    surname: str


@dataclass
class SingleChild:
    name: str


@dataclass
class Parent:
    name: str
    surname: str
    children: List[Child]
    single_child: SingleChild
    
data = {
    "name": "parent_name",
    "surname": "parent_surname",
    "extra": "parent_extra_data",
    "children": [
        {
            "name": "child1_name",
            "surname": "child1_surname",
            "extra": "child_extra_data",
        },
        {
            "name": "child2_name",
            "surname": "child2_surname",
        },
    ],
    "single_child": {"name": "test"},
}

definition = DataclassMapper.map(Parent, data)
```

You can then access the dataclass instance like:
```python
definition.single_child.name
```

And you would have gotten the following warning log messages:
```
"Unexpected attribute extra on class <class 'tests.test_dataclass_map_and_log.Parent'> with value parent_extra_data",
"Unexpected attribute extra on class <class 'tests.test_dataclass_map_and_log.Child'> with value child_extra_data",
```
