import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseGenerator(ABC):
    """
    所有生成器的抽象基类。
    所有生成器类都应该继承此类并实现 generate() 方法。
    """

    @abstractmethod
    def generate(self) -> Any:
        """
        生成并返回生成器的输出结果。

        Returns:
            Any: 生成的结果，具体类型由子类决定
        """
        pass

    def generate_many(self, count: int, allow_duplicates: bool = False) -> List[Any]:
        """
        生成多个不重复的结果（默认实现：循环调用单次生成并校验去重）。

        Args:
            count: 要生成的数量
            allow_duplicates: 如果为 True，允许重复（当数量超过可用数据时）
                            如果为 False，当数量超过可用数据时会抛出 ValueError

        Returns:
            List[Any]: 生成的结果列表，不包含重复项

        Raises:
            ValueError: 当 count 为负数或零时
            ValueError: 当 allow_duplicates=False 且请求的数量超过可用数据时
        """
        if count <= 0:
            raise ValueError(f"count must be positive, got {count}")

        results = []
        seen = set()
        max_attempts = count * 100  # 防止无限循环
        attempts = 0

        # 循环调用单次生成并校验去重
        while len(results) < count and attempts < max_attempts:
            attempts += 1
            result = self.generate()

            # 对于可哈希类型，直接使用；对于不可哈希类型，转换为字符串进行比较
            if isinstance(result, (str, int, float, tuple)):
                result_key = result
            else:
                result_key = str(result)

            # 校验是否重复
            if result_key not in seen:
                seen.add(result_key)
                results.append(result)

        # 如果未达到所需数量
        if len(results) < count:
            if allow_duplicates:
                # 如果允许重复，继续生成直到达到所需数量
                while len(results) < count:
                    results.append(self.generate())
            else:
                raise ValueError(
                    f"Cannot generate {count} unique results. "
                    f"Only {len(results)} unique results were generated. "
                    f"Set allow_duplicates=True to allow duplicates."
                )

        return results


class ListBasedGenerator(BaseGenerator):
    """
    基于固定列表的生成器基类。
    支持概率权重、分组等高级功能。

    子类可以定义：
    - NAMES: 简单列表（向后兼容）
    - NAMES_WITH_WEIGHTS: 带权重的名字列表 [(name, weight), ...]
    - NAMES_BY_GROUP: 按组分组的名字字典 {group: [names]}
    - GROUP_WEIGHTS: 组的权重字典 {group: weight}
    """

    # 子类可以定义这些属性
    NAMES: List[str] = []
    NAMES_WITH_WEIGHTS: List[Tuple[str, float]] = []
    NAMES_BY_GROUP: Dict[str, List[str]] = {}
    GROUP_WEIGHTS: Dict[str, float] = {}

    def __init__(self, group: Optional[str] = None):
        """
        初始化生成器。

        Args:
            group: 如果指定，只从该组中选择名字
        """
        self.group = group
        self._validate_config()

    def _validate_config(self) -> None:
        """验证配置是否有效"""
        has_names = bool(self.NAMES)
        has_weights = bool(self.NAMES_WITH_WEIGHTS)
        has_groups = bool(self.NAMES_BY_GROUP)

        config_count = sum([has_names, has_weights, has_groups])
        if config_count == 0:
            raise ValueError(
                "Subclass must define at least one of: NAMES, NAMES_WITH_WEIGHTS, or NAMES_BY_GROUP"
            )
        if config_count > 1:
            raise ValueError(
                "Subclass should define only one of: NAMES, NAMES_WITH_WEIGHTS, or NAMES_BY_GROUP"
            )

    def _get_available_names(self) -> List[str]:
        """获取可用的名字列表"""
        if self.NAMES_BY_GROUP:
            if self.group:
                if self.group not in self.NAMES_BY_GROUP:
                    raise ValueError(
                        f"Group '{self.group}' not found in NAMES_BY_GROUP"
                    )
                return self.NAMES_BY_GROUP[self.group]
            else:
                # 返回所有组的名字
                all_names = []
                for names in self.NAMES_BY_GROUP.values():
                    all_names.extend(names)
                return all_names
        elif self.NAMES_WITH_WEIGHTS:
            return [name for name, _ in self.NAMES_WITH_WEIGHTS]
        else:
            return self.NAMES

    def _get_weighted_names(self) -> List[Tuple[str, float]]:
        """获取带权重的名字列表"""
        if self.NAMES_WITH_WEIGHTS:
            if self.group:
                # 如果指定了组，需要从 NAMES_BY_GROUP 中筛选
                if self.NAMES_BY_GROUP and self.group in self.NAMES_BY_GROUP:
                    group_names = set(self.NAMES_BY_GROUP[self.group])
                    return [
                        (name, weight)
                        for name, weight in self.NAMES_WITH_WEIGHTS
                        if name in group_names
                    ]
                else:
                    # 如果没有分组信息，返回所有
                    return self.NAMES_WITH_WEIGHTS
            return self.NAMES_WITH_WEIGHTS
        elif self.NAMES_BY_GROUP:
            # 从分组构建权重
            weighted = []
            if self.group:
                # 如果指定了组，只返回该组的名字
                if self.group not in self.NAMES_BY_GROUP:
                    raise ValueError(
                        f"Group '{self.group}' not found in NAMES_BY_GROUP"
                    )
                group_weight = self.GROUP_WEIGHTS.get(self.group, 1.0)
                for name in self.NAMES_BY_GROUP[self.group]:
                    weighted.append((name, group_weight))
            else:
                # 如果没有指定组，返回所有组的名字（带权重）
                for group, names in self.NAMES_BY_GROUP.items():
                    group_weight = self.GROUP_WEIGHTS.get(group, 1.0)
                    for name in names:
                        weighted.append((name, group_weight))
            return weighted
        else:
            # 简单列表，所有名字权重相等
            return [(name, 1.0) for name in self.NAMES]

    def generate(self, group: Optional[str] = None) -> str:
        """
        从列表中随机选择一个（支持概率权重和分组）。

        Args:
            group: 如果指定，只从该组中选择（临时覆盖初始化时的组）

        Returns:
            str: 随机选择的结果
        """
        # 临时使用指定的组
        original_group = self.group
        try:
            if group is not None:
                self.group = group

            weighted_names = self._get_weighted_names()
            if not weighted_names:
                raise ValueError("No names available for generation.")

            # 使用权重进行随机选择
            names, weights = zip(*weighted_names)
            return random.choices(names, weights=weights, k=1)[0]
        finally:
            self.group = original_group

    def generate_many(
        self, count: int, allow_duplicates: bool = False, group: Optional[str] = None
    ) -> List[str]:
        """
        生成多个不重复的结果（支持概率权重和分组）。

        Args:
            count: 要生成的数量
            allow_duplicates: 如果为 True，允许重复（当数量超过可用数据时）
            group: 如果指定，只从该组中选择（临时覆盖初始化时的组）

        Returns:
            List[str]: 生成的结果列表

        Raises:
            ValueError: 当 count 为负数或零时
            ValueError: 当 count 超过可用数据且 allow_duplicates=False 时
        """
        if count <= 0:
            raise ValueError(f"count must be positive, got {count}")

        # 临时使用指定的组
        original_group = self.group
        try:
            if group is not None:
                self.group = group

            available_names = self._get_available_names()
            unique_names = list(set(available_names))
            max_count = len(unique_names)

            if count > max_count and not allow_duplicates:
                raise ValueError(
                    f"Cannot generate {count} unique results. "
                    f"Only {max_count} unique names available. "
                    f"Set allow_duplicates=True to allow duplicates."
                )

            if count <= max_count:
                # 使用权重进行加权随机采样
                weighted_names = self._get_weighted_names()
                if weighted_names:
                    # 去重但保持权重（取最大权重）
                    unique_weighted = {}
                    for name, weight in weighted_names:
                        if (
                            name not in unique_weighted
                            or weight > unique_weighted[name]
                        ):
                            unique_weighted[name] = weight
                    unique_weighted_list = list(unique_weighted.items())
                    unique_names_list, unique_weights = zip(*unique_weighted_list)

                    # 使用权重进行选择（不重复）
                    results = []
                    seen = set()
                    available_names = list(unique_names_list)
                    available_weights = list(unique_weights)

                    while len(results) < count and available_names:
                        # 使用权重随机选择
                        selected = random.choices(
                            available_names, weights=available_weights, k=1
                        )[0]
                        results.append(selected)
                        seen.add(selected)

                        # 从可用列表中移除已选择的
                        idx = available_names.index(selected)
                        available_names.pop(idx)
                        available_weights.pop(idx)

                    return results
                else:
                    return random.sample(unique_names, count)
            else:
                # 如果允许重复，使用权重生成
                weighted_names = self._get_weighted_names()
                if weighted_names:
                    names, weights = zip(*weighted_names)
                    return random.choices(list(names), weights=list(weights), k=count)
                else:
                    results = unique_names.copy()
                    while len(results) < count:
                        results.append(random.choice(unique_names))
                    random.shuffle(results)
                    return results
        finally:
            self.group = original_group

    def get_groups(self) -> List[str]:
        """
        获取所有可用的组。

        Returns:
            List[str]: 组名列表
        """
        if self.NAMES_BY_GROUP:
            return list(self.NAMES_BY_GROUP.keys())
        return []
