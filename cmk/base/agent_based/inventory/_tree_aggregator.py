#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Optional, Iterable, Union, Tuple, Sequence, Hashable, Dict, Literal

import cmk.utils.debug
from cmk.utils.structured_data import StructuredDataNode

from cmk.base.api.agent_based.inventory_classes import (
    AttrDict,
    Attributes,
    InventoryResult,
    TableRow,
)

from .utils import InventoryTrees


class TreeAggregator:
    def __init__(self):
        self.trees = InventoryTrees(
            inventory=StructuredDataNode(),
            status_data=StructuredDataNode(),
        )
        self._index_cache = {}
        self._class_mutex = {}

    def aggregate_results(
        self,
        inventory_generator: InventoryResult,
    ) -> Optional[Exception]:

        try:
            table_rows, attributes = self._dispatch(inventory_generator)
        except Exception as exc:
            if cmk.utils.debug.enabled():
                raise
            return exc

        for tabr in table_rows:
            self._integrate_table_row(tabr)

        for attr in attributes:
            self._integrate_attributes(attr)

        return None

    def _dispatch(
        self,
        intentory_items: Iterable[Union[TableRow, Attributes]],
    ) -> Tuple[Sequence[TableRow], Sequence[Attributes]]:
        attributes = []
        table_rows = []
        for item in intentory_items:
            expected_class_name = self._class_mutex.setdefault(tuple(item.path),
                                                               item.__class__.__name__)
            if item.__class__.__name__ != expected_class_name:
                raise TypeError(f"Cannot create {item.__class__.__name__} at path {item.path}:"
                                f" this is a {expected_class_name} node.")
            if isinstance(item, Attributes):
                attributes.append(item)
            elif isinstance(item, TableRow):
                table_rows.append(item)
            else:
                raise NotImplementedError()  # can't happen, inventory results are filtered

        return table_rows, attributes

    def _integrate_attributes(
        self,
        attributes: Attributes,
    ) -> None:
        leg_path = ".".join(attributes.path) + "."
        if attributes.inventory_attributes:
            self.trees.inventory.get_dict(leg_path).update(attributes.inventory_attributes)
        if attributes.status_attributes:
            self.trees.status_data.get_dict(leg_path).update(attributes.status_attributes)

    @staticmethod
    def _make_row_key(key_columns: AttrDict) -> Hashable:
        return tuple(sorted(key_columns.items()))

    def _get_row(
        self,
        path: str,
        tree_name: Literal["inventory", "status_data"],
        row_key: Hashable,
        key_columns: AttrDict,
    ) -> Dict[str, Union[None, int, float, str]]:
        """Find matching table row or create one"""
        table = getattr(self.trees, tree_name).get_list(path)

        new_row_index = len(table)  # index should we need to create a new row
        use_index = self._index_cache.setdefault((path, tree_name, row_key), new_row_index)

        if use_index == new_row_index:
            row = {**key_columns}
            table.append(row)

        return table[use_index]

    def _integrate_table_row(
        self,
        table_row: TableRow,
    ) -> None:
        leg_path = ".".join(table_row.path) + ":"
        row_key = self._make_row_key(table_row.key_columns)

        # do this always, it sets key_columns!
        self._get_row(
            leg_path,
            "inventory",
            row_key,
            table_row.key_columns,
        ).update(table_row.inventory_columns)

        # do this only if not empty:
        if table_row.status_columns:
            self._get_row(
                leg_path,
                "status_data",
                row_key,
                table_row.key_columns,
            ).update(table_row.status_columns)
