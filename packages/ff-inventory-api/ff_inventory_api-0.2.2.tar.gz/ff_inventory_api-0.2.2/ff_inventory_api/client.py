from __future__ import annotations

import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from .models import (
    Basket,
    EquipmentItem,
    EquipmentType,
    Inspection,
    OrganizationalList,
    User,
)


class FFInventoryAPI:
    def __init__(self):
        self.session: requests.Session = requests.Session()
        self.play_session: str | None = None
        self.csrf_token: str | None = None  # Store csrf_token

    def post_request(self, url: str, data: dict, headers: dict | None = None) -> requests.Response:
        """Helper to send a POST request using the session."""
        if headers is None:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return self.session.post(url, data=data, headers=headers)

    def login(self, username: str, password: str) -> None:
        login_url = "https://app.ff-inventory.com/login"
        login_api_url = "https://app.ff-inventory.com/doLogin"

        # Abrufen der Login-Seite, um den csrfToken zu extrahieren
        response = self.session.get(login_url)
        if response.status_code != 200:
            print("Fehler beim Abrufen der Login-Seite:", response.status_code)
            return

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token_input = soup.find("input", {"name": "csrfToken"})
        self.csrf_token = csrf_token_input["value"] if csrf_token_input else None
        if not self.csrf_token:
            print("csrfToken nicht gefunden!")
            return

        payload = {"username": username, "password": password, "csrfToken": self.csrf_token}
        login_response = self.post_request(login_api_url, data=payload)
        if login_response.status_code != 200:
            print("Login fehlgeschlagen!")
            print("Statuscode:", login_response.status_code)
            print("Antwort:", login_response.text)
            return

        cookies = self.session.cookies.get_dict()
        self.play_session = cookies.get("PLAY_SESSION")

    def get_upcoming_inspections(self) -> list[Inspection] | None:
        inspections_url = "https://app.ff-inventory.com/items/reports/upcomingInspections"
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return None

        response = self.session.get(inspections_url)
        if response.status_code != 200:
            print("Fehler beim Abrufen der offenen Prüfungen!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        inspections: list[Inspection] = []
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header row
                columns = row.find_all("td")
                if len(columns) == 0:
                    continue

                # Extract item_id from the item link in column 2
                item_id: int | None = None
                serial_number: str | None = None
                item_link = columns[2].find("a", href=re.compile(r"/items/(\d+)/show"))
                if item_link:
                    match = re.search(r"/items/(\d+)/show", item_link["href"])
                    if match:
                        item_id = int(match.group(1))
                    serial_number = item_link.get_text(strip=True)

                # Extract equipment type/model from column 1
                group_id: int | None = None
                group_name: str | None = None
                model_link = columns[1].find("a", href=re.compile(r"/itemModels/(\d+)/show"))
                if model_link:
                    match = re.search(r"/itemModels/(\d+)/show", model_link["href"])
                    if match:
                        group_id = int(match.group(1))
                    group_name = model_link.get_text(strip=True)

                # Extract plan_id from button in the actions dropdown (column 7)
                plan_id: int | None = None
                button = columns[7].find("button", {"data-plan": True})
                if button:
                    plan_id = int(button["data-plan"]) if button.get("data-plan") else None

                if item_id and group_id:
                    equipment_group = EquipmentType(id=group_id, name=group_name or "")
                    equipment_item = EquipmentItem(id=item_id, serial_number=serial_number or "")
                    inspection = Inspection(
                        equipment_item=equipment_item,
                        equipment_group=equipment_group,
                        plan_id=plan_id,
                    )
                    inspections.append(inspection)

        return inspections

    def get_organisational_lists(self) -> list[OrganizationalList]:
        lists_url = "https://app.ff-inventory.com/barcode/api/lists"
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return []

        response = self.session.get(lists_url)
        if response.status_code != 200:
            print("Fehler beim Abrufen der Listen!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return []

        lists: list[OrganizationalList] = []
        data = response.json()
        for item in data:
            list_id = int(item["idList"])
            title = item["listTitle"]
            is_private = item["private"]
            lists.append(OrganizationalList(id=list_id, title=title, is_private=is_private))
        return lists

    def create_organisational_list(self, title: str, description: str) -> bool:
        create_list_url = "https://app.ff-inventory.com/lists/save"
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return False
        if not self.csrf_token:
            print("Fehler: csrfToken ist nicht verfügbar. Bitte erneut einloggen.")
            return False

        payload = {
            "csrfToken": self.csrf_token,
            "id": "",
            "userId": "",
            "type": "CUSTOM",
            "title": title,
            "description": description,
        }
        post_response = self.post_request(create_list_url, data=payload)
        if post_response.status_code != 200:
            print("Fehler beim Erstellen der Liste!")
            print("Statuscode:", post_response.status_code)
            print("Antwort:", post_response.text)
            return False
        return True

    def delete_organisational_list(self, organizational_list: OrganizationalList) -> bool:
        delete_url = f"https://app.ff-inventory.com/lists/{organizational_list.id}/delete/"
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return False
        response = self.session.post(delete_url)
        if response.status_code != 200:
            print(f"Fehler beim Löschen der Liste mit ID {organizational_list.id}!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return False
        return True

    def add_to_list(self, equipment_item: EquipmentItem, organizational_list: OrganizationalList) -> bool:
        fixed_serial_number = equipment_item.serial_number.replace("/", "%2F").replace("#", "%23")
        add_url = (
            f"https://app.ff-inventory.com/barcode/api/lists/add/{fixed_serial_number}?idList={organizational_list.id}"
        )
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return False

        response = self.session.post(add_url, headers={"csrf-token": self.csrf_token})
        if response.status_code == 200:
            return True
        if response.status_code == 406 and "Das Gerät existiert bereits in dieser Liste!" in response.text:
            print(
                f"Item mit Seriennummer {equipment_item.serial_number} ist bereits in der Liste "
                f"{organizational_list.title} vorhanden."
            )
            return True
        print(
            f"Fehler beim Hinzufügen des Items mit Seriennummer {equipment_item.serial_number} "
            f"zur Liste {organizational_list.title}!"
        )
        print("Statuscode:", response.status_code)
        print("Antwort:", response.text)
        return False

    def remove_from_list(self, equipment_item: EquipmentItem, organizational_list: OrganizationalList) -> bool:
        remove_url = (
            f"https://app.ff-inventory.com/lists/{organizational_list.id}/entry/by/item/{equipment_item.id}/delete"
        )
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return False
        response = self.session.get(remove_url)
        if response.status_code != 200:
            print(
                f"Fehler beim Entfernen des Items mit ID {equipment_item.id} "
                f"aus der Liste {organizational_list.title}!"
            )
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return False
        return True

    def add_list_entries_to_basket(self, basket: Basket, organizational_list: OrganizationalList) -> bool:
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return False
        if not self.csrf_token:
            print("Fehler: csrfToken ist nicht verfügbar. Bitte erneut einloggen.")
            return False

        list_id = organizational_list.id
        basket_id = basket.id
        url = f"https://app.ff-inventory.com/inspections/baskets/{basket_id}/ajax/addListEntries/{list_id}"
        headers = {"csrf-token": self.csrf_token}
        response = self.session.post(url, headers=headers)
        if response.status_code != 200:
            print(f"Fehler beim Hinzufügen von Einträgen in den Warenkorb {basket_id} für Liste {list_id}!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return False
        return True

    def remove_list_entries_to_basket(self, basket: Basket, organizational_list: OrganizationalList) -> bool:
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return False
        if not self.csrf_token:
            print("Fehler: csrfToken ist nicht verfügbar. Bitte erneut einloggen.")
            return False

        list_id = organizational_list.id
        basket_id = basket.id
        url = f"https://app.ff-inventory.com/inspections/baskets/{basket_id}/ajax/removeListEntries/{list_id}"
        headers = {"csrf-token": self.csrf_token}
        response = self.session.post(url, headers=headers)
        if response.status_code != 200:
            print(f"Fehler beim Entfernen von Einträgen aus dem Warenkorb {basket_id} für Liste {list_id}!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return False
        return True

    def parse_equipment_items_from_table(self, rows, column_mapping: dict) -> list[dict]:
        parsed_items: list[dict] = []
        for row in rows[1:]:  # Skip header row
            columns = row.find_all("td")
            if len(columns) == 0:
                continue

            item_data: dict = {}
            for key, index in column_mapping.items():
                if key == "item_id":
                    input_element = columns[index].find("input", {"data-batch-id": True})
                    item_data[key] = int(input_element["data-batch-id"]) if input_element else None
                elif key == "plan_id":
                    input_element = columns[index].find("button", {"data-plan": True})
                    item_data[key] = int(input_element["data-plan"]) if input_element else None
                elif key == "group_id" or key == "group_name":
                    group_link = columns[index].find("a")
                    if key == "group_id":
                        item_data[key] = int(group_link["href"].split("/")[-2]) if group_link else None
                    elif key == "group_name":
                        item_data[key] = group_link.get_text(strip=True) if group_link else None
                else:
                    item_data[key] = columns[index].get_text(strip=True)
            parsed_items.append(item_data)
        return parsed_items

    def get_basket(self) -> Basket | None:
        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return None

        url = "https://app.ff-inventory.com/inspections/baskets/index"
        response = self.session.get(url)
        if response.status_code != 200:
            print("Fehler beim Abrufen des Prüfkorbs!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        pattern = re.compile(r"/inspections/baskets/(\d+)/")
        basket_id: int | None = None
        for a in soup.find_all("a", href=True):
            match = pattern.search(a["href"])
            if match:
                basket_id = int(match.group(1))
                break
        if basket_id is None:
            print("Basket-ID konnte nicht gefunden werden.")
            return None

        items: list[Inspection] = []
        headers = soup.find_all("h4")

        def parse_table_rows(table_el, plan_name: str | None):
            local_items: list[Inspection] = []
            if not table_el:
                return local_items
            rows = table_el.find_all("tr")
            for row in rows[1:]:
                tds = row.find_all("td")
                if not tds:
                    continue
                item_id: int | None = None
                serial_number: str | None = None
                item_link = row.find("a", href=re.compile(r"/items/(\d+)/show"))
                if item_link:
                    href = item_link.get("href", "")
                    m = re.search(r"/items/(\d+)/show", href)
                    if m:
                        item_id = int(m.group(1))
                    serial_number = item_link.get_text(strip=True) or None

                equipment_group: EquipmentType | None = None
                model_link = row.find("a", href=re.compile(r"/itemModels/(\d+)/show"))
                if model_link:
                    href = model_link.get("href", "")
                    m = re.search(r"/itemModels/(\d+)/show", href)
                    group_id = int(m.group(1)) if m else None
                    group_name = model_link.get_text(strip=True) or None
                    if group_id is not None and group_name is not None:
                        equipment_group = EquipmentType(id=group_id, name=group_name)

                plan_id: int | None = None
                create_link = row.find("a", href=re.compile(r"/inspections/create\?"))
                if create_link:
                    href = create_link.get("href", "")
                    m = re.search(r"[?&]planId=(\d+)", href)
                    if m:
                        plan_id = int(m.group(1))
                if plan_id is None:
                    btn = row.find("button", attrs={"data-plan": True})
                    if btn:
                        try:
                            plan_id = int(btn.get("data-plan"))
                        except (TypeError, ValueError):
                            plan_id = None

                # Try to extract the due date from a right-aligned cell that is not the action cell
                due_date: date | None = None
                for td in tds:
                    classes = td.get("class", [])
                    if "text-right" in classes:
                        # Skip action cells that contain an inspections/create link
                        if td.find("a", href=re.compile(r"/inspections/create\\?")):
                            continue
                        txt = td.get_text(strip=True)
                        if txt:
                            # Extract date part like 01.04.2025 from strings like "Di 01.04.2025"
                            m = re.search(r"(\d{2}\.\d{2}\.\d{4})", txt)
                            if m:
                                try:
                                    due_date = datetime.strptime(m.group(1), "%d.%m.%Y").date()
                                except ValueError:
                                    due_date = None
                            break

                if item_id is not None:
                    local_items.append(
                        Inspection(
                            equipment_item=EquipmentItem(id=item_id, serial_number=serial_number or ""),
                            equipment_group=equipment_group,
                            plan_id=plan_id,
                            plan_name=plan_name,
                            due_date=due_date,
                        )
                    )
            return local_items

        if headers:
            for h in headers:
                plan_name = h.get_text(strip=True) if h else None
                table_el = None
                nxt = h
                while nxt and not table_el:
                    nxt = nxt.find_next()
                    if nxt and getattr(nxt, "name", None) == "table":
                        table_el = nxt
                        break
                items.extend(parse_table_rows(table_el, plan_name))
        else:
            table = soup.find("table")
            items.extend(parse_table_rows(table, None))

        return Basket(id=basket_id, items=items)

    def get_equipmentitems_in_list(self, organizational_list: OrganizationalList) -> list[EquipmentItem]:
        """Fetch all EquipmentItems in a given OrganizationalList by parsing the list page."""
        list_url = f"https://app.ff-inventory.com/lists/{organizational_list.id}/show/"

        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return []

        response = self.session.get(list_url)

        if response.status_code != 200:
            print(f"Fehler beim Abrufen der Items in der Liste {organizational_list.title}!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table")
        if not table:
            return []

        rows = table.find_all("tr")
        equipment_items: list[EquipmentItem] = []

        for row in rows[1:]:  # Skip header row
            columns = row.find_all("td")
            if len(columns) == 0:
                continue

            # Extract item_id from the item link in column 2
            item_id: int | None = None
            serial_number: str | None = None
            item_link = columns[2].find("a", href=re.compile(r"/items/(\d+)/show"))
            if item_link:
                match = re.search(r"/items/(\d+)/show", item_link.get("href", ""))
                if match:
                    item_id = int(match.group(1))
                serial_number = item_link.get_text(strip=True)

            if item_id:
                equipment_items.append(
                    EquipmentItem(
                        id=item_id,
                        serial_number=serial_number or "",
                    )
                )

        return equipment_items

    def get_users(self) -> list[User]:
        """Fetch all users from the users index page and parse username + email."""
        users_url = "https://app.ff-inventory.com/users/index"

        if not self.play_session:
            print("Fehler: Nicht eingeloggt. Bitte zuerst einloggen.")
            return []

        response = self.session.get(users_url)

        if response.status_code != 200:
            print("Fehler beim Abrufen der Benutzer!")
            print("Statuscode:", response.status_code)
            print("Antwort:", response.text)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        users: list[User] = []

        table = soup.find("table")
        if not table:
            return []

        rows = table.find_all("tr")
        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) == 0:
                continue

            username_td = columns[5] if len(columns) > 5 else None
            email_td = columns[4] if len(columns) > 4 else None

            if not username_td or not email_td:
                continue

            username = username_td.get_text(strip=True)

            for sup in email_td.find_all("sup"):
                sup.decompose()
            email = email_td.get_text(strip=True)

            users.append(User(username=username, email=email))

        return users


__all__ = ["FFInventoryAPI"]
