from collections.abc import MutableSequence, Iterable

from bibleref import BibleRefException


#
# This linked list is derived from the implementation in the python-ranges module
# at https://github.com/Superbird11/ranges, under the MIT Licence
#
class GroupedList(MutableSequence):
    '''A linked-list, with the ability to also group items.
    
    A group is a view of a subset of the list. By default, all items are placed in one
    group. All items belong to one group only, such that the collection of groups spans
    the entire list. (The current implementation defines groups by marking the first
    item in each group, but this should not be relied upon.)

    As groups are just views of the items, updating an item in a group also updates
    the main list, and vice verse.

    The groups property returns a GroupsView collection, which can be indexed and iterated
    over. Each iteration returns GroupView, which can be indexed and iterated over to return
    the items in the group.
    
    Groups are created by calling append_group(), or append() or prepend() with new_group
    set to True.

    This linked-list implementation is derived from [python-ranges](https://github.com/Superbird11/ranges)
    module, under the MIT Licence.
    '''
    class _Node:
        '''Nodes of the linked list.
        
        Groups are defined by setting node.is_group_head to True for the first node
        of the group. The group continues until the next group head.
        '''
        def __init__(self, value, prev=None, next=None, parent=None):
            self.value = value
            self.parent: 'GroupedList' = parent
            self.prev: 'GroupedList._Node' = prev
            self.next: 'GroupedList._Node' = next
            self.is_group_head: bool = False  # True if this node is the start of a group.
            self.prev_head: 'GroupedList._Node' = None # If this is a group head, link to next group head.
            self.next_head: 'GroupedList._Node' = None # If this is a group head, link to prev group head.

        def clear_group_head(self):
            self.is_group_head = False
            self.prev_head = None
            self.next_head = None

        def __eq__(self, other):
            return self.value.__eq__(other.value)

        def __lt__(self, other):
            return self.value.__lt__(other.value)

        def __gt__(self, other):
            return self.value.__gt__(other.value)

        def __ge__(self, other):
            return self.value.__ge__(other.value)

        def __le__(self, other):
            return self.value.__le__(other.value)

        def _id(self, obj):
            return id(obj) if obj is not None else None

        def __repr__(self):
            return str(self)

        def __str__(self):
            group = f" G {self._id(self.prev_head)} {id(self)} {self._id(self.next_head)}" if self.is_group_head else ""
            return f"Node({str(self.value)}{group})"

    class GroupViews:
        '''A read-only collection of `GroupView` objects.
        
        Iterating over a`GroupViews` collection returns each individual `GroupView`. `len(group_views)`
        gives the collection length. The collection can be indexed to return a particular
        `GroupView`: e.g. `group_views[2]`
        '''
        def __init__(self, parent: 'GroupedList'):
            self.parent = parent

        def _conform_group_index(self, group_index: int) -> int:
            ''' Check the group index is within range. If negative, convert to its
            positive equivalent. Return the resulting index.
            '''
            if group_index < 0:
                group_index += self.parent._group_count
            if group_index >= self.parent._group_count:
                raise IndexError(f"Group index {group_index} out of range")
            return group_index

        def _group_at(self, group_index: int) -> 'GroupedList._Node':
            group_index = self._conform_group_index(group_index)
            group_head = self.parent._first_head
            for i in range(group_index):
                group_head = group_head.next_head
            return group_head

        def __len__(self):
            return self.parent._group_count

        def __iter__(self):
            '''Yields a `GroupedList.GroupView` for each group in the list.'''
            group_head = self.parent._first_head
            while group_head is not None:
                yield GroupedList.GroupView(group_head)
                group_head = group_head.next_head

        def __getitem__(self, group_index):
            group_head = self._group_at(group_index)
            return GroupedList.GroupView(group_head)

        def __repr__(self):
            return f"GroupViews({str(self)})"

        def __str__(self):
            return str(list(self))

    class GroupView:
        '''A view of a group (subset) of items in the LinkedList.
        
        Iterating over a GroupView returns the individual items in the view. A GroupView can be indexed
        for get, set, and delete operations:

        `value = group_view[2]`

        `group_view[2] = value`

        `del group_view[2]`
        '''
        def __init__(self, group_head: 'GroupedList._Node'):
            self.group_head = group_head

        def _check_group_head(self):
            if not self.group_head.is_group_head or self.group_head.parent is None:
                raise GroupViewError("GroupView has been modified")

        def __len__(self):
            count = 0
            for item in self:
                count += 1
            return count

        def __iter__(self):
            '''Yields each item in the view.'''
            self._check_group_head()
            node = self.group_head
            yield node.value
            while node.next is not None and not node.next.is_group_head:
                node = node.next
                yield node.value

        def _node_at(self, index) -> 'GroupedList._Node':
            if index < 0:
                raise IndexError(f"Groups don't accept negative indices")
            self._check_group_head()
            node = self.group_head
            for i in range(index):
                node = node.next
                if node is None or node.is_group_head:
                    raise IndexError(f"List index {i+1} out of range")
            return node

        def __getitem__(self, index):
            self._check_group_head()
            return self._node_at(index).value

        def __setitem__(self, index, value):
            self._check_group_head()
            self.group_head.parent._check_type(value)
            self._node_at(index).value = value

        def __delitem__(self, index):
            self._check_group_head()
            node = self._node_at(index)
            self.group_head.parent._pop_node(node)
        
        def __repr__(self):
            return f"GroupView({str(self)})"

        def __str__(self):
            return str(list(self))

    def __init__(self, iterable: Iterable = None):
        '''Creates a new `GroupedList` and adds the items in `iterable` to this list.
        
        If the items of `iterable` are Python lists or tuples, each element of `iterable` is added as a
        separate group.'''
        self.clear()
        if iterable is None:
            return
        for item in iterable:
            if isinstance(item, list) or isinstance(item, tuple):
                self.append_group(item)
            else:
                self.append(item)

    def _check_type(self, value):
        '''Subclasses can override to raise an exception if the provided
        value is not of a certain type.
        '''
        pass

    def _check_is_child(self, node: _Node):
        if not isinstance(node, GroupedList._Node) or node.parent is not self:
            raise ValueError(f"List is not the parent of this node: {node}")

    def _conform_index(self, index: int) -> int:
        ''' Check the index is within range. If negative, convert to its
        positive equivalent. Return the resulting index.
        '''
        if index < 0:
            index += self._node_count
        if index >= self._node_count:
            raise IndexError(f"List index {index} out of range")
        return index

    def _node_at(self, index: int) -> 'GroupedList._Node':
        index = self._conform_index(index)
        if index <= self._node_count // 2:
            # Node is closer to the start, so search from there
            node = self._first
            for i in range(index):
                node = node.next
            return node
        else:
            # Node is closer to the end, so seach from there
            node = self._last
            for i in range(self._node_count - index - 1):
                node = node.prev
            return node

    def _insert_first(self, value):
        '''Inserts `value` as the first item of the list.'''
        self._first = self._Node(value, parent=self)
        self._last = self._first
        self._node_count += 1
        # First node also forms the head of the first group
        self._setup_single_group()

    def _setup_single_group(self):
        '''Sets up the first group of the list.
        
        Assumes there are no existing groups.'''
        if len(self) > 0:
            self._first.is_group_head = True
            self._first.prev_head = None
            self._first.next_head = None
            self._first_head = self._first
            self._last_head = self._first
            self._group_count = 1

    def _insert_before(self, node: 'GroupedList._Node', value, new_group: bool = False):
        '''Inserts `value` in the list before `node`.'''
        self._check_is_child(node)
        inserting_first = True if node is self._first else None
        new = self._Node(value, prev=node.prev, next=node, parent=self)
        if node.prev is not None:
            node.prev.next = new
        node.prev = new
        if node is self._first:
            self._first = new
        self._node_count += 1

        if new_group:
            if inserting_first:
                # New node becomes new stand-alone group at start of list
                self._insert_new_group_before_head(new, keep_existing_head=True)
            else:
                # New node breaks up an existing group to start a new group
                self._insert_new_group_at_node(new)
        else:
            if new.next is not None and new.next.is_group_head:
                # New node displaces the existing head of an existing group
                self._insert_new_group_before_head(new, keep_existing_head=False)
            else:
                # New node will automatically become part of an existing group
                pass

    def _insert_after(self, node: 'GroupedList._Node', value, new_group: bool = False):
        '''Inserts `value` in the list after `node`.'''
        self._check_is_child(node)
        inserting_last = True if node is self._last else None
        new = self._Node(value, prev=node, next=node.next, parent=self)
        if node.next is not None:
            node.next.prev = new
        node.next = new
        if node is self._last:
            self._last = new
        self._node_count += 1

        if new_group:
            self._insert_new_group_at_node(new)

    def _insert_new_group_before_head(self, node: 'GroupedList._Node', keep_existing_head: bool = False):
        old_head = node.next
        node.is_group_head = True
        node.prev_head = old_head.prev_head
        if old_head.prev_head is not None:
            old_head.prev_head.next_head = node

        if keep_existing_head:
            node.next_head = old_head
            old_head.prev_head = node
            self._group_count += 1
        else:
            node.next_head = old_head.next_head
            if old_head.next_head is not None:
                old_head.next_head.prev_head = node
            elif self._last_head is old_head:
                self._last_head = node
            old_head.clear_group_head()
        if self._first_head is old_head:
            self._first_head = node

    def _insert_new_group_at_node(self, node: 'GroupedList._Node'):
        if node is self._first:
            # First node is always already a group.
            return
        node.is_group_head = True
        prev_group_head = self._find_group_head(node.prev)
        node.prev_head = prev_group_head
        node.next_head = prev_group_head.next_head
        if prev_group_head.next_head is not None:
            prev_group_head.next_head.prev_head = node
        prev_group_head.next_head = node
        if self._last_head is prev_group_head:
            self._last_head = node
        self._group_count += 1

    def _find_group_head(self, node: 'GroupedList._Node') -> 'GroupedList._Node':
        '''Search for the next group head, beginning at `node`, and returning the group head node.'''
        while node is not None and not node.is_group_head:
            node = node.prev
        return node

    def _pop_node(self, node: 'GroupedList._Node'):
        '''Remove `node` from this list, and returns the node's value.'''
        self._check_is_child(node)
        if self._node_count == 1:
            # pop only element
            self._first = None
            self._last = None
            self._first_head = None
            self._last_head = None
        elif node is self._first:
            # pop from start
            self._first = node.next
            self._first.prev = None
        elif node is self._last:
            # pop at end
            self._last = self._last.prev
            self._last.next = None
        else:
            # pop from somewhere in middle
            node.prev.next = node.next
            node.next.prev = node.prev
        
        node.parent = None
        self._node_count -= 1

        if node.is_group_head:
            # Try pushing the group head forward one node
            if node.next is None or node.next.is_group_head:
                # The next node either doesn't exist or is already the start of another group.
                # Either way we're losing the group this node belongs to.
                self._group_count -= 1
                next_head_link = node.next_head
                prev_head_link = node.prev_head
            else:
                # We can successfully push the group head forward to the next node
                node.next.is_group_head = True
                node.next.prev_head = node.prev_head
                node.next.next_head = node.next_head
                next_head_link = node.next
                prev_head_link = node.next

            if self._first_head is node:
                self._first_head = next_head_link
            if self._last_head is node:
                self._last_head = prev_head_link
            if node.prev_head is not None:
                node.prev_head.next_head = next_head_link
            if node.next_head is not None:
                node.next_head.prev_head = prev_head_link
            node.clear_group_head()

        return node.value

    def _pop_before(self, node: 'GroupedList._Node'):
        '''Remove the node before this `node` from this list, and return's the value of the popped node.'''
        self._check_is_child(node)
        if node is self._first:
            raise IndexError("Can't pop before first node")
        return self._pop_node(node.prev)

    def _pop_after(self, node: 'GroupedList._Node'):
        '''Remove the node after this `node` from this list, and returns the value of the popped node.'''
        self._check_is_child(node)
        if node is self._last:
            raise IndexError("Can't pop after last node")
        return self._pop_node(node.next)

    def _node_iter(self):
        '''Return an iterator that yields the nodes in this list.'''
        node = self._first
        while node is not None:
            yield node
            node = node.next

    @property
    def groups(self) -> GroupViews:
        '''Returns the `GroupViews` collection for this list.'''
        return GroupedList.GroupViews(self)
    
    def to_nested_lists(self):
        '''Returns this `GroupedList` represented as a regular Python list of groups, which are in turn a regular
        list of the group's values.'''
        outer_list = []
        for group in self.groups:
            inner_list = []
            for item in group:
                inner_list.append(item)
            outer_list.append(inner_list)
        return outer_list

    def index(self, value, min_index: int = None, limit_index: int =None):
        '''Returns the index of the first occurrence of `value` in the list, at or after `min_index`
        and before `limit_index`.'''
        if min_index is None:
            min_index = 0
        if limit_index is None:
            limit_index = self._node_count
        self._check_type(value)
        min_index = self._conform_index(min_index)
        limit_index = self._conform_index(limit_index-1) + 1
        if min_index > limit_index: # Swap
            (limit_index, min_index) = (min_index, limit_index)
        node: GroupedList._Node = self._first
        for index in range(limit_index):
            if node.value == value and index >= min_index:
                return index
            node = node.next
        # At this point item not found
        raise ValueError(f"Value {value} not found in list")        
            
    def count(self, value):
        '''Returns the total number of occurrences of `value` in this list.'''
        self._check_type(value)
        count = 0
        for node_value in self:
            if node_value == value:
                count += 1
        return count         

    def prepend(self, value, new_group: bool = False):
        '''Inserts `value` at the start of this list.
        
        If `new_group` is true, the `value` forms a new group.'''
        self._check_type(value)
        if self._node_count == 0:
            self._insert_first(value)
        else:
            self._insert_before(self._first, value, new_group)

    def append(self, value, new_group: bool = False):
        '''Inserts `value` at the end of this list.
        
        If `new_group` is true, the `value` forms a new group.'''
        self._check_type(value)
        if self._node_count == 0:
            self._insert_first(value)
        else:
            self._insert_after(self._last, value, new_group)
               
    def append_group(self, iterable):
        '''Appends each item of `iterable` to the end of this list.
        
        The new items all form a single new group.'''
        is_first_item = True
        for item in iterable:
            self.append(item, new_group=is_first_item)
            is_first_item = False

    def extend(self, iterable):
        '''Appends each item of `iterable` to the end of this list.'''
        for item in iterable:
            self.append(item)

    def insert(self, index: int, value):
        '''Inserts `value` into this list at the given `index`.'''
        self._check_type(value)
        if index == 0:
            self.prepend(value)
        elif index == self._node_count:
            self.append(value)
        else:
            self._insert_before(self._node_at(index), value)

    def insert_group_at(self, index: int = None):
        index = self._conform_index(index)
        self._insert_new_group_at_node(self._node_at(index))

    def pop(self, index: int = None):
        '''Removes the item at the given `index`, and returns its value.'''
        if index is None:
            index = self._node_count - 1
        index = self._conform_index(index)
        return self._pop_node(self._node_at(index))

    def remove(self, value):
        '''Removes the first occurence of the given `value` from this list.'''
        self._check_type(value)
        node = self._first
        while node is not None:
            if node.value == value:
                self._pop_node(node)
                return
            node = node.next
        # At this point item not found
        raise ValueError(f"Value {value} not found in list")        

    def clear(self):
        '''Removes all items from the list.'''
        self._first: GroupedList._Node = None          # First node
        self._last: GroupedList._Node = None           # Last node
        self._node_count: int = 0                    # Count of nodes
        self._first_head: GroupedList._Node = None     # First node that is a group head
        self._last_head: GroupedList._Node = None      # Last node that is a group head
        self._group_count: int = 0                   # Count of groups

    def clear_groups(self):
        '''Clears all existing groups and replaces them with a single new group containing all the items
        in the list.'''
        for node in self._node_iter():
            node.clear_group_head()
        self._setup_single_group()

    def reverse(self):
        '''Reverses the items of this list in-place.
        
        For simplicity, this also clears all existing groups and places all list items in one new group.
        '''
        if self._node_count == 0:
            return
        node = self._last
        while node is not None:
            (node.next, node.prev) = (node.prev, node.next) # Swap next and prev links
            # Clear groups:
            node.clear_group_head()
            node = node.next
        (self._first, self._last) = (self._last, self._first) # Swap first and last links
        self._setup_single_group()

    #
    # Sort-related methods
    #

    def sort(self):
        '''Sorts this list in-place. All existing groups are cleared and replaced with a single
        new group.'''
        (self._first, self._last) = self._merge_sort(self._first, clear_group_heads=True)
        self._setup_single_group()

    def _merge_sort(self, first_node: 'GroupedList._Node', clear_group_heads=False):
        '''Sorts a list beginning with `first_node`, and returns a tuple of (new_first_node, new_last_node).
        '''
        if first_node is None or first_node.next is None:
            return (first_node, first_node)
        
        first_node_A = first_node
        first_node_B = self._split(first_node, clear_group_heads)
        (first_node_A, last_node_A) = self._merge_sort(first_node_A, clear_group_heads=False)
        (first_node_B, last_node_B) = self._merge_sort(first_node_B, clear_group_heads=False)

        (new_first_node, new_last_node) = self._merge_sublists(first_node_A, last_node_A, 
                                                               first_node_B, last_node_B)
        return (new_first_node, new_last_node)

    def _split(self, first_node: 'GroupedList._Node', clear_group_heads=False):
        '''Given the first node of a sublist, splits the list in half and returns the first
        node of the second half.'''
        slow_node = first_node
        if clear_group_heads:
            slow_node.clear_group_head()
        fast_node = first_node.next

        while fast_node is not None:
            if clear_group_heads:
                fast_node.clear_group_head()            
            fast_node = fast_node.next
            if fast_node is not None:
                if clear_group_heads:
                    fast_node.clear_group_head()            
                slow_node = slow_node.next
                fast_node = fast_node.next
        
        first_node_B = slow_node.next
        slow_node.next = None
        first_node_B.prev = None
        return first_node_B

    def _merge_sublists(self, first_node_A: 'GroupedList._Node', last_node_A: 'GroupedList._Node',
                              first_node_B: 'GroupedList._Node', last_node_B: 'GroupedList._Node'):
        '''Combines two sublists (A and B) into a single sorted list. Returns a tuple of
        (new_first_node, new_last_node)'''
        if first_node_A is None:
            return (first_node_B, last_node_B)
        if first_node_B is None:
            return (first_node_A, last_node_A)
        
        if first_node_A <=  first_node_B: # Nodes compare using their values
            (next_first_node, new_last_node) = self._merge_sublists(first_node_A.next, last_node_A,
                                                                    first_node_B, last_node_B)
            first_node_A.next = next_first_node
            next_first_node.prev = first_node_A
            first_node_A.prev = None
            return (first_node_A, new_last_node)
        else: # first_node_B is less than first_node_A
            (next_first_node, new_last_node) = self._merge_sublists(first_node_A, last_node_A,
                                                                    first_node_B.next, last_node_B)
            first_node_B.next = next_first_node
            next_first_node.prev = first_node_B
            first_node_B.prev = None
            return (first_node_B, new_last_node)

    #
    # End of sort-related methods
    #

    def __len__(self):
        return self._node_count
    
    def __iter__(self):
        node = self._first
        while node is not None:
            yield node.value
            node = node.next

    def __eq__(self, other) -> bool:
        return self.equals(other)

    def equals(self, other_iterable, compare_groups=True) -> bool:
        '''Returns `True` if each item in this list equals the corresponding item in `other_iterable`,
        otherwise `False`.
        
        If `compare_groups` is `True`, `other_iterable` must also be a `GroupedList` and the groups of the
        two lists must match, otherwise returns `False`.'''
        if len(self) != len(other_iterable):
            return False
        if compare_groups:
            if not isinstance(other_iterable, GroupedList):
                return False
            if self._group_count != other_iterable._group_count:
                return False
            self_groups = list(self.groups)
            other_groups = list(other_iterable.groups)
            for i in range(len(self_groups)):
                try:
                    for self_item, other_item in zip(list(self_groups[i]), list(other_groups[i]), strict=True):
                        if self_item != other_item:
                            return False
                except ValueError:
                    return False
        else:
            for self_item, other_item in zip(self, other_iterable):
                if self_item != other_item:
                    return False
        return True

    def __contains__(self, value):
        self._check_type(value)
        for node_value in self:
            if node_value == value:
                return True
        # At this point item not found
        return False
 
    def __getitem__(self, index: int):
        return self._node_at(index).value

    def __setitem__(self, index: int, value):
        self._check_type(value)
        self._node_at(index).value = value

    def __delitem__(self, index: int):
        self.pop(index)

    def __reversed__(self):
        node = self._last
        while node is not None:
            yield node.value
            node = node.prev

    def __iadd__(self, iterable):
        self.extend(iterable)
        return self
    
    def __repr__(self):
        return f"GroupedList({str(self)})"

    def __str__(self):
        return str(self.to_nested_lists())


class GroupViewError(BibleRefException):
    '''Raised when a no-longer-valid GroupView is accessed.'''




