import unittest

from bible.util import LinkedList, ListError


class TestLinkedList(unittest.TestCase):    
    def test_construction(self):
        self.assertListEqual(list(LinkedList()), [])
        self.assertListEqual(list(LinkedList([1])), [1])
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3, 10])
    
    def test_conform_index(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertEqual(test_list._conform_index(-2), -2 + len(test_list))
        self.assertRaises(IndexError, lambda: test_list._conform_index(len(test_list)))
    
    def test_node_at(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertIs(test_list._node_at(0), test_list._first)
        self.assertIs(test_list._node_at(-1), test_list._last)
        self.assertIs(test_list._node_at(2), test_list._first.next.next)
    
    def test_insert_first(self):
        test_list = LinkedList()
        test_list._insert_first(6)
        self.assertIs(test_list._first, test_list._last)
        self.assertEqual(test_list._first.value, 6)
        self.assertEqual(len(test_list), 1)
    
    def test_insert_before(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        test_list._insert_before(test_list._node_at(3), 12)
        self.assertListEqual(list(test_list), [5, 8, 2, 12, 7, 3, 10])
        test_list._insert_before(test_list._node_at(0), 14)
        self.assertListEqual(list(test_list), [14, 5, 8, 2, 12, 7, 3, 10])  

    def test_insert_after(self):
        test_list = LinkedList([5,8,2,7,3,10])
        test_list._insert_after(test_list._node_at(3), 12)
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 12, 3, 10])
        test_list._insert_after(test_list._node_at(-1), 14)
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 12, 3, 10, 14])

    def test_pop_node(self):
        test_list = LinkedList([1])
        value = test_list._pop_node(test_list._node_at(0))
        self.assertEqual(value, 1)
        self.assertListEqual(list(test_list), [])
        self.assertEqual(len(test_list), 0)

        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        value = test_list._pop_node(test_list._node_at(0))
        self.assertEqual(value, 5)
        self.assertListEqual(list(test_list), [8, 2, 7, 3, 10])
        self.assertEqual(len(test_list), 5)
        value = test_list._pop_node(test_list._node_at(-1))
        self.assertEqual(value, 10)
        self.assertListEqual(list(test_list), [8,2,7,3])
        self.assertEqual(len(test_list), 4)

    def test_pop_before(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertRaises(IndexError, lambda: test_list._pop_before(test_list._node_at(0)))
        value = test_list._pop_before(test_list._node_at(3))
        self.assertEqual(value, 2)
        self.assertListEqual(list(test_list), [5, 8, 7, 3, 10])

    def test_pop_after(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertRaises(IndexError, lambda: test_list._pop_after(test_list._node_at(-1)))
        value = test_list._pop_after(test_list._node_at(2))
        self.assertEqual(value, 7)
        self.assertListEqual(list(test_list), [5,8,2,3,10])

    def test_prepend(self):
        test_list = LinkedList()
        test_list.prepend(1)
        self.assertListEqual(list(test_list), [1])
        test_list.prepend(2)
        self.assertListEqual(list(test_list), [2, 1])

    def test_append(self):
        test_list = LinkedList()
        test_list.append(1)
        self.assertListEqual(list(test_list), [1])
        test_list.append(2)
        self.assertListEqual(list(test_list), [1, 2])

    def test_insert(self):
        test_list = LinkedList()
        test_list.insert(0, 1)
        self.assertListEqual(list(test_list), [1])
        test_list.insert(0, 2)
        test_list.insert(1, 3)
        self.assertListEqual(list(test_list), [2, 3, 1])
        test_list.insert(3, 4)
        self.assertListEqual(list(test_list), [2, 3, 1, 4])

    def test_index(self):
        test_list = LinkedList([5, 3, 6, 3, 1, 7, 1, 6, 9, 3])
        self.assertEqual(test_list.index(3), 1)
        self.assertEqual(test_list.index(3, 2), 3)
        self.assertEqual(test_list.index(3, 4, len(test_list)), 9)
        self.assertRaises(ValueError, lambda: test_list.index(3, 4, -1))

    def test_count(self):
        test_list = LinkedList([5, 3, 6, 3, 1, 7, 1, 6, 9, 3])
        self.assertEqual(test_list.count(5), 1)
        self.assertEqual(test_list.count(3), 3)
        self.assertEqual(test_list.count(6), 2)
        self.assertEqual(test_list.count(1), 2)
        self.assertEqual(test_list.count(10), 0)
    
    def test_pop(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        value = test_list.pop()
        self.assertEqual(value, 10)
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3])
        value = test_list.pop(0)
        self.assertEqual(value, 5)
        self.assertListEqual(list(test_list), [8, 2, 7, 3])
        value = test_list.pop(2)
        self.assertEqual(value, 7)
        self.assertListEqual(list(test_list), [8, 2, 3])

    def test_clear(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        test_list.clear()
        self.assertListEqual(list(test_list), [])
    
    def test_len(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertEqual(len(test_list), 6)

    def test_len(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertTrue(2 in test_list)
        self.assertFalse(9 in test_list)
        
    def test_get_set(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertEqual(test_list[0], 5)
        self.assertEqual(test_list[5], 10)
        self.assertEqual(test_list[3], 7)
        test_list[0] = 20
        test_list[5] = 30
        test_list[3] = 40
        self.assertEqual(test_list[0], 20)
        self.assertEqual(test_list[5], 30)
        self.assertEqual(test_list[3], 40)

    def test_del(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        del test_list[0]
        self.assertListEqual(list(test_list), [8, 2, 7, 3, 10])
        del test_list[4]
        self.assertListEqual(list(test_list), [8, 2, 7, 3])
        del test_list[2]
        self.assertListEqual(list(test_list), [8, 2, 3])

    def test_reversed(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        self.assertListEqual(list(reversed(test_list)), [10, 3, 7, 2, 8, 5])

    def test_extend(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        test_list.extend([12, 9, 20])
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3, 10, 12, 9, 20])
    
    def test_remove(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10, 2])
        test_list.remove(2)
        self.assertListEqual(list(test_list), [5, 8, 7, 3, 10, 2])

    def test_reverse(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        test_list.reverse()
        self.assertListEqual(list(test_list), [10, 3, 7, 2, 8, 5])

    def test_iadd(self):
        test_list = LinkedList([5, 8, 2, 7, 3, 10])
        test_list += [12, 9, 20]
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3, 10, 12, 9, 20])

    def test_group_construction(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        test_list.append_group([3, 7, 5])
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 6], [3, 7, 5]])

    def test_groups_view(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        test_list.append_group([3, 7, 5])
        self.assertEqual(len(test_list.groups), 3)
        self.assertEqual(test_list.groups[2].group_head.value, 3)
        group_list = list(test_list.groups)
        self.assertEqual(group_list[0].group_head.value, 2)
        self.assertEqual(group_list[1].group_head.value, 1)
        self.assertEqual(group_list[2].group_head.value, 3)

    def test_group_view(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        test_list.append_group([3, 7, 5])
        group_0 = test_list.groups[0]
        self.assertEqual(group_0[0], 2)
        self.assertEqual(group_0[1], 8)
        self.assertEqual(group_0[2], 4)

        self.assertEqual(test_list.groups[2][0], 3)
        self.assertEqual(test_list.groups[2][1], 7)
        self.assertEqual(test_list.groups[2][2], 5)

    def test_group_head_deletion(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        test_list.append_group([3, 7, 5])
        group_1 = test_list.groups[1]
        group_2 = test_list.groups[2]
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 6], [3, 7, 5]])
        self.assertEqual(len(test_list.groups), 3)
        self.assertEqual(group_1[0], 1)
        self.assertEqual(group_2[0], 3)

        del test_list[3]
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [9, 6], [3, 7, 5]])
        self.assertEqual(len(test_list.groups), 3)
        self.assertRaises(ListError, lambda: group_1[0])
        self.assertEqual(group_2[0], 3)

        del test_list[3]
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [6], [3, 7, 5]])
        self.assertEqual(len(test_list.groups), 3)
        self.assertRaises(ListError, lambda: group_1[0])
        self.assertEqual(group_2[0], 3)

        del test_list[3]
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [3, 7, 5]])
        self.assertEqual(len(test_list.groups), 2)
        self.assertRaises(ListError, lambda: group_1[0])
        self.assertEqual(group_2[0], 3)

        del test_list[3]
        del test_list[3]
        del test_list[3]
        self.assertEqual(len(test_list.groups), 1)
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4]])

    def test_group_prepend(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 6]])
        test_list.prepend(3, new_group=False)
        self.assertEqual(test_list.to_nested_lists(), [[3, 2, 8, 4], [1, 9, 6]])
        test_list.prepend(7, new_group=True)
        self.assertEqual(test_list.to_nested_lists(), [[7], [3, 2, 8, 4], [1, 9, 6]])

    def test_group_insert_before(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(3))

        test_list._insert_before(test_list._node_at(3), 7, new_group=False)
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [7, 1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(3))

        test_list._insert_before(test_list._node_at(3), 5, new_group=True)
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [5], [7, 1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(4))

        test_list._insert_before(test_list._node_at(2), 3, new_group=False)
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 3, 4], [5], [7, 1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(5))

        test_list._insert_before(test_list._node_at(2), 10, new_group=True)
        self.assertEqual(test_list.to_nested_lists(), [[2, 8], [10, 3, 4], [5], [7, 1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(6))

        test_list = LinkedList([5])
        test_list._insert_before(test_list._node_at(0), 6, new_group=False)
        self.assertEqual(test_list.to_nested_lists(), [[6, 5]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(0))

    def test_group_pop_node(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(3))
        test_list.pop(0)
        self.assertEqual(test_list.to_nested_lists(), [[8, 4], [1, 9, 6]])
        self.assertIs(test_list._first_head, test_list._node_at(0))
        self.assertIs(test_list._last_head, test_list._node_at(2))

    def test_group_item_modify(self):
        test_list = LinkedList()
        test_list.append_group([2, 8, 4])
        test_list.append_group([1, 9, 6])
        test_list.append_group([3, 7, 5])
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 6], [3, 7, 5]])
        test_list.groups[1][2] = 20
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9, 20], [3, 7, 5]])

        del test_list.groups[1][2]
        self.assertEqual(test_list.to_nested_lists(), [[2, 8, 4], [1, 9], [3, 7, 5]])

    def test_group_equals(self):
        list_1 = LinkedList()
        list_1.append_group([1, 2, 3])
        list_1.append_group([4, 5, 6])
        list_1.append_group([7, 8])
        list_1.append_group([9, 10])
        list_2 = LinkedList()
        list_2.append_group([1, 2, 3])
        list_2.append_group([4, 5, 6])
        list_2.append_group([7, 8, 9])
        list_2.append_group([10])
        self.assertFalse(list_1.equals(list_2, compare_groups=True))
        self.assertTrue(list_1.equals(list_2, compare_groups=False))

        list_3 = LinkedList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        list_4 = LinkedList([1, 2, 3, 4, 5, 6, 7, 8, 9, 11])
        self.assertFalse(list_3 == list_4)
    
    def test_basic_sort(self):
        values = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5]
        test_list = LinkedList(values)
        test_list.sort()
        self.assertEqual(test_list, LinkedList(sorted(values)))
        self.assertEqual(test_list._first.value, 1)
        self.assertEqual(test_list._last.value, 10)
        self.assertTrue(self.verify_is_single_group(test_list))

    def test_sort_of_groups(self):
        test_list = LinkedList()
        test_list.append_group([12, 3, 20])
        test_list.append_group([18, 5, 11])
        test_list.append_group([1, 8])
        test_list.append_group([15])
        test_list.append_group([2, 6, 14])
        test_list.sort()
        self.assertEqual(test_list, LinkedList([1, 2, 3, 5, 6, 8, 11, 12, 14, 15, 18, 20]))
        self.assertEqual(test_list._first.value, 1)
        self.assertEqual(test_list._last.value, 20)
        self.assertTrue(self.verify_is_single_group(test_list))

    def verify_is_single_group(self, linked_list: LinkedList):
        first = True
        for node in linked_list._node_iter():
            if first:
                if linked_list._first_head is not node:
                    return False
                if linked_list._last_head is not node:
                    return False
            if node.is_group_head != first:
                return False
            if node.prev_head is not None or node.next_head is not None:
                return False
            first = False
        return True

    

