from __future__ import annotations

import time
from operator import itemgetter
from typing import Any

import requests
from loguru import logger

# =============================================================================
# Exceptions
# =============================================================================


class ZabbixError(RuntimeError):
    """Zabbix API error"""


# =============================================================================
# Utils
# =============================================================================


def sort_dicts(
    data: list[dict],
    key: str,
    *,
    reverse: bool = False,
) -> list[dict]:
    return sorted(data, key=itemgetter(key), reverse=reverse)


# =============================================================================
# Zabbix Client
# =============================================================================


class Zabbix:
    def __init__(self, api: str, username: str, password: str) -> None:
        self.api = api
        self.auth = self._login(username, password)

    # -------------------------------------------------------------------------
    # Core Request
    # -------------------------------------------------------------------------

    def request(self, method: str, params: dict | list) -> dict:
        if not self.api:
            raise ZabbixError("Zabbix API URL not set")

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": None if method == "apiinfo.version" else self.auth,
            "id": int(time.time()),
        }

        resp = requests.post(
            self.api,
            json=payload,
            headers={"Content-Type": "application/json-rpc"},
            timeout=10,
        )

        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            raise ZabbixError(data["error"])

        return data["result"]

    # -------------------------------------------------------------------------
    # Auth
    # -------------------------------------------------------------------------

    def _login(self, username: str, password: str) -> str:
        logger.info("Login started")

        result = self.request(
            "user.login",
            {"username": username, "password": password},
        )

        logger.success("Login succeeded")
        return result

    def logout(self) -> None:
        self.request("user.logout", {})
        logger.success("Logout succeeded")

    # -------------------------------------------------------------------------
    # Basic Info
    # -------------------------------------------------------------------------

    def get_version(self) -> dict:
        return self.request("apiinfo.version", {})

    # -------------------------------------------------------------------------
    # Host / Group / Template
    # -------------------------------------------------------------------------

    def get_hostgroup_ids(self, name: str) -> list[str]:
        result = self.request(
            "hostgroup.get",
            {"output": ["groupid"], "filter": {"name": name}},
        )
        return [r["groupid"] for r in result]

    def get_template_ids(self, name: str) -> list[str]:
        result = self.request(
            "template.get",
            {"output": ["templateid"], "filter": {"name": name}},
        )
        return [r["templateid"] for r in result]

    def get_hosts_by_group(self, name: str, output: str | list = "extend") -> list[dict]:
        group_ids = self.get_hostgroup_ids(name)
        return self.request(
            "host.get",
            {"output": output, "groupids": group_ids},
        )

    def get_hosts_by_template(self, name: str, output: str | list = "extend") -> list[dict]:
        template_ids = self.get_template_ids(name)
        return self.request(
            "host.get",
            {"output": output, "templateids": template_ids},
        )

    # -------------------------------------------------------------------------
    # Interface
    # -------------------------------------------------------------------------

    def get_interfaces(self, hostids: list[str]) -> list[dict]:
        return self.request(
            "hostinterface.get",
            {"hostids": hostids},
        )

    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------

    def _get_items_by_key(
        self,
        hostids: list[str],
        item_key: str,
    ) -> dict[str, str]:
        items = self.request(
            "item.get",
            {
                "output": ["itemid", "hostid"],
                "hostids": hostids,
                "filter": {"key_": item_key},
            },
        )

        return {item["hostid"]: item["itemid"] for item in items}

    def _get_history(
        self,
        itemids: list[str],
        time_from: int,
        time_till: int,
        data_type: int,
    ) -> list[dict]:
        return self.request(
            "history.get",
            {
                "output": "extend",
                "history": data_type,
                "itemids": itemids,
                "time_from": time_from,
                "time_till": time_till,
            },
        )

    def get_history_by_item_key(
        self,
        hosts: list[dict],
        time_from: int,
        time_till: int,
        item_key: str,
        data_type: int = 3,
    ) -> list[dict]:

        if not hosts:
            return []

        hostids = [h["hostid"] for h in hosts]
        item_map = self._get_items_by_key(hostids, item_key)

        if not item_map:
            return []

        history = self._get_history(
            list(item_map.values()),
            time_from,
            time_till,
            data_type,
        )

        history_by_item = {}
        for h in history:
            history_by_item.setdefault(h["itemid"], []).append(h)

        result: list[dict] = []

        for host in hosts:
            itemid = item_map.get(host["hostid"])
            if not itemid:
                continue

            host = host.copy()
            host["itemkey"] = item_key
            host["itemid"] = itemid
            host["history"] = sort_dicts(
                history_by_item.get(itemid, []),
                "clock",
            )
            result.append(host)

        return result

    # -------------------------------------------------------------------------
    # Create Objects
    # -------------------------------------------------------------------------

    def _get_host_by_ip(self, ip: str) -> tuple[str, ...]:
        result = self.request(
            "hostinterface.get",
            {
                "filter": {"ip": ip},
                "selectHosts": ["host"],
            },
        )

        if not result:
            raise ZabbixError(f"Host not found for IP {ip}")

        host = result[0]["hosts"][0]
        return host["host"], result[0]["hostid"], result[0]["interfaceid"]

    def create_item(self, hostid: str, interfaceid: str, item: dict) -> str:
        params = {
            "hostid": hostid,
            "interfaceid": interfaceid,
            "type": 7,
            "value_type": 3,
            "delay": "1m",
            "history": "7d",
            "trends": "7d",
        } | item

        result = self.request("item.create", params)
        return result["itemids"][0]

    def create_trigger(self, host: str, trigger: dict) -> None:
        trigger = trigger.copy()
        trigger["expression"] = trigger["expression"].format(host=host)

        self.request("trigger.create", [trigger])

    def create_graph(self, itemid: str, graph: dict) -> None:
        params = {
            "width": 900,
            "height": 200,
            "gitems": [{"itemid": itemid, "color": "0040FF"}],
        } | graph

        self.request("graph.create", params)

    def create_object(
        self,
        ips: list[str],
        *,
        item: dict | None = None,
        trigger: dict | None = None,
        graph: dict | None = None,
    ) -> None:

        for ip in ips:
            host, hostid, interfaceid = self._get_host_by_ip(ip)

            itemid: str | None = None

            if item:
                itemid = self.create_item(hostid, interfaceid, item)

            if trigger:
                self.create_trigger(host, trigger)

            if graph and itemid:
                self.create_graph(itemid, graph)
