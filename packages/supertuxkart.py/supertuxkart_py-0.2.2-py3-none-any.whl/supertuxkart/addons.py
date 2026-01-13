from __future__ import annotations

from .enums import AddonStatus, AddonType
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SuperTuxKartClient, AsyncSuperTuxKartClient
    from xml.etree.ElementTree import Element
    from typing import Optional


class AddonVote:
    def __init__(self, d: Element):
        self.voted: bool = d.attrib["voted"] == "yes"
        self.rating: float = float(d.attrib["rating"])

    def __repr__(self):
        return f"<AddonVote voted={self.voted} rating={self.rating}>"


class SetAddonVote:
    def __init__(self, d: Element):
        self.new_average: float = float(d.attrib["new-average"])
        self.new_number: int = int(d.attrib["new-number"])
        self.id: str = d.attrib["addon-id"]


class Addon:
    def __init__(self, d: Element):
        a = d.attrib
        self.id: str = a["id"]
        self.type: AddonType = AddonType(d.tag)
        self.name: str = a["name"]
        self.file: str = a["file"]
        self.date: datetime = datetime.fromtimestamp(int(a["date"]))
        self.uploader: Optional[str] = a["uploader"] or None
        self.designer: str = a["designer"]
        self.description: Optional[str] = a["description"] or None
        self.image: Optional[str] = a.get("image")
        self.icon: Optional[str] = a.get("icon")
        self.format: int = int(a["format"])
        self.revision: int = int(a["revision"])
        self.status: AddonStatus = AddonStatus(int(a["status"]))
        self.size: int = int(a["size"])
        self.rating: float = float(a["rating"])

    def __repr__(self):
        return (
            "<Addon id=%s "
            "name=%s "
            "uploader=%s "
            "status=%s "
            "size=%s "
            "revision=%s>"
        ) % (
            self.id,
            self.name,
            self.uploader,
            self.status,
            self.size,
            self.revision,
        )

    def __str__(self):
        return self.name


class AddonsModule:
    def __init__(self, client: SuperTuxKartClient):
        self.client: SuperTuxKartClient = client

    def get_addon_vote(self, id: str) -> AddonVote:
        data = self.client.http.xml_request(
            "/api/v2/user/get-addon-vote", {"addonid": id}
        )
        return AddonVote(data)

    def set_addon_vote(self, id: str, rating: int) -> SetAddonVote:
        if rating < 1 or rating > 6:
            raise ValueError("Rating must not go below 1 or above 6.")

        data = self.client.http.xml_request(
            "/api/v2/user/set-addon-vote", {"addonid": id, "rating": rating}
        )
        return SetAddonVote(data)

    def get_addons(self) -> list[Addon]:
        data = self.client.http.xml_request(
            "/dl/xml/online_assets.xml", no_auth=True, check_status=False
        )
        return [Addon(x) for x in data]


class AsyncAddonsModule:
    def __init__(self, client: AsyncSuperTuxKartClient):
        self.client: AsyncSuperTuxKartClient = client

    async def get_addon_vote(self, id: str) -> AddonVote:
        data = await self.client.http.xml_request(
            "/api/v2/user/get-addon-vote", {"addonid": id}
        )
        return AddonVote(data)

    async def set_addon_vote(self, id: str, rating: int) -> SetAddonVote:
        if rating < 1 or rating > 6:
            raise ValueError("Rating must not go below 1 or above 6.")

        data = await self.client.http.xml_request(
            "/api/v2/user/set-addon-vote", {"addonid": id, "rating": rating}
        )
        return SetAddonVote(data)

    async def get_addons(self) -> list[Addon]:
        data = await self.client.http.xml_request(
            "/dl/xml/online_assets.xml", no_auth=True, check_status=False
        )
        return [Addon(x) for x in data]
