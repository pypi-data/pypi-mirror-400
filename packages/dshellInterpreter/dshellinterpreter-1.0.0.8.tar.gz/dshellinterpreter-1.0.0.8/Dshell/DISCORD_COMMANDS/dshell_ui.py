from Dshell.full_import import (ButtonStyle,
                           PrivateChannel,
                           Interaction,
                           Button,
                           EasyModifiedViews,
                           CustomIDNotFound)

from .._DshellParser.ast_nodes import UiNode, CodeNode

from .._DshellInterpreteur.utils_interpreter import regroupe_commandes

from .._DshellInterpreteur.dshell_scope import new_scope

from Dshell.full_import import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur


ButtonStyleValues: tuple = tuple(i.name for i in ButtonStyle)
print(ButtonStyleValues)

async def build_ui_parameters(ui_node: UiNode, interpreter: "DshellInterpreteur"):
    """
    Builds the parameters for a UI component from the UiNode.
    Can accept buttons and select menus.
    :param ui_node:
    :param interpreter:
    :return:
    """
    for ident_component in range(len(ui_node.buttons)):
        regrouped_parameters = await regroupe_commandes(ui_node.buttons[ident_component].body, interpreter, normalise=True)
        args_button: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

        code = args_button.pop('code', None)
        style = args_button.pop('style', 'primary').lower()
        custom_id = args_button.pop('custom_id', str(ident_component))

        if code is not None and not isinstance(code, CodeNode):
            raise TypeError(f"Button code muste be a CodeNode or None, not {type(code)}")

        if not isinstance(custom_id, str):
            raise TypeError(f"Button custom_id must be a string, not {type(custom_id)} !")

        if style not in ButtonStyleValues:
            raise ValueError(f"Button style must be one of {', '.join(ButtonStyleValues)}, not '{style}' !")

        args_button['custom_id'] = custom_id
        args_button['style'] = ButtonStyle[style]
        args = args_button.pop('*', ())
        yield args, args_button, code

async def build_ui(ui_node: UiNode, interpreter: "DshellInterpreteur") -> EasyModifiedViews:
    """
    Builds a UI component from the UiNode.
    Can accept buttons and select menus.
    :param ui_node:
    :param interpreter:
    :return:
    """
    view = EasyModifiedViews()

    async for args, args_button, code in build_ui_parameters(ui_node, interpreter):
        b = Button(**args_button)
        view.add_items(b)
        view.set_callable(b.custom_id, _callable=ui_button_callback, data={'code': code, 'interpreter': interpreter})

    return view

async def rebuild_ui(ui_node : UiNode, view: EasyModifiedViews, interpreter: "DshellInterpreteur") -> EasyModifiedViews:
    """
    Rebuilds a UI component from an existing EasyModifiedViews.
    :param view:
    :param interpreter:
    :return:
    """
    async for args, args_button, code in build_ui_parameters(ui_node, interpreter):
        try:
            ui = view.get_ui(args_button['custom_id'])
        except CustomIDNotFound:
            raise ValueError(f"Button with custom_id '{args_button['custom_id']}' not found in the view !")

        ui.label = args_button.get('label', ui.label)
        ui.style = args_button.get('style', ui.style)
        ui.emoji = args_button.get('emoji', ui.emoji)
        ui.disabled = args_button.get('disabled', ui.disabled)
        ui.url = args_button.get('url', ui.url)
        ui.row = args_button.get('row', ui.row)
        new_code = code if code is not None else view.get_callable_data(args_button['custom_id'])['code']
        view.set_callable(args_button['custom_id'], _callable=ui_button_callback, data={'code': new_code, 'interpreter': interpreter})

    return view


async def ui_button_callback(button: Button, interaction: Interaction, data: dict[str, Any]):
    """
    Callback for UI buttons.
    Executes the code associated with the button.
    :param button:
    :param interaction:
    :param data:
    :return:
    """
    code = data.pop('code', None)
    interpreter: "DshellInterpreteur" = data.pop('interpreter', None)
    if code is not None:
        local_env = {
            '__ret__': None,
            '__guild__': interaction.guild.name if interaction.guild else None,
            '__channel__': interaction.channel.name if interaction.channel else None,
            '__author__': interaction.user.id,
            '__author_name__': interaction.user.name,
            '__author_display_name__': interaction.user.display_name,
            '__author_avatar__': interaction.user.display_avatar.url if interaction.user.display_avatar else None,
            '__author_discriminator__': interaction.user.discriminator,
            '__author_bot__': interaction.user.bot,
            '__author_nick__': interaction.user.nick if hasattr(interaction.user, 'nick') else None,
            '__author_id__': interaction.user.id,
            '__message__': interaction.message.content if hasattr(interaction.message, 'content') else None,
            '__message_id__': interaction.message.id if hasattr(interaction.message, 'id') else None,
            '__channel_name__': interaction.channel.name if interaction.channel else None,
            '__channel_type__': interaction.channel.type.name if hasattr(interaction.channel, 'type') else None,
            '__channel_id__': interaction.channel.id if interaction.channel else None,
            '__private_channel__': isinstance(interaction.channel, PrivateChannel),
        }
        local_env.update(data)
        from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur
        with new_scope(interpreter, local_env):
            await DshellInterpreteur(code, ctx=interaction, debug=False, vars_env=interpreter.env).execute()
    else:
        await interaction.response.defer(invisible=True)

    data.update({'code': code})