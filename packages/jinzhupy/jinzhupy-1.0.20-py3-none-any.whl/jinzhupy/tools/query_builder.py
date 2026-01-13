# -*- coding: utf-8 -*-
# @Author	: starview.brotherbaby
# @Date		: 2025/12/24 16:40
# @Last Modified by:   starview.brotherbaby
# @Last Modified time: 2025/12/24 16:40
# Thanks for your comments!

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Set


def get_year_from_timestamp(ms_ts):
    """ 从毫秒级时间戳去获取其对应的年份 """
    sec_ts = int(ms_ts) // 1000
    dt = datetime.datetime.fromtimestamp(sec_ts)
    return dt.year


class ConditionType(Enum):
    """条件类型枚举"""
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "gt"
    GREATER_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_EQUAL = "lte"
    BETWEEN = "between"
    LIKE = "like"
    ILIKE = "ilike"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


@dataclass
class QueryCondition:
    """查询条件数据类"""
    field: str
    condition_type: ConditionType
    value: Any

    def apply(self, model) -> Any:
        """将条件应用到模型"""
        if hasattr(model, self.field):
            field_obj = getattr(model, self.field)
        else:
            raise AttributeError(f"Model {model.__class__.__name__} has no attribute '{self.field}'")

        # 应用条件
        if self.condition_type == ConditionType.EQUAL:
            return field_obj == self.value
        elif self.condition_type == ConditionType.NOT_EQUAL:
            return field_obj != self.value
        elif self.condition_type == ConditionType.IN:
            return field_obj.in_(self.value)
        elif self.condition_type == ConditionType.NOT_IN:
            return field_obj.notin_(self.value)
        elif self.condition_type == ConditionType.GREATER_THAN:
            return field_obj > self.value
        elif self.condition_type == ConditionType.GREATER_EQUAL:
            return field_obj >= self.value
        elif self.condition_type == ConditionType.LESS_THAN:
            return field_obj < self.value
        elif self.condition_type == ConditionType.LESS_EQUAL:
            return field_obj <= self.value
        elif self.condition_type == ConditionType.BETWEEN:
            return field_obj.between(*self.value)
        elif self.condition_type == ConditionType.LIKE:
            return field_obj.like(self.value)
        elif self.condition_type == ConditionType.ILIKE:
            return field_obj.ilike(self.value)
        elif self.condition_type == ConditionType.IS_NULL:
            return field_obj.is_(None)
        elif self.condition_type == ConditionType.IS_NOT_NULL:
            return field_obj.is_not(None)
        else:
            raise ValueError(f"Unsupported condition type: {self.condition_type}")


class GenericQueryBuilder:
    """通用查询构建器"""

    def __init__(self):
        self.base_conditions: List[QueryCondition] = []
        self.year_specific_conditions: Dict[str, List[QueryCondition]] = {}

    def add_condition(self, field: str, condition_type: ConditionType, value: Any,
                      year: Optional[str] = None) -> 'GenericQueryBuilder':
        """添加查询条件

        Args:
            field: 字段名
            condition_type: 条件类型
            value: 条件值
            year: 年份，如果为None则为基础条件
        """
        condition = QueryCondition(field, condition_type, value)

        if year:
            if year not in self.year_specific_conditions:
                self.year_specific_conditions[year] = []
            self.year_specific_conditions[year].append(condition)
        else:
            self.base_conditions.append(condition)

        return self

    def add_equal(self, field: str, value: Any, year: Optional[str] = None) -> 'GenericQueryBuilder':
        """添加等于条件"""
        return self.add_condition(field, ConditionType.EQUAL, value, year)

    def add_in(self, field: str, values: Union[List[Any], Set[Any]],
               year: Optional[str] = None) -> 'GenericQueryBuilder':
        """添加IN条件"""
        return self.add_condition(field, ConditionType.IN, values, year)

    def add_between(self, field: str, start: Any, end: Any, year: Optional[str] = None) -> 'GenericQueryBuilder':
        """添加BETWEEN条件"""
        return self.add_condition(field, ConditionType.BETWEEN, (start, end), year)

    def add_gte(self, field: str, value: Any, year: Optional[str] = None) -> 'GenericQueryBuilder':
        """添加大于等于条件"""
        return self.add_condition(field, ConditionType.GREATER_EQUAL, value, year)

    def add_lte(self, field: str, value: Any, year: Optional[str] = None) -> 'GenericQueryBuilder':
        """添加小于等于条件"""
        return self.add_condition(field, ConditionType.LESS_EQUAL, value, year)

    def add_time_range(self, start_time: Optional[int], end_time: Optional[int],
                       field_name: str, max_year_span: int = 1) -> 'GenericQueryBuilder':
        """添加时间范围条件

        Args:
            start_time: 开始时间
            end_time: 结束时间
            field_name: 时间字段名
            max_year_span: 最大年份跨度，默认1年
        """
        if not start_time or not end_time:
            return self

        start_year = get_year_from_timestamp(start_time)
        end_year = get_year_from_timestamp(end_time)

        # 检查年份跨度
        if (end_year - start_year) > max_year_span:
            raise ValueError(f"{field_name} the time frame cannot exceed {max_year_span} year(s).")

        if start_year == end_year:
            # 同一年份
            self.add_between(field_name, start_time, end_time, str(start_year))
        else:
            # 跨年
            self.add_gte(field_name, start_time, str(start_year))
            self.add_lte(field_name, end_time, str(end_year))

        return self

    def build_conditions(self, year: str, model) -> List[Any]:
        """为所有条件构建查询条件"""
        conditions = []

        # 添加基础条件
        for condition in self.base_conditions:
            conditions.append(condition.apply(model))

        # 添加年份特定条件
        if year in self.year_specific_conditions:
            for condition in self.year_specific_conditions[year]:
                conditions.append(condition.apply(model))

        return conditions

    def get_years_to_query(self) -> List[str]:
        """获取需要查询的年份列表"""
        return list(self.year_specific_conditions.keys())
