from pydantic import BaseModel
from app.utils.general import remove_none_props_from_dict_recursive
from app.utils.custom_exceptions import DataError


class Update(BaseModel):
    def ensure_valid_field(self):
        filtered = remove_none_props_from_dict_recursive(self.__dict__)

        if len(filtered.items()) == 0:
            raise DataError("Provide at least one field to be updated")

        return filtered
