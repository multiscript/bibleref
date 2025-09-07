from collections.abc import MutableSequence, Iterable
from typing import Any

from bibleref import BibleRefException

class SimpleGroupView:
    '''A view of a group (subset) of items in the LinkedList.
    
    Iterating over a SimpleGroupView returns the individual items in the view. A SimpleGroupView can be indexed
    for get, set, and delete operations:

    `value = group_view[2]`

    `group_view[2] = value`

    `del group_view[2]`
    '''
    def __init__(self, parent: 'SimpleGroupedList', group_index: int):
        self._parent = parent
        if group_index < 0:
            group_index += len(self._parent._group_starts)
        if group_index < 0 or group_index>= len(self._parent._group_starts):
            raise IndexError(f"Group index {group_index} out of range")
        self._group_index = group_index
    
    @property
    def _start_item_index(self):
        return self._parent._group_starts[self._group_index]
    
    def __len__(self):
        if self._group_index == len(self._parent._group_starts) - 1:
            # This is the last group
            return len(self._parent._items) - self._start_item_index
        else:  
            return self._parent._group_starts[self._group_index + 1] - self._start_item_index

    def __iter__(self):
        '''Yields each item in the view.'''
        for item_index in range(self._start_item_index, self._start_item_index + len(self)):
            yield self._parent._items[item_index]

    def _conform_item_index(self, index) -> int:
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError(f"Group item index {index} out of range")
        return index

    def __getitem__(self, index):
        index = self._conform_item_index(index)
        return self._parent._items[self._start_item_index + index]

    def __setitem__(self, index, value):
        index = self._conform_item_index(index)
        self._parent._items[self._start_item_index + index] = value

    def __delitem__(self, index):
        index = self._conform_item_index(index)
        del self._parent._items[self._start_item_index + index]
    
    def __repr__(self):
        return f"SimpleGroupView({str(self)})"

    def __str__(self):
        return str(list(self))


class SimpleGroupViews:
    '''A read-only collection of `SimpleGroupView` objects.
    
    Iterating over a`GroupViews` collection returns each individual `GroupView`. `len(group_views)`
    gives the collection length. The collection can be indexed to return a particular
    `GroupView`: e.g. `group_views[2]`
    '''
    def __init__(self, parent: 'SimpleGroupedList'):
        self._parent = parent

    def __len__(self):
        return len(self._parent._group_starts)

    def __iter__(self):
        '''Yields a `GroupedList.GroupView` for each group in the list.'''
        for group_index in range(len(self)):
            yield SimpleGroupView(self._parent, group_index)

    def __getitem__(self, group_index):
        return SimpleGroupView(self._parent, group_index)

    def __repr__(self):
        return f"SimpleGroupViews({str(self)})"

    def __str__(self):
        return str(list(self))


class SimpleGroupedList(MutableSequence):
    '''A simplified version of GroupedList, using Python lists internally.
    '''
    def __init__(self, iterable: Iterable | None = None):
        '''Creates a new `SimpleGroupedList` and adds any items in `iterable` to this list. If `iterable` is None, the
        new `SimpleGroupedList` is empty.
        
        If the items of `iterable` are Python lists or tuples, each element of `iterable` is added as a
        separate group.'''
        self._items: list = []
        self._group_starts: list[int] = [] # Indices of self._items that start a new group.
        if iterable is None:
            return
        for item in iterable:
            if isinstance(item, list) or isinstance(item, tuple):
                self.append_group(item)
            else:
                self.append(item)
    
    @property
    def groups(self) -> 'SimpleGroupViews':
        '''Returns the `GroupViews` collection for this list.'''
        return SimpleGroupViews(self)

    def _conform_item_index(self, index) -> int:
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError(f"Item index {index} out of range")
        return index

    def _check_type(self, value):
        '''Subclasses can override to raise an exception if the provided
        value is not of a certain type.
        '''
        pass

    def to_nested_lists(self):
        '''Returns this `SimpleGroupedList` represented as a regular Python list of groups, which are in turn a regular
        list of the group's values.'''
        outer_list = []
        for group in self.groups:
            inner_list = []
            for item in group:
                inner_list.append(item)
            outer_list.append(inner_list)
        return outer_list
    
    def index(self, value, start: int=0, stop: int | None = None) -> int:
        if stop is None:
            stop = len(self._items)
        return self._items.index(value, start, stop) 

    def count(self, value):
        return self._items.count(value)
    
    def clear(self):
        '''Removes all items and groups from this list.'''
        self._items.clear()
        self._group_starts.clear()

    def clear_groups(self):
        '''Clears all existing groups. If the list is not empty, puts all existing items into a single new
        group.'''
        if len(self._items) > 0:
            self._group_starts = [0]
        else:
            self._group_starts.clear()

    def reverse(self) -> None:
        '''Reverses the items of this list in-place.
        
        For simplicity, this also clears all existing groups and places all existing items in one new group.
        '''
        self._items.reverse()
        self.clear_groups()

    def insert(self, index: int, value, new_group: bool = False):
        '''Inserts `value` into this list at the given `index`.'''
        self._check_type(value)
        index = self._conform_item_index(index)
        self._items.insert(index, value)
        if len(self._items) == 1:
            # First item in the list
            self._group_starts = [0]
            return
        
        # Adjust group starts
        prev_group_index = -1
        for i in range(len(self._group_starts)):
            if self._group_starts[i] < index:
                prev_group_index = i
            else:
                self._group_starts[i] += 1
        if new_group:
            self._group_starts.insert(prev_group_index + 1, index)

    def pop(self, index: int=-1):
        '''Removes the item at the given `index`, and returns its value.'''
        index = self._conform_item_index(index)
        value = self._items.pop(index)

        # Adjust group starts
        group_index = -1
        for i in range(len(self._group_starts)):
            if self._group_starts[i] == index:
                # The item being removed is the start of a group
                # Try pushing the group start forward one item
                if (i == len(self._group_starts) - 1) or self._group_starts[i + 1] == index + 1:
                    # There is no space to push the group start forward, so remove the group
                    del self._group_starts[i]
                    i -= 1
                else:
                    # Push the group start forward one item.
                    # This is achieved already simply by removing the item, but not updating the group start.
                    pass
            elif self._group_starts[i] > index:
                self._group_starts[i] -= 1
        return value

    def prepend(self, value, new_group: bool = False):
        '''Inserts `value` at the start of this list.
        
        If `new_group` is true, the `value` forms a new group.'''
        self.insert(0, value, new_group=new_group)

    def append(self, value, new_group: bool = False):
        '''Inserts `value` at the end of this list.
        
        If `new_group` is true, the `value` forms a new group.'''
        self.insert(len(self), value, new_group=new_group)
               
    def append_group(self, iterable):
        '''Appends each item of `iterable` to the end of this list.
        
        The new items all form a single new group.'''
        is_first_item = True
        for item in iterable:
            self.append(item, new_group=is_first_item)
            is_first_item = False

    def extend(self, values: Iterable):
        '''Appends each item of `values` to the end of this list.'''
        for item in values:
            self.append(item)

    def insert_group_at(self, index: int):
        '''If a group already starts in `index`, does nothing. Otherwise, starts a new group at `index`.'''
        index = self._conform_item_index(index)
        # Adjust group starts
        prev_group_index = -1
        for i in range(len(self._group_starts)):
            if self._group_starts[i] < index:
                prev_group_index = i
            elif self._group_starts[i] == index:
                # A group already starts here
                return
            else:
                break
        self._group_starts.insert(prev_group_index + 1, index)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Index must be an int")
        return self._items[index]

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise TypeError("Index must be an int")
        self._check_type(value)
        self._items[index] = value

    def __delitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Index must be an int")
        self.pop(index)

 