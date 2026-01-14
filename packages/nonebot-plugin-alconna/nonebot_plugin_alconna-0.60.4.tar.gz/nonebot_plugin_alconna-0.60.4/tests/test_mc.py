def test_mc_style_text():
    from nonebot.adapters.minecraft.message import Message, MessageSegment
    from nonebot.adapters.minecraft.models import Color

    from nonebot_plugin_alconna import Text, UniMessage

    msg = UniMessage([Text("1234").color("red", 0, 2).color("yellow"), Text("456").color("blue")])

    assert msg.export_sync(adapter="Minecraft") == Message(
        [
            MessageSegment.text("12", color=Color.red),
            MessageSegment.text("34", color=Color.yellow),
            MessageSegment.text("456", color=Color.blue),
        ]
    )
