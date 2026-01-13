from re_common.v2.baselibrary.tools.tree_processor.node import TreeNode


def build_forest(node_list):
    nodes = {}  # cid -> TreeNode
    has_parent = set()

    # 第一步：创建所有节点
    for cid, pid, count in node_list:
        node = TreeNode(cid, count)
        nodes[cid] = node
        if pid is not None:
            has_parent.add(cid)

    # 第二步：连接 parent-child
    for cid, pid, _ in node_list:
        if pid is not None and pid in nodes:
            parent = nodes[pid]
            child = nodes[cid]
            parent.children.append(child)
            child.parent = parent

    # 第三步：找所有根节点（即没有 parent 的）
    roots = [node for cid, node in nodes.items() if node.parent is None]
    return roots  # 返回多棵树的根节点列表
