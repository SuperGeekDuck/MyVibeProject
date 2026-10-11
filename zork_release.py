

# -*- coding: utf-8 -*-
"""
简易中文版 Zork —— 《白房子的秘密》
运行：python zork_cn.py
目标：在房子下面的地窖里找到金色徽章
"""

import sys

# ===============================================================
# 输出工具
# ===============================================================

def say(text=""):
    """按 74 个半角宽度自动换行（中文字符按 2 宽计算）"""
    if text == "":
        print()
        return
    line, width = "", 0
    for ch in text:
        w = 2 if ord(ch) > 0x2E7F else 1
        if width + w > 74:
            print(line)
            line, width = ch, w
        else:
            line += ch
            width += w
    if line:
        print(line)


# ===============================================================
# 游戏数据
# ===============================================================

# 方向别名表
DIRS = {
    "北": ["北", "北边", "北面", "北方", "north", "n"],
    "南": ["南", "南边", "南面", "南方", "south", "s"],
    "东": ["东", "东边", "东面", "东方", "east", "e"],
    "西": ["西", "西边", "西面", "西方", "west", "w"],
    "上": ["上", "上边", "上面", "楼上", "上楼", "上去", "up", "u"],
    "下": ["下", "下边", "下面", "楼下", "下楼", "下去", "down", "d"],
}
DIR_ORDER = ["北", "南", "东", "西", "上", "下"]

# 物品表
ITEMS = {
    "黄铜钥匙": {
        "desc": "一把沉甸甸的黄铜钥匙，齿牙很粗，像是能打开某个老旧的锁。",
        "takeable": True,
    },
    "银币": {
        "desc": "一枚已经发黑的银币，正面刻着一只张牙舞爪的狮子。",
        "takeable": True,
    },
    "油灯": {
        "desc": "一盏铜制油灯，灯芯还湿润着，灯座里还剩小半盏灯油。"
                "要是有点火的东西就好了。",
        "takeable": True,
    },
    "面包": {
        "desc": "半块硬得像石头的黑面包。你不太想吃它。",
        "takeable": True,
    },
    "小刀": {
        "desc": "一把生锈的削皮小刀，勉强还算锋利。",
        "takeable": True,
    },
    "火柴": {
        "desc": "一小盒火柴，盒子受潮发软，好在里面还剩几根干燥的。",
        "takeable": True,
    },
    "宝箱": {
        "desc": "一个沉重的橡木箱，箱盖上钉着铁皮，锁扣早就锈断了。",
        "takeable": False,
        "openable": True,
        "loot": ["金色徽章"],
        "open_text": "你掀开箱盖，一股霉味扑面而来，箱底躺着什么东西，微微反光。",
    },
    "金色徽章": {
        "desc": "一枚巴掌大的金色徽章，上面浮雕着一座白色房子。它沉甸甸的，散发着温润的光。",
        "takeable": True,
    },
}

# 房间表
ROOMS = {
    "门厅": {
        "desc": "你站在白房子的门厅里。黑白相间的棋盘格地砖在脚下延伸，"
                "墙上的穿衣镜蒙着厚厚的灰，只照出你模糊的影子。"
                "北边是一扇半掩的木门，南边垂着一道墨绿色的门帘，东边通向厨房。"
                "楼梯下方，还有一扇沉重的木门。",
        "exits": {
            "北": "书房",
            "南": "客厅",
            "东": "厨房",
            "下": {
                "to": "地下室",
                "lock": "黄铜钥匙",
                "locked_text": "楼梯下的木门挂着一把黄铜大锁，锁得严严实实。",
                "unlock_text": "你把黄铜钥匙插进锁孔，用力一转——咔哒。木门开了。",
            },
        },
        "items": [],
    },
    "书房": {
        "desc": "书房四壁都是顶到天花板的书架，书脊上的烫金早已剥落。"
                "屋子中央摆着一张胡桃木写字台，抽屉半开着，积了厚厚一层灰。"
                "南边是来时的门。",
        "exits": {"南": "门厅"},
        "items": ["黄铜钥匙"],
    },
    "客厅": {
        "desc": "客厅里摆着一圈蒙着白布的高背椅，壁炉里堆着冷透的灰烬。"
                "墙角的落地钟停了，指针凝固在三点十七分。北边通回门厅。",
        "exits": {"北": "门厅"},
        "items": ["银币", "油灯"],
    },
    "厨房": {
        "desc": "厨房的台面上落满灰尘，铜锅倒扣在架子上。"
                "一块硬邦邦的黑面包搁在案板边，旁边还丢着一把生锈的小刀。"
                "灶台边上有只小铁盒，看着像是火柴。"
                "西边通回门厅。",
        "exits": {"西": "门厅"},
        "items": ["面包", "小刀", "火柴"],
    },
    "地下室": {
        "desc": "地下室又潮又暗，空气里有股铁锈和陈年泥土的味道。"
                "一缕光从楼梯口斜斜射下来，正好照亮地上的一个橡木箱。"
                "你听见水滴落下的声音，一下，又一下。",
        "dark": True,
        "dark_desc": "四周黑得伸手不见五指，只有楼梯口透下来一缕微光。"
                     "你听见水滴落下的声音，一下，又一下。",
        "exits": {"上": "门厅"},
        "items": ["宝箱"],
    },
}

# ===============================================================
# 玩家状态
# ===============================================================

player = {"room": "门厅", "bag": []}


# ===============================================================
# 基础工具
# ===============================================================

def find_item(text, names):
    """在名字列表里找出玩家指的那个东西（支持模糊匹配）"""
    if not text:
        return None
    for n in names:                      # 完全匹配优先
        if n == text:
            return n
    for n in names:                      # 再尝试包含匹配
        if text in n or n in text:
            return n
    return None


def parse_dir(text):
    """把「去北边」「向北走」「北」都解析成「北」"""
    t = text
    for p in ("去", "往", "向", "朝", "走", "到", "进", "回", "爬"):
        t = t.replace(p, "")
    for d, aliases in DIRS.items():
        if t in aliases:
            return d
    return None


def has_light():
    """玩家现在有没有亮着的油灯（随身或在本房间）"""
    if not ITEMS["油灯"].get("lit"):
        return False
    if "油灯" in player["bag"]:
        return True
    return "油灯" in ROOMS[player["room"]]["items"]


def too_dark():
    """当前房间太黑，看不清东西"""
    return ROOMS[player["room"]].get("dark") and not has_light()


# ===============================================================
# 各种动作
# ===============================================================

def look():
    """环顾四周"""
    r = ROOMS[player["room"]]
    say()
    say("【%s】" % player["room"])
    if too_dark():
        say(r["dark_desc"])
    else:
        say(r["desc"])
        if r["items"]:
            say("这里的东西：" + "、".join(r["items"]))
    exits = [d for d in DIR_ORDER if d in r["exits"]]
    say("出口：" + "、".join(exits))


def go(room_name):
    player["room"] = room_name
    look()


def do_move(d):
    """朝某个方向走"""
    room = ROOMS[player["room"]]
    if d not in room["exits"]:
        say("那边没有出口。")
        return

    ex = room["exits"][d]
    if isinstance(ex, str):              # 普通出口
        go(ex)
        return

    # 上锁的出口
    if ex.get("unlocked"):
        go(ex["to"])
        return

    key = ex.get("lock")
    if key and key in player["bag"]:
        ex["unlocked"] = True
        say(ex["unlock_text"])
        go(ex["to"])
    else:
        say(ex["locked_text"])


def do_examine(target):
    """检查物品"""
    if too_dark():
        say("太黑了，你什么也看不清。")
        return
    if not target:
        say("你想看什么？")
        return
    room_items = ROOMS[player["room"]]["items"]
    name = find_item(target, room_items) or find_item(target, player["bag"])
    if name is None:
        say("你看不到「%s」。" % target)
        return
    say(ITEMS[name]["desc"])


def do_take(target):
    """捡起物品"""
    if too_dark():
        say("太黑了，你什么也看不清。")
        return
    if not target:
        say("你想拿什么？")
        return
    room_items = ROOMS[player["room"]]["items"]
    name = find_item(target, room_items)
    if name is None:
        in_bag = find_item(target, player["bag"])
        if in_bag:
            say("你身上已经有「%s」了。" % in_bag)
        else:
            say("这里没有「%s」。" % target)
        return

    if not ITEMS[name].get("takeable"):
        say("「%s」太重了，你搬不动。" % name)
        return

    room_items.remove(name)
    player["bag"].append(name)
    say("你拿起了「%s」。" % name)

    if name == "金色徽章":
        win()


def do_drop(target):
    """放下物品"""
    if not target:
        say("你想放下什么？")
        return
    name = find_item(target, player["bag"])
    if name is None:
        say("你身上没有「%s」。" % target)
        return
    player["bag"].remove(name)
    ROOMS[player["room"]]["items"].append(name)
    say("你放下了「%s」。" % name)


def do_bag():
    """查看背包"""
    if not player["bag"]:
        say("你身上什么也没有。")
    else:
        say("你身上带着：" + "、".join(player["bag"]))


def do_open(target):
    """打开容器"""
    if too_dark():
        say("太黑了，你什么也看不清。")
        return
    if not target:
        say("你想打开什么？")
        return

    room_items = ROOMS[player["room"]]["items"]
    name = find_item(target, room_items) or find_item(target, player["bag"])
    if name is None:
        say("这里没有「%s」。" % target)
        return

    it = ITEMS[name]
    if it.get("opened"):
        say("「%s」已经打开了。" % name)
        return
    if not it.get("openable"):
        say("「%s」打不开。" % name)
        return

    it["opened"] = True
    say(it.get("open_text", "你打开了「%s」。" % name))

    loot = it.get("loot", [])
    if loot:
        for thing in loot:
            if name in room_items:
                room_items.append(thing)
            else:
                player["bag"].append(thing)
        say("里面是：" + "、".join(loot) + "。")


def do_light(target):
    """点燃东西"""
    if not target:
        say("你想点燃什么？")
        return
    room_items = ROOMS[player["room"]]["items"]
    name = find_item(target, room_items) or find_item(target, player["bag"])
    if name is None:
        say("这里没有「%s」。" % target)
        return
    if name != "油灯":
        say("「%s」点不着。" % name)
        return
    if ITEMS["油灯"].get("lit"):
        say("油灯已经亮着了。")
        return
    if "火柴" not in player["bag"]:
        say("你身上没有火。")
        return
    ITEMS["油灯"]["lit"] = True
    say("你划亮一根火柴，小心地点燃油灯。火苗晃了两下，稳稳地立住了，"
        "暖黄的光晕慢慢散开，把四周照得清清楚楚。")


def show_help():
    say()
    say("可用指令：")
    say("  看 / 环顾 .................. 观察四周")
    say("  北 / 南 / 东 / 西 / 上 / 下 .. 朝某个方向走")
    say("      （也可以说「去北边」「向北走」）")
    say("  检查 <东西> ................ 仔细看一件东西")
    say("  拿 <东西> .................. 把东西捡起来")
    say("  放下 <东西> ................ 把东西放在地上")
    say("  打开 <东西> ................ 打开箱子之类的容器")
    say("  点燃 <东西> ................ 用火柴点着油灯")
    say("  背包 ....................... 看看身上带了什么")
    say("  帮助 / 退出")


def win():
    say()
    say("=" * 36)
    say("金色徽章在你手心里沉甸甸地发热。")
    say("恍惚间，你仿佛看见白房子的窗户一扇接一扇亮起了灯，")
    say("很远的地方，有人在喊你的名字。")
    say()
    say("你找到了白房子的秘密 —— 游戏胜利！")
    say("=" * 36)
    sys.exit(0)


# ===============================================================
# 指令解析
# ===============================================================

# 动词前缀表（长前缀放在前面，避免被短前缀截断）
VERBS = [
    (("检查", "查看", "打量", "端详", "研究", "看看", "看"), do_examine),
    (("拿起", "捡起", "拾起", "拿走", "拿取", "带上", "拿", "捡", "取", "拾"), do_take),
    (("放下", "丢弃", "扔掉", "扔下", "扔", "丢", "放"), do_drop),
    (("打开", "揭开", "开"), do_open),
    (("点燃", "点亮", "点着", "点"), do_light),
]


def handle(raw):
    """处理一条输入，返回 False 表示退出游戏"""
    cmd = raw.strip()
    for ch in " \t，。！？!?,.":
        cmd = cmd.replace(ch, "")
    cmd = cmd.replace("　", "")
    if not cmd:
        return True