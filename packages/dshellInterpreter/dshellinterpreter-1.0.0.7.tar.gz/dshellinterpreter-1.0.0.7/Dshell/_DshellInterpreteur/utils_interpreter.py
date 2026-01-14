from .dshell_arguments import DshellArguments
from .._DshellTokenizer.dshell_token_type import Token
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT

from .._DshellParser.ast_nodes import IfNode, ParamNode, ListNode

from .._DshellParser.dshell_parser import to_postfix

from Dshell.full_import import sub, escape
from Dshell.full_import import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur

async def regroupe_commandes(body: list[Token], interpreter: "DshellInterpreteur", normalise: bool = False) -> DshellArguments:
    """
    Groups the command arguments in the form of a python dictionary.
    Note that you can specify the parameter you wish to pass via -- followed by the parameter name. But this is not mandatory!
    Non-mandatory parameters will be stored in a list in the form of tokens with the key \`*\`.
    The others, having been specified via a separator, will be in the form of a list of tokens with the IDENT token as key, following the separator for each argument.
    If two parameters have the same name, the last one will overwrite the previous one.
    To accept duplicates, use the SUB_SEPARATOR (~~) to create a sub-dictionary for parameters with the same name (sub-dictionary is added to the list returned).

    :param body: The list of tokens to group.
    :param interpreter: The Dshell interpreter instance.
    :param normalise: If True, normalises the arguments (make value lowercase).
    """
    # tokens to return

    instance_dhsell_arguments = DshellArguments()
    index = 0
    n = len(body)

    while index < n:

        if normalise and hasattr(body[index], 'value') and isinstance(body[index].value, str):
                body[index].value = body[index].value.lower()

        # If the current token is the last one and is a parameter marker, add it with empty value
        if index == n - 1 and body[index].type in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):
            if body[index].type == DTT.PARAMETER:
                instance_dhsell_arguments.set_parameter(body[index].value, '', DTT.PARAMETER)
            elif body[index].type == DTT.STR_PARAMETER:
                instance_dhsell_arguments.set_parameter(body[index].value, '', DTT.STR_PARAMETER)
            else:  # DTT.PARAMETERS
                instance_dhsell_arguments.set_parameter(body[index].value, ListNode([]), DTT.PARAMETERS)
            index += 1
            continue

        if body[index].type == DTT.PARAMETER:

            value = ''
            current_index = index
            while (index + 1) < n and body[index + 1].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):

                value = await interpreter.eval_data_token(body[index + 1])
                index += 1
                break

            instance_dhsell_arguments.set_parameter(body[current_index].value, value, DTT.PARAMETER, obligatory=value == '*')
            index += 1

        elif body[index].type == DTT.STR_PARAMETER:

            final_argument = ''
            current_index = index

            while (index + 1) < n and body[index + 1].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):

                final_argument += body[index + 1].value + ' '
                index += 1
                instance_dhsell_arguments.set_parameter(body[current_index].value, final_argument, type_=DTT.STR_PARAMETER)

            index += 1

        elif body[index].type == DTT.PARAMETERS:

            list_parameters = []
            current_index = index
            while (index + 1) < n and body[index + 1].type not in (DTT.PARAMETER, DTT.STR_PARAMETER, DTT.PARAMETERS):

                list_parameters.append(await interpreter.eval_data_token(body[index + 1]))
                index += 1
                instance_dhsell_arguments.set_parameter(body[current_index].value, ListNode(list_parameters), type_=DTT.PARAMETERS)

            index += 1

        else:
            instance_dhsell_arguments.add_non_specified_parameters(await interpreter.eval_data_token(body[index]))
            index += 1

    return instance_dhsell_arguments

async def get_params(node: ParamNode, interpreter: "DshellInterpreteur") -> dict[str, Any]:
    """
    Get the parameters from a ParamNode.
    :param node: The ParamNode to get the parameters from.
    :param interpreter: The Dshell interpreter instance.
    :return: A dictionary of parameters.
    """
    def remplacer(match) -> str:
        spacial_char = match.group(1)
        if spacial_char:
            return ''
        return match.group(4)

    variables = interpreter.vars
    regrouped_parameters: DshellArguments = await regroupe_commandes(node.body, interpreter)

    from .._DshellTokenizer.dshell_tokenizer import DshellTokenizer
    _ = DshellTokenizer(variables).start()
    regrouped_variables = await regroupe_commandes(_[0] if _ else tuple(), interpreter)

    already_modified = set()
    variables_non_specified_parameters = regrouped_variables.parameters.pop('*', None).value  # remove non-specified parameters

    for param_name, param_data in regrouped_variables.parameters.items():
        regrouped_parameters.update_parameter(param_name, param_data)
        variables = sub(rf"--([*']?)({escape(param_name)})\s+(.*)\s*?(.*)$", remplacer, variables, count=1)
        already_modified.add(param_name)

    index_variable = 0
    for var in regrouped_parameters.parameters.keys():
        if var not in already_modified:

            parameter_type = regrouped_parameters.get_parameter(var).type

            if parameter_type == DTT.PARAMETER and index_variable < len(variables_non_specified_parameters):
                regrouped_parameters.set_parameter(var, variables_non_specified_parameters[index_variable], parameter_type)  # variables_post_regrouped[index_variable] n'est pas un token donc impossible de l'évaluer ! pose problème dans les commandes qui requière autre chose que des str
                index_variable += 1

            elif parameter_type == DTT.STR_PARAMETER:
                variables_post_regrouped: list[str] = variables.strip().split(' ') if variables else []  # set uniquement pour les paramètres full str
                str_parameters_set_for_variables = variables_post_regrouped[index_variable:]
                # la ligne dessous permet de set un paramètre full str avec plusieurs mots. Si les variables restantes sont vides, on met la valeur par défaut (obligé de passer la fonction str car sinon ça met un DshellArgumentsData)
                regrouped_parameters.set_parameter(var, ' '.join(str_parameters_set_for_variables if str_parameters_set_for_variables else [str(regrouped_parameters.parameters.get(var, ''))]), parameter_type)
                break

            elif parameter_type == DTT.PARAMETERS:
                regrouped_parameters.set_parameter(var, ListNode(variables_non_specified_parameters[index_variable:]), parameter_type)
                break

    for param_name, param_data in regrouped_parameters.parameters.items():
        if param_data.obligatory and param_data.value == '*':
            raise Exception(f"Parameter '{param_name}' is obligatory but not specified!")

    x = regrouped_parameters.get_dict_parameters()
    x.pop('*', None)
    return x


async def eval_expression_inline(if_node: IfNode, interpreter: "DshellInterpreteur") -> Token:
    """
    Eval a conditional expression inline.
    :param if_node: The IfNode to evaluate.
    :param interpreter: The Dshell interpreter instance.
    """
    if await eval_expression(if_node.condition, interpreter):
        return await eval_expression(if_node.body, interpreter)
    else:
        return await eval_expression(if_node.else_body.body, interpreter)


async def eval_expression(tokens: list[Token], interpreter: "DshellInterpreteur") -> Any:
    """
    Evaluates an arithmetic and logical expression.
    :param tokens: A list of tokens representing the expression.
    :param interpreter: The Dshell interpreter instance.
    """
    from .._DshellTokenizer.dshell_keywords import dshell_operators
    postfix = to_postfix(tokens, interpreter)
    stack = []

    for token in postfix:

        if token.type in {DTT.INT, DTT.FLOAT, DTT.BOOL, DTT.STR, DTT.LIST, DTT.IDENT, DTT.EVAL_GROUP}:
            stack.append(await interpreter.eval_data_token(token))

        elif token.type in (DTT.MATHS_OPERATOR, DTT.LOGIC_OPERATOR, DTT.LOGIC_WORD_OPERATOR):
            op = token.value

            if op == "not":
                a = stack.pop()
                result = dshell_operators[op][0](a)

            else:
                b = stack.pop()
                try:
                    a = stack.pop()
                except IndexError:
                    if op == "-":
                        a = 0
                    else:
                        raise SyntaxError(f"Invalid expression: {op} operator requires two operands, but only one was found.")

                result = dshell_operators[op][0](a, b)

            stack.append(result)

        else:
            raise SyntaxError(f"Unexpected token type: {token.type} - {token.value}")

    if len(stack) != 1:
        raise SyntaxError("Invalid expression: stack should contain exactly one element after evaluation.")

    return stack[0]