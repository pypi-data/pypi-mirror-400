from .._DshellTokenizer.dshell_token_type import Token
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from .._DshellInterpreteur.errors import DshellInterpreterStopExecution
from Dshell.full_import import TypeVar, Union, Optional, Any, Callable, sleep, findall
from .._DshellParser.ast_nodes import *
from Dshell.full_import import AutoShardedBot, Interaction, Message, PrivateChannel, Embed
from Dshell.full_import import EasyModifiedViews
from .._DshellParser.dshell_parser import parse, print_ast
from .._DshellTokenizer.dshell_tokenizer import DshellTokenizer
from .cached_messages import dshell_cached_messages
from .._DshellTokenizer.dshell_keywords import dshell_commands
from .utils_interpreter import get_params, eval_expression, eval_expression_inline, regroupe_commandes
from ..DISCORD_COMMANDS.dshell_embed import build_embed, rebuild_embed
from ..DISCORD_COMMANDS.dshell_ui import build_ui, rebuild_ui
from ..DISCORD_COMMANDS.utils.utils_permissions import build_permission
from .dshell_scope import Scope, new_scope

from Dshell.full_import import Union



All_nodes = TypeVar('All_nodes', IfNode, LoopNode, ElseNode, ElifNode, ArgsCommandNode, VarNode)
context = TypeVar('context', AutoShardedBot, Message, PrivateChannel, Interaction)

class DshellInterpreteur:
    """
    Discord Dshell interpreter.
    Make what you want with Dshell code to interact with Discord !
    """

    def __init__(self, code: Union[str, CodeNode], ctx: context,
                 debug: bool = False,
                 vars: Optional[str] = None,
                 vars_env: Optional[dict[str, Any] | Scope] = None):
        """
        Interpreter Dshell code
        :param code: The code to interpret. Each line must end with a newline character, except SEPARATOR and SUB_SEPARATOR tokens.
        :param ctx: The context in which the code is executed. It can be a Discord bot, a message, or a channel.
        :param debug: If True, prints the AST of the code and put the ctx to None.
        :param vars: Optional dictionary of variables to initialize in the interpreter's environment.
        :param vars_env: Optional dictionary of additional environment variables to add to the interpreter's environment.

        Note: __message_before__ (message content before edit) can be overwritten by vars_env parameter.
        """
        if not isinstance(code, CodeNode):
            try:
                self.ast: list[ASTNode] = parse(DshellTokenizer(code).start(), StartNode([]))[0]
            except Exception as e:
                raise e
        else:
            self.ast: list[ASTNode] = code.body

        message = ctx.message if isinstance(ctx, Interaction) else ctx
        self.env: Scope = Scope()
        self.env.update({
            '__ret__': None,  # environment variables, '__ret__' is used to store the return value of commands

            '__author__': message.author.id,
            '__author_name__': message.author.name,
            '__author_display_name__': message.author.display_name,
            '__author_avatar__': message.author.display_avatar.url if message.author.display_avatar else None,
            '__author_discriminator__': message.author.discriminator,
            '__author_bot__': message.author.bot,
            '__author_nick__': message.author.nick if hasattr(message.author, 'nick') else None,
            '__author_id__': message.author.id,
            '__author_add_reaction__': None, # Can be overwritten by add vars_env parameter to get the author on message add event reaction
            '__author_remove_reaction__': None, # Can be overwritten by add vars_env parameter to get the author on message remove event reaction

            '__message__': message.content,
            '__message_content__': message.content,
            '__message_id__': message.id,
            '__message_author__': message.author.id,
            '__message_before__': message.content,  # same as __message__, but before edit. Can be overwritten by add vars_env parameter
            '__message_created_at__': str(message.created_at),
            '__message_edited_at__': str(message.edited_at),
            '__message_reactions__': ListNode([str(reaction.emoji) for reaction in message.reactions]),
            '__message_add_reaction__': None, # Can be overwritten by add vars_env parameter to get the reaction added on message add event reaction
            '__message_remove_reaction__': None, # Can be overwritten by add vars_env parameter to get the reaction removed on message remove event reaction
            '__message_url__': message.jump_url if hasattr(message, 'jump_url') else None,
            '__last_message__': message.channel.last_message_id,

            '__channel__': message.channel.id,
            '__channel_name__': message.channel.name,
            '__channel_type__': message.channel.type.name if hasattr(message.channel, 'type') else None,
            '__channel_id__': message.channel.id,
            '__private_channel__': isinstance(message.channel, PrivateChannel),

            '__guild__': message.channel.guild.id,
            '__guild_name__': message.channel.guild.name,
            '__guild_id__': message.channel.guild.id,
            '__guild_members__': ListNode([member.id for member in message.channel.guild.members]),
            '__guild_member_count__': message.channel.guild.member_count,
            '__guild_icon__': message.channel.guild.icon.url if message.channel.guild.icon else None,
            '__guild_owner_id__': message.channel.guild.owner_id,
            '__guild_description__': message.channel.guild.description,
            '__guild_roles__': ListNode([role.id for role in message.channel.guild.roles]),
            '__guild_roles_count__': len(message.channel.guild.roles),
            '__guild_emojis__': ListNode([emoji.id for emoji in message.channel.guild.emojis]),
            '__guild_emojis_count__': len(message.channel.guild.emojis),
            '__guild_channels__': ListNode([channel.id for channel in message.channel.guild.channels]),
            '__guild_text_channels__': ListNode([channel.id for channel in message.channel.guild.text_channels]),
            '__guild_voice_channels__': ListNode([channel.id for channel in message.channel.guild.voice_channels]),
            '__guild_categories__': ListNode([channel.id for channel in message.channel.guild.categories]),
            '__guild_stage_channels__': ListNode([channel.id for channel in message.channel.guild.stage_channels]),
            '__guild_forum_channels__': ListNode([channel.id for channel in message.channel.guild.forum_channels]),
            '__guild_channels_count__': len(message.channel.guild.channels),

        } if message is not None and not debug else {'__ret__': None}) # {} is used in debug mode, when ctx is None

        if isinstance(vars_env, Scope):
            self.env = vars_env
        elif vars_env is not None: # add the variables to the environment
            self.env.update(vars_env)

        self.vars = vars or ''
        self.ctx: context = ctx

        dshell_cached_messages.set(dict()) # save all messages view in the current scoop

        if debug:
            print_ast(self.ast)

    async def execute(self, ast: Optional[list[All_nodes]] = None):
        """
        Executes the abstract syntax tree (AST) generated from the Dshell code.

        This asynchronous method traverses and interprets each node in the AST, executing commands,
        handling control flow structures (such as if, elif, else, and loops), managing variables,
        and interacting with Discord through the provided context. It supports command execution,
        variable assignment, sleep operations, and permission handling, among other features.

        :param ast: Optional list of AST nodes to execute. If None, uses the interpreter's main AST.
        :raises RuntimeError: If an EndNode is encountered, indicating execution should be stopped.
        :raises Exception: If sleep duration is out of allowed bounds.
        """
        if ast is None:
            ast = self.ast

        for node in ast:

            if isinstance(node, StartNode):
                await self.execute(node.body)

            if isinstance(node, CommandNode):
                result = await call_function(dshell_commands[node.name], node.body, self)
                self.env.set(f'__{node.name}__', result) # return value of the command
                self.env.set('__ret__', result)  # global return variable for all commands

            elif isinstance(node, ParamNode):
                params = await get_params(node, self)
                self.env.update(params)  # update the environment

            elif isinstance(node, IfNode):
                elif_valid = False
                if await eval_expression(node.condition, self):
                    await self.execute(node.body)
                    continue
                elif node.elif_nodes:

                    for i in node.elif_nodes:
                        if await eval_expression(i.condition, self):
                            await self.execute(i.body)
                            elif_valid = True
                            break

                if not elif_valid and node.else_body is not None:
                    await self.execute(node.else_body.body)

            elif isinstance(node, LoopNode):
                self.env.set(node.variable.name.value, 0)
                for i in DshellIterator(await eval_expression(node.variable.body, self)):
                    with new_scope(self, {node.variable.name.value: i}):
                        await self.execute(node.body)

            elif isinstance(node, VarNode):

                first_node = node.body[0]
                if isinstance(first_node, IfNode):
                    self.env.set(node.name.value, await eval_expression_inline(first_node, self))

                elif isinstance(first_node, EmbedNode):
                    # rebuild the embed if it already exists
                    if self.env.contains(node.name.value) and isinstance(self.env.get(node.name.value), Embed):
                        self.env.set(node.name.value, await rebuild_embed(self.env.get(node.name.value), first_node.body, first_node.fields, self))
                    else:
                        self.env.set(node.name.value, await build_embed(first_node.body, first_node.fields, self))

                elif isinstance(first_node, PermissionNode):
                    # rebuild the permissions if it already exists
                    if self.env.contains(node.name.value) and isinstance(self.env.get(node.name.value), dict):
                        self.env.get(node.name.value).update(await build_permission(first_node.body, self))
                    else:
                        self.env.set(node.name.value, await build_permission(first_node.body, self))

                elif isinstance(first_node, UiNode):
                    # rebuild the UI if it already exists
                    if self.env.contains(node.name.value) and isinstance(self.env.get(node.name.value), EasyModifiedViews):
                        self.env.set(node.name.value, await rebuild_ui(first_node, self.env.get(node.name.value), self))
                    else:
                        self.env.set(node.name.value, await build_ui(first_node, self))

                elif isinstance(first_node, CodeNode):
                    if self.env.contains(node.name.value) and isinstance(self.env.get(node.name.value), first_node):
                        self.env.get(node.name.value).update(first_node)
                    else:
                        self.env.set(node.name.value, first_node)

                else:
                    self.env.set(node.name.value, await eval_expression(node.body, self))

            elif isinstance(node, SleepNode):
                sleep_time = await eval_expression(node.body, self)
                if sleep_time > 3600:
                    raise Exception(f"Sleep time is too long! ({sleep_time} seconds) - maximum is 3600 seconds)")
                elif sleep_time < 1:
                    raise Exception(f"Sleep time is too short! ({sleep_time} seconds) - minimum is 1 second)")

                await sleep(sleep_time)

            elif isinstance(node, EvalNode):

                self.env.set('__ret__', await eval_CodeNode(node, self))

            elif isinstance(node, ReturnNode):
                self.env.set('__ret__', await eval_expression(node.body, self))

            elif isinstance(node, EndNode):
                if await self.eval_data_token(node.error_message):
                    raise RuntimeError("Execution stopped - EndNode encountered")
                else:
                    raise DshellInterpreterStopExecution()

        self.env.clear()

    async def eval_data_token(self, token: Token):
        """
        Eval a data token and returns its value in Python.
        :param token: The token to evaluate.
        """

        if not hasattr(token, 'type'):
            return token

        if token.type in (DTT.INT, DTT.MENTION):
            return int(token.value)
        elif token.type == DTT.FLOAT:
            return float(token.value)
        elif token.type == DTT.BOOL:
            return token.value.lower() == "true"
        elif token.type == DTT.NONE:
            return None
        elif token.type == DTT.LIST:
            return ListNode(
                [await self.eval_data_token(tok) for tok in token.value])  # token.value contient déjà une liste de Token
        elif token.type == DTT.IDENT:
            try:
                return self.env.get(token.value)
            except KeyError:
                return token.value
        elif token.type == DTT.EVAL_GROUP:
            await self.execute(parse([token.value], StartNode([]))[0]) # obliger de parser car ce il n'est pas dejà un AST
            return self.env.get('__ret__')
        elif token.type == DTT.STR:
            temp = token.value
            for match in findall(rf"\$({'|'.join(self.env.keys())})", temp):
                temp = temp.replace('$' + match, str(self.env.get(match)))
            return temp
        else:
            return token.value  # fallback



async def call_function(function: Callable, args: ArgsCommandNode, interpreter: DshellInterpreteur):
    """
    Call the function with the given arguments.
    It can be an async function !
    :param function: The function to call.
    :param args: The arguments to pass to the function.
    :param interpreter: The Dshell interpreter instance.
    """
    reformatted = await regroupe_commandes(args.body, interpreter)

    args = reformatted.get_non_specified_parameters()  # remove non-specified parameters from dict parameters
    kwargs = reformatted.get_dict_parameters()
    kwargs.pop('*', None)

    args.insert(0, interpreter.ctx)  # add the context as first argument

    return await function(*args, **kwargs)

async def eval_CodeNode(eval_node: EvalNode, interpreter: DshellInterpreteur):
    """
    Eval a CodeNode and return its value.
    :param eval_node: The EvalNode with the code to evaluate.
    :param interpreter: The Dshell interpreter instance.
    """
    codeNode = await interpreter.eval_data_token(eval_node.codeNode)
    argscommand = await regroupe_commandes(eval_node.argsNode.body, interpreter)
    kwargs = argscommand.get_dict_parameters()
    kwargs.pop('*', None)

    result = None
    with new_scope(interpreter, kwargs):
        await interpreter.execute(codeNode.body)
        result = interpreter.env.get('__ret__')

    return result


class DshellIterator:
    """
    Used to transform anything into an iterable
    """

    def __init__(self, data):
        self.data = data if isinstance(data, (str, list, ListNode)) else range(int(data))
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.data):
            self.current = 0
            raise StopIteration

        value = self.data[self.current]
        self.current += 1
        return value


