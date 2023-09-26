class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.len = 0

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
        self.len += 1

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.len += 1

    def delete(self, data):
        if not self.head:
            return
        if self.head.data == data:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
        self.len -= 1

    def display(self):
        current = self.head
        while current:
            print(current.data, end=" -> ")
            current = current.next
        print("None")

    def change(self, data, index):
        if index < 0:
            print("index invalid!")
            return
        elif index == 0 and not self.head:
            self.head = Node(data)
            return
        elif index == 0 and self.head:
            print("list invalid!")
            return
        elif index >= self.len:
            print("index invalid!")
            return
        else:
            current = self.head
            for _ in range(index):
                current = current.next
            current.data = data

    def search(self, data):
        current = self.head
        while current:
            if current.data == data:
                print("found!")
                return
            current = current.next
        print("not found!")
        return False
        

linked_list = LinkedList()
linked_list.append(1)
linked_list.append(2)
linked_list.append(3)
linked_list.display()  # 输出: 1 -> 2 -> 3 -> None

linked_list.change(4, 1)
linked_list.prepend(0)
linked_list.display()  # 输出: 0 -> 1 -> 4 -> 3 -> None

linked_list.delete(2)
linked_list.display()  # 输出: 0 -> 1 -> 3 -> None

linked_list.search(3)  # 输出: found!