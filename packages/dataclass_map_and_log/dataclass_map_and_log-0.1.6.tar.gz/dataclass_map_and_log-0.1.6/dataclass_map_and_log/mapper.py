import inspect
import logging

logger = logging.getLogger(__name__)


class DataclassMapper:
    @staticmethod
    def _filter_dict(_class, data):
        class_description = inspect.getfullargspec(_class.__init__)
        arguments = class_description.args
        arguments.pop(0)  # Remove self
        filtered_data = {}
        for attr, value in data.items():
            if attr in arguments:
                filtered_data[attr] = DataclassMapper._get_filtered_item(
                    value, attr, class_description
                )
            else:
                logger.warning(
                    "Unexpected attribute %s on class %s with value %s",
                    attr,
                    _class,
                    "None" if value is None else value,
                )
        return _class(**filtered_data)

    @staticmethod
    def _get_filtered_item(value, attr, class_description):
        if type(value) is dict:
            return DataclassMapper._filter_dict(
                DataclassMapper._get_target_class(attr, class_description), value
            )
        if type(value) is list:
            return DataclassMapper._filter_list(value, attr, class_description)
        return value

    @staticmethod
    def _filter_list(_list, attr, class_description):
        return [
            DataclassMapper._get_filtered_item(item, attr, class_description)
            for item in _list
        ]

    @staticmethod
    def _is_list_annotation(_class):
        return (
            _class.__module__ == "typing"
        )  # Simple way of checking if it List[SomeClass]

    @staticmethod
    def _get_target_class(attr, class_description):
        result = class_description.annotations[attr]
        if DataclassMapper._is_list_annotation(result):
            return result.__args__[0]
        return result

    @staticmethod
    def map(_class, data):
        return DataclassMapper._filter_dict(_class, data)
