# Nova — Grammar

```ebnf
program = { declaration } ;

declaration =
    function_declaration
    | statement ;

function_declaration =
    "fn" identifier "(" parameters? ")" block ;

parameters =
    identifier { "," identifier } ;

statement =
    variable_declaration
    | return_statement
    | if_statement
    | while_statement
    | expression_statement ;

variable_declaration =
    "let" identifier [ "=" expression ] ";" ;

return_statement =
    "return" [ expression ] ";" ;

block =
    "{" { declaration } "}" ;

expression =
    assignment ;

assignment =
    logical_or
    | identifier "=" assignment ;

logical_or =
    logical_and { "||" logical_and } ;

logical_and =
    equality { "&&" equality } ;

equality =
    comparison { ("==" | "!=") comparison } ;

comparison =
    term { ("<" | "<=" | ">" | ">=") term } ;

term =
    factor { ("+" | "-") factor } ;

factor =
    unary { ("*" | "/" | "%") unary } ;

unary =
    ("!" | "-") unary
    | call ;

call =
    primary { "(" arguments? ")" } ;

primary =
    number
    | string
    | identifier
    | "true"
    | "false"
    | "nil"
    | "(" expression ")" ;
