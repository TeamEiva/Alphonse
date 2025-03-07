# Copyright (C) 2020 KenHV

from sqlalchemy.exc import IntegrityError

from userbot import CMD_HELP, bot
from userbot.events import register

fban_replies = [
    "New FedBan",
    "Starting a federation ban",
    "Start a federation ban",
    "FedBan Reason update",
    "FedBan reason updated",
    "has already been fbanned, with the exact same reason.",
]

unfban_replies = ["New un-FedBan", "I'll give", "Un-FedBan"]


@register(outgoing=True, disable_edited=True, pattern=r"^\.(d)?fban(?: |$)(.*)")
async def fban(event):
    """Bans a user from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    match = event.pattern_match.group(2)

    if event.is_reply:
        reply_msg = await event.get_reply_message()
        fban_id = reply_msg.sender_id

        if event.pattern_match.group(1) == "d":
            await reply_msg.delete()

        reason = match
    else:
        pattern = match.split()
        fban_id = pattern[0]
        reason = " ".join(pattern[1:])

    try:
        fban_id = await event.client.get_peer_id(fban_id)
    except Exception:
        pass

    if event.sender_id == fban_id:
        return await event.edit(
            "**Error: This action has been prevented by KensurBot self preservation protocols.**"
        )

    fed_list = get_flist()
    if len(fed_list) == 0:
        return await event.edit("**You haven't connected to any federations yet!**")

    user_link = f"[{fban_id}](tg://user?id={fban_id})"

    await event.edit(f"**Fbanning** {user_link}...")
    failed = []
    total = 0

    for i in fed_list:
        total += 1
        chat = int(i.chat_id)
        try:
            async with bot.conversation(chat) as conv:
                await conv.send_message(f"/fban {user_link} {reason}")
                reply = await conv.get_response()
                await bot.send_read_acknowledge(
                    conv.chat_id, message=reply, clear_mentions=True
                )

                if all(i not in reply.text for i in fban_replies):
                    failed.append(i.fed_name)
        except Exception:
            failed.append(i.fed_name)

    reason = reason or "Not specified."

    if failed:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += f"• {i}\n"
    else:
        status = f"Success! Fbanned in {total} feds."

    await event.edit(
        f"**Fbanned **{user_link}!\n**Reason:** {reason}\n**Status:** {status}"
    )


@register(outgoing=True, disable_edited=True, pattern=r"^\.unfban(?: |$)(.*)")
async def unfban(event):
    """Unbans a user from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    match = event.pattern_match.group(1)
    if event.is_reply:
        unfban_id = (await event.get_reply_message()).sender_id
        reason = match
    else:
        pattern = match.split()
        unfban_id = pattern[0]
        reason = " ".join(pattern[1:])

    try:
        unfban_id = await event.client.get_peer_id(unfban_id)
    except:
        pass

    if event.sender_id == unfban_id:
        return await event.edit("**Wait, that's illegal**")

    fed_list = get_flist()
    if len(fed_list) == 0:
        return await event.edit("**You haven't connected to any federations yet!**")

    user_link = f"[{unfban_id}](tg://user?id={unfban_id})"

    await event.edit(f"**Un-fbanning **{user_link}**...**")
    failed = []
    total = 0

    for i in fed_list:
        total += 1
        chat = int(i.chat_id)
        try:
            async with bot.conversation(chat) as conv:
                await conv.send_message(f"/unfban {user_link} {reason}")
                reply = await conv.get_response()
                await bot.send_read_acknowledge(
                    conv.chat_id, message=reply, clear_mentions=True
                )

                if all(i not in reply.text for i in unfban_replies):
                    failed.append(i.fed_name)
        except Exception:
            failed.append(i.fed_name)

    reason = reason or "Not specified."

    if failed:
        status = f"Failed to un-fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += f"• {i}\n"
    else:
        status = f"Success! Un-fbanned in {total} feds."

    reason = reason or "Not specified."
    await event.edit(
        f"**Un-fbanned** {user_link}!\n**Reason:** {reason}\n**Status:** {status}"
    )


@register(outgoing=True, pattern=r"^\.addf(?: |$)(.*)")
async def addf(event):
    """Adds current chat to connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import add_flist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    fed_name = event.pattern_match.group(1)
    if not fed_name:
        return await event.edit("**Pass a name in order connect to this group!**")

    try:
        add_flist(event.chat_id, fed_name)
    except IntegrityError:
        return await event.edit(
            "**This group is already connected to federations list.**"
        )

    await event.edit("**Added this group to federations list!**")


@register(outgoing=True, pattern=r"^\.delf$")
async def delf(event):
    """Removes current chat from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import del_flist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    del_flist(event.chat_id)
    await event.edit("**Removed this group from federations list!**")


@register(outgoing=True, pattern=r"^\.listf$")
async def listf(event):
    """List all connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    fed_list = get_flist()
    if len(fed_list) == 0:
        return await event.edit("**You haven't connected to any federations yet!**")

    msg = "**Connected federations:**\n\n"

    for i in fed_list:
        msg += f"• {i.fed_name}\n"

    await event.edit(msg)


@register(outgoing=True, disable_edited=True, pattern=r"^\.clearf$")
async def clearf(event):
    """Removes all chats from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import del_flist_all
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    del_flist_all()
    await event.edit("**Disconnected from all connected federations!**")


CMD_HELP.update(
    {
        "fban": ">`.fban <id/username> <reason>`"
        "\nUsage: Bans user from connected federations."
        "\nYou can reply to the user whom you want to fban or manually pass the username/id."
        "\n`.dfban` does the same but deletes the replied message."
        "\n\n`>.unfban <id/username> <reason>`"
        "\nUsage: Same as fban but unbans the user"
        "\n\n>`.addf <name>`"
        "\nUsage: Adds current group and stores it as <name> in connected federations."
        "\nAdding one group is enough for one federation."
        "\n\n>`.delf`"
        "\nUsage: Removes current group from connected federations."
        "\n\n>`.listf`"
        "\nUsage: Lists all connected federations by specified name."
        "\n\n>`.clearf`"
        "\nUsage: Disconnects from all connected federations. Use it carefully."
    }
)
