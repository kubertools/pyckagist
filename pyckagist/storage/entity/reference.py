from pyckagist.storage.entity.base import BaseEntity


class ReferenceEntity(BaseEntity):
    namespace: str
    package: str

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.namespace != other.namespace:
            return False
        if self.package != other.package:
            return False

        return True
