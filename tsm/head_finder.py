from ctypes import ArgumentError
from typing import List, Dict
import logging
from collections import defaultdict
from abc import ABCMeta, abstractmethod

from nltk import Tree

logger = logging.getLogger(__name__)


class HeadFinder(metaclass=ABCMeta):
    @abstractmethod
    def determine_head(self, t: Tree, parent: Tree) -> Tree:
        pass


class CopulaHeadFinder:
    @abstractmethod
    def makes_copula_head(self) -> bool:
        pass


class AbstractCollinsHeadFinder(HeadFinder, CopulaHeadFinder):
    """
    Construct a `HeadFinder`.
    The `categories_to_avoid` set categories which, if it comes to last resort
    processing (i.e., none of the rules matched), will be avoided as heads.
    In last resort processing, it will attempt to match the leftmost or rightmost
    constituent not in this set but will fall back to the left or rightmost
    constituent if necessary.

    # Parameters

    categories_to_avoid : `List[str]`
        Constituent types to avoid as head.
    """
    def __init__(self, categories_to_avoid: List[str]):
        self.non_terminal_info: Dict[str, List[List[str]]] = {}
        self.default_rule = None
        self.default_left_rule: List[str] = [""] * (len(categories_to_avoid) + 1)
        self.default_right_rule: List[str] = [""] * (len(categories_to_avoid) + 1)

        if len(categories_to_avoid.length) > 0:
            self.default_left_rule[0] = "leftexcept"
            self.default_right_rule[0] = "rightexcept"
            self.default_left_rule[1:] = categories_to_avoid
            self.default_right_rule[1:] = categories_to_avoid
        else:
            self.default_left_rule[0] = "left"
            self.default_right_rule[0] = "right"

    def makes_copula_head(self) -> bool:
        return False

    def determine_head(self, t: Tree, parent: Tree) -> Tree:
        if not self.non_terminal_info:
            raise ValueError("Classes derived from AbstractCollinsHeadFinder must create and fill Dict non_terminal_info.")

        if t is None or not isinstance(t, Tree):
            raise ArgumentError("Can't return head of null or leaf Tree.")

        logger.info("determine_head for " + t.label())

        if len(t) == 1:
            logger.info("Only one child determines " + t[0].label() + " as head of " + t.label());
            return t[0]

        return self.determine_non_trivial_head(t, parent)

    def determine_non_trivial_head(self, t: Tree, parent: Tree) -> Tree:
        the_head: Tree = None
        mother_category: str = t.label()
        if mother_category.startswith('@'):
            mother_category = mother_category[1:]

        logger.info("Looking for head of " + t.label())

        how: List[List[str]] = self.non_terminal_info.get(mother_category)
        if how is None:
            logger.info(
                f"Warning: No rule found for {mother_category} (first char: {mother_category[0]})"
            )
            if self.default_rule is not None:
                logger.info("Using default rule")
                return self.traverse_locate([subtree for subtree in t], self.default_rule, True)
            else:
                raise ArgumentError(
                    f"No head rule defined for {mother_category} using {self.__name__} in {t.pformat()}"
                )
        for i in range(len(how)):
            last_resort: bool = i == len(how) - 1
            the_head = self.traverse_locate([subtree for subtree in t], how[i], last_resort)
            if the_head is not None:
                break

        logger.info(f"  Chose {"null node" if theHead is None else the_head.label()}")
        return the_head

    def traverse_locate(self, daughter_trees: List[Tree], how: List[str], last_resort: bool) -> Tree:
        head_idx: int = 0
        if how[0] == "left":
            head_idx = self.find_left_head(daughter_trees, how)
        elif how[0] == "right":
            head_idx = self.find_right_head(daughter_trees, how)
        elif how[0] == "leftexcept":
            head_idx = self.find_left_except_head(daughter_trees, how)
        elif how[0] == "rightexcept":
            head_idx = self.find_right_except_head(daughter_trees, how)
        elif how[0] == "leftdis":
            raise NotImplementedError
        elif how[0] == "rightdis":
            raise NotImplementedError
        else:
            raise ArgumentError(f"ERROR: invalid direction type {how[0]} to non_terminal_info map in AbstractCollinsHeadFinder.")

        # what happens if our rule didn't match anything
        if head_idx < 0:
            if last_resort:
                # use the default rule to try to match anything except categories_to_avoid
                # if that doesn't match, we'll return the left or rightmost child (by
                # setting head_idx).  We want to be careful to ensure that post_operation_fix
                # runs exactly once.
                rule: str = None
                if how[0].startswith("left"):
                    head_idx = 0
                    rule = self.default_left_rule
                else:
                    head_idx = len(daughter_trees) - 1
                    rule = self.default_right_rule
                child = self.traverse_locate(daughter_trees, rule, False)
                if child is not None:
                    return child
                else:
                    return daughter_trees[head_idx]
            else:
                return None

        head_idx = self.post_operation_fix(head_idx, daughter_trees)
        return daughter_trees[head_idx]

    def find_left_head(self, daughter_trees: List[Tree], how: List[str]) -> int:
        head_idx: int = 0
        for i in range(1, len(how)):
            for head_idx in range(len(daughter_trees)):
                child_category: str = daughter_trees[head_idx].label()
                if how[i] == child_category:
                    return head_idx
        return -1

    def find_left_dis_head(self, daughter_trees: List[Tree], how: List[str]) -> int:
        for head_idx in range(len(daughter_trees)):
            child_category = daughter_trees[head_idx].label()
            for i in range(1, len(how)):
                if how[i] == child_category:
                    return head_idx
        return -1

    def find_left_except_head(self, daughter_trees: List[Tree], how: List[str]) -> int:
        for head_idx in range(len(daughter_trees)):
            child_category: str = daughter_trees[head_idx].label()
            if child_category not in how[1:]:
                return head_idx
        return -1

    def find_right_head(self, daughter_trees: List[Tree], how: List[str]) -> int:
        head_idx: int = 0
        for i in range(1, len(how)):
            for head_idx in range(len(daughter_trees)-1, -1, -1):
                child_category: str = daughter_trees[head_idx].label()
                if how[i] == child_category:
                    return head_idx
        return -1

    # from right, but search for any of the categories, not by category in turn
    def find_right_dis_head(self, daughter_trees: List[Tree], how: List[str]) -> int:
        for head_idx in range(len(daughter_trees)-1, -1, -1):
            child_category = daughter_trees[head_idx].label()
            for i in range(1, len(how)):
                if how[i] == child_category:
                    return head_idx
        return -1

    def find_right_except_head(self, daughter_trees: List[Tree], how: List[str]) -> int:
        for head_idx in range(len(daughter_trees)-1, -1, -1):
            child_category: str = daughter_trees[head_idx].label()
            if child_category not in how[1:]:
                return head_idx
        return -1

    def post_operation_fix(self, head_idx: int, daughter_trees: List[Tree]) -> int:
        return head_idx