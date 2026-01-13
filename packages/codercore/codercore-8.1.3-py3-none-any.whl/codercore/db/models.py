from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    def set_fields(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __hash__(self) -> int:
        raise NotImplementedError

    def __eq__(self, other: any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return hash(self) == hash(other)
