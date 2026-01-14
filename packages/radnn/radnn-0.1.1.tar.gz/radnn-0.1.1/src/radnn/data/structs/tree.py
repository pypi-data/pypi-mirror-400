# ......................................................................................
# MIT License

# Copyright (c) 2019-2026 Pantelis I. Kaplanoglou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ......................................................................................

# This implementation is ported from the Java/C# trees that have been developed by me
# for the lesson CS215 "Data Structures & Algorithms" at Anatolia American University.

import numpy as np

from typing import Type, Any, Callable, Optional, Iterable, Union, List


class TreeNodeList(list):
  """
  Python version of CTreeNodeList<T>:
  - inherits from list
  - enforces uniqueness and max_branching_factor in append_node
  """
  
  def __init__(self, max_branching_factor: int = np.inf):
    super().__init__()
    self._max_branching_factor = max_branching_factor
  
  @property
  def item_count(self) -> int:
    return len(self)
  
  @property
  def max_branching_factor(self) -> int:
    return self._max_branching_factor
  
  @max_branching_factor.setter
  def max_branching_factor(self, value: int) -> None:
    self._max_branching_factor = int(value)
  
  def contains(self, node: Type["TreeNode"]) -> bool:
    return node in self
  
  def append_node(self, node: Type["TreeNode"]) -> None:
    if node is None:
      return
    if len(self) >= self._max_branching_factor:
      return
    if node not in self:
      super().append(node)
  
  def remove_node(self, node: Type["TreeNode"]) -> None:
    if node in self:
      super().remove(node)
  
  def __str__(self) -> str:
    lines = []
    for n in self:
      # C# used "[{Value}]".PadRight(16) + " " + Path
      v = getattr(n, "value", None)
      left = f"[{v}]"
      left = left + (" " * max(0, 16 - len(left)))
      lines.append(f"{left} {n.path}")
    return "\r\n".join(lines)


class TreeNode(object):
  def __init__(self):
    
    self.name: str = ""
    self.index: int = -1
    self.value: Any = None
    self._parent: TreeNode | None = None
    self._children: TreeNodeList = TreeNodeList()
    
  # -------------------------
  # Properties (C#-like)
  # -------------------------
  @property
  def children(self) -> TreeNodeList:
    return self._children
  
  @property
  def parent(self) -> Type["TreeNode"] | None:
    return self._parent
  
  @parent.setter
  def parent(self, new_parent: Type["TreeNode"] | None):
    # Remove from current parent
    if self._parent is not None:
      self._parent.children.remove_node(self)
    
    self._parent = new_parent
    
    # Add to new parent
    if self._parent is not None:
      self._parent.children.append_node(self)
  
  @property
  def is_root(self) -> bool:
    return self._parent is None
  
  @property
  def is_leaf(self) -> bool:
    return self._children.item_count == 0
  
  @property
  def child_count(self) -> int:
    return len(self._children)
  
  def __getitem__(self, index: int) -> Type["TreeNode"] | None:
    try:
      return self._children[index]
    except IndexError:
      return None
  
  @property
  def level(self) -> int:
    if self._parent is None:
      return 0
    return self._parent.level + 1
  
  @property
  def root(self) -> Type["TreeNode"]:
    if self._parent is None:
      return self
    return self._parent.root
  
  @property
  def path(self) -> str:
    if self._parent is None:
      return "/"
    if self._parent.is_root:
      return self._parent.path + self.name
    return self._parent.path + "/" + self.name
  
  def new_child(self, node_name_or_id: Union[str, int, None] = None) -> Type["TreeNode"]:
    child = TreeNode()
    child.index = len(self._children) + 1
    if node_name_or_id is None:
      child.name = str(child.index)
    else:
      child.name = str(node_name_or_id)
    child.parent = self
    return child
  
  def add_child(self, child_node: Type["TreeNode"]) -> int:
    child_node.parent = self
    return self._children.item_count - 1
  
  def remove_child(self, child_or_name: Union[Type["TreeNode"], str]) -> None:
    if isinstance(child_or_name, TreeNode):
      child_or_name.parent = None
    else:
      name = str(child_or_name)
      for c in list(self.children):
        if c.name == name:
          c.parent = None
          break
    
  def delete(self) -> None:
    # Postorder delete: delete children first
    for c in list(self.children):
      c.delete()
    
    # Then remove self from parent
    if self._parent is not None:
      self._parent.remove_child(self)
  
  def __eq__(self, other: Type["TreeNode"]) -> bool:
    return self.name == other.name
  
  def __str__(self) -> str:
    return self.path




class TreeNodeQueue(list):
  @property
  def is_empty(self) -> bool:
    return len(self) == 0
  
  def enqueue(self, item: TreeNode) -> None:
    self.append(item)
  
  def peek(self) -> Optional[TreeNode]:
    return self[0] if len(self) == 0 else None
    
  def dequeue(self) -> Optional[TreeNode]:
    return self.pop[0] if len(self) == 0 else None



class Tree:
  def __init__(self, root: Optional[TreeNode] = None):
    self.root: TreeNode = root if root is not None else TreeNode()
    self._node_list: Optional[TreeNodeList] = None
    #self.comparison_by: Optional[Callable[[Any, Any], int]] = None  #TODO
  '''
  def compare(self, this_item: Any, other_item: Any) -> int:
    """
    Closest Python equivalent of C# compare(T,T):
    - If comparison_by provided, use it.
    - Else try normal Python comparisons.
    - If not comparable, return 1 (same default as C# code's nResult=1).
    """
    if self.comparison_by is not None:
      return int(self.comparison_by(this_item, other_item))
    
    try:
      if this_item == other_item:
        return 0
      # Python doesn't have CompareTo; approximate:
      return -1 if this_item < other_item else 1
    except Exception:
      return 1
  '''
  
  def clear(self) -> None:
    self.root.delete()
    self.root = TreeNode()
  
  def _recurse_preorder_append(self, current: TreeNode, depth: int) -> None:
    self._node_list.append_node(current)
    for child in current.children:
      self._recurse_preorder_append(child, depth + 1)
  
  def _recurse_postorder_append(self, current: TreeNode, depth: int) -> None:
    for child in current.children:
      self._recurse_postorder_append(child, depth + 1)
    self._node_list.append_node(current)
  
  def traverse_depth_first(self, is_preorder: bool = True) -> TreeNodeList:
    self._node_list = TreeNodeList()
    if is_preorder:
      self._recurse_preorder_append(self.root, 0)
    else:
      self._recurse_postorder_append(self.root, 0)
    return self._node_list
  
  def traverse_breadth_first(self) -> TreeNodeList:
    node_list = TreeNodeList()
    q = TreeNodeQueue()
    q.enqueue(self.root)
    
    while not q.is_empty:
      node = q.dequeue()
      if node is None:
        continue
      node_list.append_node(node)
      for child in node.children:
        q.enqueue(child)
    
    return node_list
  
  def _recurse_follow_path(self, path_names: list, current: TreeNode, depth: int) -> Optional[TreeNode]:
    next_name = path_names.pop(0)
    if next_name is None:
      return None
    
    for child in current.children:
      if child.name == next_name:
        if len(path_names) == 0:
          return child
        return self._recurse_follow_path(path_names, child, depth + 1)
    
    return None
  
  def follow(self, path: str) -> Optional[TreeNode]:
    # Split by '/'
    parts = path.split("/")
    
    q = list()
    for p in parts:
      q.append(p)
    
    # In an empty tree the result will be the root node
    result: Optional[TreeNode] = self.root
    if not q.is_empty:
      q.pop(0)  # remove "" representing root when path starts with "/"
      result = self._recurse_follow_path(q, self.root, 1)
    
    return result
  
  def _indent(self, depth: int) -> str:
    if depth - 1 >= 0:
      return " " * ((depth - 1) * 4)
    return ""
  
  def _recurse_node_description(self, current: Optional[TreeNode], depth: int) -> str:
    if current is None or not current.is_root:
      prefix = self._indent(depth) + "|__ "
    else:
      prefix = ">"
    
    if current is None:
      return prefix
    
    s = prefix + current.name
    for child in current.children:
      s += "\r\n" + self._recurse_node_description(child, depth + 1)
    return s
  
  def __str__(self) -> str:
    return self._recurse_node_description(self.root, 0)
