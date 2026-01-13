# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:18
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:18
# Thanks for your comments!

import time

from sqlalchemy import Column, DECIMAL, VARCHAR, BigInteger, Integer
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

meta_data = MetaData()


class ModelBase:
    __allow_unmapped__ = True  # 允许未映射的字段


ModelBase = declarative_base(metadata=meta_data, cls=ModelBase)


class ModifyingBehevior(object):
    """
    模型固定字段
    """
    obsoleted = Column('obsoleted', Integer, default=0)
    created_at = Column('created_at', BigInteger, default=lambda: int(time.time() * 1000))
    updated_at = Column('updated_at', BigInteger, default=lambda: int(time.time() * 1000),
                        onupdate=lambda: int(time.time() * 1000))
    created_by = Column('created_by', VARCHAR(50))
    updated_by = Column('updated_by', VARCHAR(50))
    sort_value = Column('sort_value', DECIMAL(10, 2))

    def as_dict(self):
        res_dict = {}
        for k in self._sa_class_manager._all_key_set:
            res_dict[str(k)] = getattr(self, k)
        return res_dict
