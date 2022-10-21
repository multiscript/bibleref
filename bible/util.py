from collections.abc import MutableSequence


# Derived from https://github.com/Superbird11/ranges/blob/master/ranges/_helper.py (MIT Licence)
class _LinkedList(MutableSequence):
    '''A linked list, with the ability to also group items.

    Groups are accessed using the groups property and created using append_group().
    '''    
    class Node:
        def __init__(self, value, prev=None, next=None, parent=None):
            self.value = value
            self.prev = prev
            self.next = next
            self.is_group_head: bool = False  # True if this node is the start of a group.
            self.prev_head = None # If this is a group head, link to next group head.
            self.next_head = None # If this is a group head, link to prev group head.
            self.parent = parent

        def __eq__(self, other):
            return self.value.__eq__(other.data)

        def __lt__(self, other):
            return self.value.__lt__(other.data)

        def __gt__(self, other):
            return self.value.__gt__(other.data)

        def __ge__(self, other):
            return self.value.__ge__(other.data)

        def __le__(self, other):
            return self.value.__le__(other.data)

        def __str__(self):
            return f"Node({str(self.value)})"

        def __repr__(self):
            return str(self)

    def __init__(self, iterable=None):
        self._first = None          # First node
        self._last = None           # Last node
        self._node_count = 0        # Count of nodes
        self._first_head = None     # First node that is a group head
        self._last_head = None      # Last node that is a group head
        self._group_count = 0       # Count of groups
        if iterable is not None:
            self.extend(iterable)

    def _check_type(self, value):
        '''Subclasses can override to raise an exception if the provided
        value is not of a certain type.
        '''
        pass

    def _check_is_child(self, node):
        if not isinstance(node, _LinkedList.Node) or node.parent is not self:
            raise ValueError(f"List is not the parent of this node: {node}")

    def _conform_index(self, index):
        ''' Check the index is within range. If negative, convert to its
        positive equivalent. Return the resulting index.
        '''
        if index < 0:
            index += self._node_count
        if index >= self._node_count:
            raise IndexError(f"List index {index} out of range")
        return index

    def _node_at(self, index):
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
        self._first = self.Node(value, parent=self)
        self._last = self._first
        self._node_count += 1

    def _insert_before(self, node, value):
        self._check_is_child(node)
        if node is self._first:
            self.prepend(value)
        else:
            new = self.Node(value, prev=node.prev, next=node, parent=self)
            node.prev.next = new
            node.prev = new
            self._node_count += 1

    def _insert_after(self, node, value):
        self._check_is_child(node)
        if node is self._last:
            self.append(value)
        else:
            new = self.Node(value, prev=node, next=node.next, parent=self)
            node.next.prev = new
            node.next = new
            self._node_count += 1

    def _pop_node(self, node):
        self._check_is_child(node)
        # pop only element
        if self._node_count == 1:
            self._first = None
            self._last = None
            self._first_head = None
            self._last_head = None
            self._group_count = 0
        # pop from start
        elif node is self._first:
            self._first = node.next
            self._first.prev = None
        # pop at end
        elif node is self._last:
            self._last = self._last.prev
            self._last.next = None
        else:
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
                if self._first_head is node:
                    self._first_head = node.next_head
                if self._last_head is node:
                    self._last_head = node.prev_head
                if node.prev_head is not None:
                    node.prev_head.next_head = node.next_head
                if node.next_head is not None:
                    node.next_head.prev_head = node.prev_head
            else:
                node.next.is_group_head = True
                node.next.prev_head = node.prev_head
                node.next.next_head = node.next_head

        return node.value

    def _pop_before(self, node):
        self._check_is_child(node)
        if node is self._first:
            raise IndexError("Can't pop before first node")
        return self._pop_node(node.prev)

    def _pop_after(self, node):
        self._check_is_child(node)
        if node is self._last:
            raise IndexError("Can't pop after last node")
        return self._pop_node(node.next)

    def index(self, value, min_index=None, limit_index=None):
        if min_index is None:
            min_index = 0
        if limit_index is None:
            limit_index = self._node_count
        self._check_type(value)
        min_index = self._conform_index(min_index)
        limit_index = self._conform_index(limit_index-1) + 1
        if min_index > limit_index: # Swap
            (limit_index, min_index) = (min_index, limit_index)
        node: _LinkedList.Node = self._first
        for index in range(limit_index):
            if node.value == value and index >= min_index:
                return index
            node = node.next
        # At this point item not found
        raise ValueError(f"Value {value} not found in list")        
            
    def count(self, value):
        self._check_type(value)
        count = 0
        for node_value in self:
            if node_value == value:
                count += 1
        return count         

    def prepend(self, value):
        self._check_type(value)
        if self._node_count == 0:
            self._insert_first(value)
        else:
            new = self.Node(value, next=self._first, parent=self)
            self._first.prev = new
            self._first = new
            self._node_count += 1

    def append(self, value):
        self._check_type(value)
        if self._node_count == 0:
            self._insert_first(value)
        else:
            new = self.Node(value, prev=self._last, parent=self)
            self._last.next = new
            self._last = new
            self._node_count += 1
    
    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def insert(self, index, value):
        self._check_type(value)
        if index == 0:
            self.prepend(value)
        elif index == self._node_count:
            self.append(value)
        else:
            self._insert_before(self._node_at(index), value)

    def pop(self, index=None):
        if index is None:
            index = self._node_count - 1
        index = self._conform_index(index)
        return self._pop_node(self._node_at(index))

    def remove(self, value):
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
        self._first = None
        self._last = None
        self._length = 0

    def reverse(self):
        '''For simplicity, this also clears any groups.
        '''
        if self._node_count == 0:
            return
        node = self._last
        while node is not None:
            (node.next, node.prev) = (node.prev, node.next) # Swap next and prev links
            # Clear groups:
            node.is_group_head = False
            node.prev_head = None
            node.next_head = None
            node = node.next
        (self._first, self._last) = (self._last, self._first) # Swap first and last links
        node._first_head = None
        self._last_head = None
        self._group_count = 0

    def __len__(self):
        return self._node_count
    
    def __iter__(self):
        node = self._first
        while node is not None:
            yield node.value
            node = node.next

    def __contains__(self, value):
        self._check_type(value)
        for node_value in self:
            if node_value == value:
                return True
        # At this point item not found
        return False
 
    def __getitem__(self, index):
        return self._node_at(index).value

    def __setitem__(self, index, value):
        self._check_type(value)
        self._node_at(index).value = value

    def __delitem__(self, index):
        self.pop(index)

    def __reversed__(self):
        node = self._last
        while node is not None:
            yield node.value
            node = node.prev

    def __iadd__(self, iterable):
        self.extend(iterable)
        return self
