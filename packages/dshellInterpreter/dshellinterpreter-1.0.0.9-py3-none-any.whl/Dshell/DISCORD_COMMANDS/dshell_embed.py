from .._DshellTokenizer.dshell_token_type import Token

from .._DshellParser.ast_nodes import FieldEmbedNode

from .._DshellInterpreteur.utils_interpreter import regroupe_commandes

from Dshell.full_import import Embed

from Dshell.full_import import Any, TYPE_CHECKING

from .utils.utils_global import utils_build_colour

if TYPE_CHECKING:
    from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur

async def build_embed_args(body: list[Token], fields: list[FieldEmbedNode], interpreter: "DshellInterpreteur") -> tuple[dict, list[dict]]:
    """
    Builds the arguments for an embed from the command information.
    """
    regrouped_parameters = await regroupe_commandes(body, interpreter)
    args_main_embed: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()
    args_main_embed.pop('*')  # remove unspecified parameters for the embed
    args_main_embed: dict[str, Token]  # specify what it contains from now on

    args_fields: list[dict[str, Token]] = []
    for field in fields:  # do the same for the fields
        y = await regroupe_commandes(field.body, interpreter)
        args_field = y.get_dict_parameters()
        args_field.pop('*')
        args_field: dict[str, Token]
        args_fields.append(args_field)

    if 'color' in args_main_embed:
        args_main_embed['color'] = utils_build_colour(args_main_embed['color'])  # convert color to Colour object or int

    return args_main_embed, args_fields


async def build_embed(body: list[Token], fields: list[FieldEmbedNode], interpreter: "DshellInterpreteur") -> Embed:
    """
    Builds an embed from the command information.
    """

    args_main_embed, args_fields = await build_embed_args(body, fields, interpreter)
    embed = Embed(**args_main_embed)  # build the main embed
    for field in args_fields:
        embed.add_field(**field)  # add all fields

    return embed

async def rebuild_embed(embed: Embed, body: list[Token], fields: list[FieldEmbedNode], interpreter: "DshellInterpreteur") -> Embed:
    """
    Rebuilds an embed from an existing embed and the command information.
    """
    args_main_embed, args_fields = await build_embed_args(body, fields, interpreter)

    for key, value in args_main_embed.items():
        if key == 'color':
            embed.colour = value
        else:
            setattr(embed, key, value)

    if args_fields:
        embed.clear_fields()
        for field in args_fields:
            embed.add_field(**field)

    return embed