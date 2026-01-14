from __future__ import annotations

from datetime import date


class EquipmentType:
    def __init__(self, id: int, name: str):
        self.id: int = id
        self.name: str = name

    def __repr__(self) -> str:
        return f"EquipmentType(id={self.id}, name={self.name})"


class EquipmentItem:
    def __init__(self, id: int, serial_number: str):
        self.id: int = id
        self.serial_number: str = serial_number

    def __repr__(self) -> str:
        return f"EquipmentItem(id={self.id}, serial_number={self.serial_number})"


class BasketItem:
    def __init__(self, equipment_item: EquipmentItem, plan_id: int | None, plan_name: str | None = None):
        self.equipment_item: EquipmentItem = equipment_item
        self.plan_id: int | None = plan_id
        self.plan_name: str | None = plan_name

    def __repr__(self) -> str:
        return (
            f"BasketItem(equipment_item={self.equipment_item}, "
            f"plan_id={self.plan_id}, plan_name={self.plan_name})"
        )


class Basket:
    def __init__(self, id: int, items: list[Inspection] | None = None):
        self.id: int = id
        self.items: list[Inspection] = items or []

    def __repr__(self) -> str:
        return f"Basket(id={self.id}, items={self.items})"


class Inspection:
    def __init__(
        self,
        equipment_item: EquipmentItem,
        equipment_group: EquipmentType | None = None,
        plan_id: int | None = None,
        plan_name: str | None = None,
        due_date: date | None = None,
    ):
        self.equipment_item: EquipmentItem = equipment_item
        self.equipment_group: EquipmentType | None = equipment_group
        self.plan_id: int | None = plan_id
        self.plan_name: str | None = plan_name
        self.due_date: date | None = due_date

    def __repr__(self) -> str:
        return (
            f"Inspection(equipment_item={self.equipment_item}, equipment_group={self.equipment_group}, "
            f"plan_id={self.plan_id}, plan_name={self.plan_name}, due_date={self.due_date})"
        )


class OrganizationalList:
    def __init__(self, id: int, title: str, is_private: bool):
        self.id: int = id
        self.title: str = title
        self.is_private: bool = is_private

    def __repr__(self) -> str:
        return (
            f"OrganizationalList(id={self.id}, title={self.title}, "
            f"is_private={self.is_private})"
        )


class User:
    def __init__(self, username: str, email: str):
        self.username: str = username
        self.email: str = email

    def __repr__(self) -> str:
        return f"User(username={self.username}, email={self.email})"


__all__ = [
    "EquipmentType",
    "EquipmentItem",
    "BasketItem",
    "Basket",
    "Inspection",
    "OrganizationalList",
    "User",
]
